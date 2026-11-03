"""Flag fields whose answer the OCR text holds only in a clearly garbled form.

A field is flagged when ALL hold:
  1. its dataset's text is OCR (native-text datasets are never flagged);
  2. it has a gold value (a "not in the document" field is never flagged), the scorer can parse that gold, and
     the gold is not a pick from fixed options (RealDoc's checkbox states are not printed text);
  3. no span of the text the systems read is scored correct by the scorer (`score.exact_norm`, which already ignores
     case, spacing, punctuation, date and money formats), and the gold's alphanumerics don't occur in the text;
  4. a span a few OCR misreads away IS scored correct:
     - text: the gold's alphanumerics (case-folded) align to a stretch of the text's alphanumerics with at most
       max(1, 20%) character edits, all of them misreads: a digit only swaps with its look-alike letter (0/O, 1/l/I,
       5/S, 8/B/S, ...), never with another digit (as likely a different value printed on the page); no digit is
       added or dropped; no 2+ consecutive characters are added or dropped and no edits touch 3+ consecutive
       characters (a whole word added, missing or different is a reworded gold, not a misread); no two adjacent
       characters are swapped (a typing slip in the gold); the gold's first and last characters are present (a
       missing end is a different span boundary); the match covers whole OCR words (HTML tags aside), so it never
       borrows a letter from the next word;
     - number / money / date / time / datetime: fixing at most 2 OCR confusions (letter read as a digit inside a
       digit-bearing token, digit read as a letter inside a word, a dropped decimal point) makes the scorer accept
       the span. A digit replaced by another digit never counts.
  A list field is flagged when one of its gold items is garbled and none is missing outright.

Fields that are simply not in the text (OCR dropped them, or the gold is computed or reworded) are NOT flagged.

  python scripts/flag_garbled_ocr.py            # -> results/v0.1/garbled_ocr.json
Needs rapidfuzz (`pip install -e ".[analysis]"`). Checked by eye against the page images on a fit-half sample while
the rules were set, then on 44 eval-half flags: 41 real misreads, 1 gold typo, 2 not found on the page.
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

from rapidfuzz.distance import OSA, Levenshtein

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from extract_bench import score as S  # noqa: E402
from extract_bench.common import dataset_dir, load_items, load_split  # noqa: E402
from extract_bench.run import item_text  # noqa: E402

OCR_SETS = ["fatura", "omniai", "docvqa", "vrdu", "realdoc", "kleister_charity", "sroie", "cord"]
OUT = ROOT / "results" / "v0.1" / "garbled_ocr.json"
MAX_FIX = 2
L2D = {"O": "0", "o": "0", "D": "0", "Q": "0", "@": "0", "l": "1", "I": "1", "i": "1", "|": "1", "!": "1", "]": "1",
       "S": "5", "s": "5", "B": "8", "Z": "2", "z": "2", "G": "6", "g": "9", "q": "9"}
D2L = {"0": "o", "1": "l", "5": "s", "8": "b"}
TYPED = ("number", "money", "date", "time", "datetime")
SPAN_TOKENS = {"number": 3, "money": 3, "date": 5, "time": 3, "datetime": 6}


def usq(s) -> str:
    return S._usquash(S.norm_text(s))


CONFUSABLE = {"0": "od@q", "1": "lit|!]", "2": "z", "4": "a", "5": "s", "6": "gb", "7": "t", "8": "bs", "9": "gq"}


def _look_alike(x: str, y: str) -> bool:
    d, c = (x, y) if x.isdigit() else (y, x)
    return c in CONFUSABLE.get(d, "")


def misread_only(a: str, b: str) -> bool:
    """Edits turning text `a` into gold `b` are misreads: a digit only ever swaps with its look-alike letter (never
    another digit, never an arbitrary letter), no digit is added or dropped, no 2+ consecutive characters are added
    or dropped, no two adjacent characters are swapped (a transposition is a typing slip in the gold), and the gold's
    first and last characters are not missing (that is a span boundary). Edits touch at most 2 consecutive gold
    characters (a misread is local: rn -> m, l -> I; a run of 3+ is a different word)."""
    if OSA.distance(a, b) < Levenshtein.distance(a, b):
        return False
    ops = Levenshtein.editops(a, b)
    hit = sorted({j for _, _, j in ops})               # gold positions an edit touches
    if any(hit[k + 2] - hit[k] == 2 for k in range(len(hit) - 2)):
        return False                                   # 3+ consecutive edited characters: a different word
    run_kind, run_end, run_len = None, -9, 0
    for op, i, j in ops:
        x = a[i] if op != "insert" and i < len(a) else ""
        y = b[j] if op != "delete" and j < len(b) else ""
        if op == "replace":
            if (x.isdigit() or y.isdigit()) and not _look_alike(x, y):
                return False
        if op in ("insert", "delete"):
            if (x or y).isdigit() or (op == "insert" and j in (0, len(b) - 1)):
                return False                         # gold's first/last char missing: a span boundary, not a misread
            pos = i if op == "delete" else j
            run_len = run_len + 1 if (op == run_kind and pos == run_end + 1) else 1
            run_kind, run_end = op, pos
            if run_len >= 2:
                return False
    return True


class Doc:
    def __init__(self, text: str):
        self.text = text
        masked = re.sub(r"<[^<>\n]{1,40}>", lambda m: " " * len(m.group()), text)   # HTML tags (OmniAI) aren't words
        self.toks = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", masked)]
        self.sq = [usq(t) for t, _, _ in self.toks]
        self.all_sq = "".join(self.sq)
        self.tok_of = [k for k, s in enumerate(self.sq) for _ in s]   # squashed char -> token index
        ends = [0]
        for s in self.sq:
            ends.append(ends[-1] + len(s))
        self.bounds = set(ends)                       # squashed offsets where an OCR token starts or ends

    def span(self, a: int, b: int) -> tuple[str, int, int]:
        return self.text[self.toks[a][1]:self.toks[b - 1][2]], self.toks[a][1], self.toks[b - 1][2]


def text_status(doc: Doc, gold: str):
    """'clean' | ('garbled', span) | 'absent' for one acceptable text gold."""
    g = usq(gold)
    if not g or g in doc.all_sq:
        return "clean"
    if len(g) < 4:
        return "absent"
    cut = max(1, round(0.2 * len(g)))
    q = 3 if len(g) < 8 else 4                       # seed: a garbled copy keeps some exact q-gram
    starts = set()
    for o in range(len(g) - q + 1):
        p = doc.all_sq.find(g[o:o + q])
        while p >= 0:
            starts.add(p - o)
            p = doc.all_sq.find(g[o:o + q], p + 1)
    best = None
    for s0 in starts:
        for s in range(max(0, s0 - cut), s0 + cut + 1):
            if s not in doc.bounds:
                continue
            for n in range(len(g) - cut, len(g) + cut + 1):
                if s + n not in doc.bounds:              # whole OCR tokens only: never borrow a neighbour's letter
                    continue
                w = doc.all_sq[s:s + n]
                if len(w) < n:
                    continue
                d = Levenshtein.distance(w, g, score_cutoff=cut)
                if d <= cut and (best is None or d < best[0]) and misread_only(w, g):
                    best = (d, s, n)
    if best is None:
        return "absent"
    _, s, n = best
    return ("garbled", doc.span(doc.tok_of[s], doc.tok_of[s + n - 1] + 1))


def fixes(span: str):
    """Variants of `span` with up to MAX_FIX OCR-confusion fixes: (variant, n_fixes)."""
    out = []
    toks = re.split(r"(\s+)", span)
    edited, n = [], 0
    for t in toks:
        if re.search(r"\d", t):                       # digit-bearing token: letters read as digits
            nt = "".join(L2D.get(c, c) for c in t)
        elif re.fullmatch(r"[A-Za-z0-9]+", t or "_") and re.search(r"[A-Za-z]", t):
            nt = "".join(D2L.get(c, c) for c in t)    # word: digits read as letters (0ct, Ju1y)
        else:
            nt = t
        n += sum(a != b for a, b in zip(t, nt)); edited.append(nt)
    v = "".join(edited)
    if 0 < n <= MAX_FIX:
        out.append((v, n))
    for base, k in [(span, 0), (v, n)] if n <= MAX_FIX else [(span, 0)]:   # a dropped decimal point
        m = re.fullmatch(r"(\D*)(\d{3,})(\D*)", base)
        if m and k + 1 <= MAX_FIX:
            out.append((f"{m.group(1)}{m.group(2)[:-2]}.{m.group(2)[-2:]}{m.group(3)}", k + 1))
    return out


def typed_status(doc: Doc, f: dict, gold):
    ftype = f["type"]
    for k in range(len(doc.toks)):                   # fast path: any span already correct
        for L in range(1, SPAN_TOKENS[ftype] + 1):
            if k + L > len(doc.toks):
                break
            s, _, _ = doc.span(k, k + L)
            if len(re.findall(r"\d", s)) and S.exact_norm(s, gold, ftype, f) >= 1:
                return "clean"
    for k in range(len(doc.toks)):
        for L in range(1, SPAN_TOKENS[ftype] + 1):
            if k + L > len(doc.toks):
                break
            s, a, b = doc.span(k, k + L)
            if len(re.findall(r"\d", s)) < 2:        # a number must really be there, not conjured from letters
                continue
            for v, n in fixes(s):
                if S.exact_norm(v, gold, ftype, f) >= 1:
                    return ("garbled", (s, a, b), v)
    return "absent"


def field_status(doc: Doc, f: dict):
    """-> ('clean'|'absent', None) or ('garbled', detail)."""
    golds = f["gold"] if f["type"] == "list" else S._golds(f["gold"])
    ftype = (f.get("items") or "text") if f["type"] == "list" else f["type"]
    if ftype in ("duration",) or f.get("enum_options") or f.get("enum_state"):
        return "skip", None                          # a pick from fixed options (checkbox state) isn't printed text
    res = []
    for g in golds:
        if g is None:
            continue
        sub = {**f, "type": ftype}
        r = typed_status(doc, sub, g) if ftype in TYPED else text_status(doc, str(g))
        res.append((g, r))
    if f["type"] == "list":
        if any(r == "absent" for _, r in res) or not any(isinstance(r, tuple) for _, r in res):
            return ("absent" if any(r == "absent" for _, r in res) else "clean"), None
    elif any(r == "clean" for _, r in res) or not any(isinstance(r, tuple) for _, r in res):
        return ("clean" if any(r == "clean" for _, r in res) else "absent"), None
    g, r = next((g, r) for g, r in res if isinstance(r, tuple))
    (text, a, b) = r[1]
    return "garbled", {"gold": g, "ocr": text, "start": a, "end": b, **({"fixed": r[2]} if len(r) > 2 else {})}


def main():
    split = load_split("v0.1")
    out = {"version": "v0.1", "rule": __doc__.split("\n\n")[1].strip(), "datasets": {}}
    for ds in OCR_SETS:
        ids = set(split[ds]["eval"]) | set(split[ds]["fit"])
        dsd = dataset_dir(ds); df = S.DAYFIRST_DEFAULT.get(ds)
        flags, counts = {}, {"clean": 0, "garbled": 0, "absent": 0, "skip": 0}
        for it in load_items(ds):
            if it["id"] not in ids:
                continue
            text, src = item_text(it, dsd)
            if not text or src == "native":
                continue
            doc = Doc(text)
            for f in it["fields"]:
                if f["gold"] is None or (f["type"] == "list" and not f["gold"]) or S.gold_unparseable(f):
                    continue
                if df is not None and "dayfirst" not in f and f["type"] in ("date", "datetime"):
                    f = {**f, "dayfirst": df}
                st, det = field_status(doc, f)
                counts[st] += 1
                if st == "garbled":
                    flags.setdefault(it["id"], {})[f["name"]] = det
        out["datasets"][ds] = {"counts": counts, "flags": flags}
        print(ds, counts, flush=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print("->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
