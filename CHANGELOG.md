# Changelog

Benchmark versions look like `vMAJOR.MINOR`. A new version starts whenever numbers stop being comparable: new items, a
label fix, a scorer change or a split change. Each version keeps its own `splits/` file and `results/` directory.
Package releases follow semver.

## Unreleased

- d1-2B (Liquid AI, open weights) joins the text board through `extract-bench open` as `d1_2b`: one `system_one`
  read question per field, one forward pass per document, bf16 on one RTX 3090, model code pinned to revision
  `10e7671d`. The runner keeps every read's span and the import answers at calibrated `found` >= 0.5, d1's own cut
  (d1 itself also dropped spans whose raw `found` was under 0.5; 391 fields recovered). d1 has no list read, so each
  list field gets one value. Its questions carry Clairic's unit hints (money: the field's unit, else "currency";
  number: its unit). The other systems' scores don't change.
- d1-2B with the page image joins the image board as `d1_2b_img`, with `clairic_vision_ocr`'s input: the item's original
  page files (at most 4, Clairic's size checks) plus the same text and questions, at d1's trained 1.6 MP picture cap.
  63.2 against Sage 2's 69.1 and Clairic + image's 75.7; lifting the cap to 16.7 MP scored 62.9.
- `scripts/flag_garbled_ocr.py` writes `results/v0.1/garbled_ocr.json`: fields whose printed answer the OCR text holds
  only misread (215 fields, 118 in the eval half). `extract-bench report --exclude-garbled-ocr` drops them for every
  system and writes `board.no_garbled_ocr.*`; the text-board order and gaps don't change. The script needs the new
  `analysis` extra (rapidfuzz).
- `score._cents` no longer raises `InvalidOperation` on money values beyond 28 significant digits (a multi-line span
  whose digit runs parse as one number); such a value now scores 0.

## v0.1 (package 0.1.0), 2026-11-01

This is the first release prepared for publication.

- It has 12 datasets with cards and deterministic builders, and the v0.1 split of 1,844 items in eval and fit halves.
- It has results for five systems that read text (Sage 2 rc9 fast, Clairic, NuExtract3, Schematron-3B and GLiNER2.5)
  and one that also reads the page image (Clairic with the image).
- The `extract-bench` CLI has the commands `datasets`, `run` (`ocr`, `read`, `score`, `export`), `report`, `validate`
  and `open` (`export` and `import` for GPU models). Runs are mock runs by default. A live call needs `EXB_LIVE=1` and
  a spend cap, and every call goes to a local ledger.
- `extract-bench validate` checks the submission format. Scripts in `scripts/` draw the README figures and the
  raw-output examples.

Before v0.1 we ran these internal reads, and this release folds them in:

- 2026-10-29: we added open-weight extraction models (NuExtract3, Schematron-3B, GLiNER2.5), run with vLLM 0.32 in
  bf16 at temperature 0 on one A40. Output that doesn't parse scores 0 on every field.
- 2026-10-28: Levanto read every item with Sage 2 rc9, fast tier, and fitted its abstention thresholds on the `fit`
  half. This read introduced the single-request item filter.
- 2026-10-26: we fixed the scorer for every system, and comments in `score.py` name each fix. The scorer now folds
  Unicode dashes and quotes, ignores a leading article and keeps digit runs apart when comparing text, compares money in
  cents rounded half up, leaves unparseable gold dates unscored, scores TAT-QA spans by token F1, and merges list
  answers across windows by their spans.
- 2026-10-23: we built and audited the datasets and made the first live reads of Clairic with text, with the image,
  and with both.
