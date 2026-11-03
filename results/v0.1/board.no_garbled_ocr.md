# Extract Bench v0.1 board (eval split, garbled OCR excluded)

`extract-bench report` generates this file. Each cell is field accuracy in percent under rule (a), on headline fields. A ✱ means the 95% bootstrap interval of the difference from the reference excludes 0. The means leave out the receipt sets. Fields whose answer the OCR text holds only misread (results/v0.1/garbled_ocr.json) are dropped for every system.

## headline

| Dataset | Items | Fields | Sage 2 | Clairic | Δ vs Sage 2 [95% CI] |
|---|---:|---:|---:|---:|---|
| fatura | 62 | 606 | **91.6** | 88.4 | Clairic -3.1 [-5.1, -1.3] ✱ |
| omniai | 95 | 1,524 | **74.1** | 70.9 | Clairic -3.3 [-6.1, -0.4] ✱ |
| docvqa | 139 | 139 | 73.6 | **75.4** | Clairic +1.8 [-4.5, +8.1] |
| vrdu | 131 | 971 | **67.1** | 60.0 | Clairic -7.1 [-10.3, -3.7] ✱ |
| realdoc | 70 | 216 | **41.7** | 40.3 | Clairic -1.4 [-8.6, +5.4] |
| kleister_nda | 31 | 93 | **94.6** | **94.6** | Clairic +0.0 [-5.4, +5.4] |
| kleister_charity | 44 | 344 | 84.3 | **86.9** | Clairic +2.6 [-0.3, +5.8] |
| emails | 45 | 45 | **80.0** | 66.7 | Clairic -13.3 [-33.3, +6.7] |
| tatqa | 24 | 24 | **83.5** | 79.4 | Clairic -4.1 [-19.4, +11.2] |
| squad2 | 57 | 57 | 92.1 | **94.7** | Clairic +2.7 [-3.1, +9.2] |
| sroie (receipts) | 143 | 516 | 65.7 | **67.1** | Clairic +1.4 [-1.2, +3.8] |
| cord (receipts) | 79 | 940 | **53.2** | 51.1 | Clairic -2.0 [-4.5, +0.7] |
| **Mean of 10 sets** | | | **78.3** | **75.7** | Clairic -2.5 [-5.4, +0.4] |
| "Not in the document" correct (7 sets) | | | 72.2 | 59.0 | |

## text

| Dataset | Items | Fields | Sage 2 | Clairic | NuExtract3 | Schematron-3B | GLiNER2.5 | d1-2B | Δ vs Sage 2 [95% CI] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fatura | 62 | 606 | **91.6** | 88.4 | 89.8 | 85.8 | 68.6 | 85.3 | Clairic -3.1 [-5.1, -1.3] ✱; NuExtract3 -1.8 [-3.3, -0.3] ✱; Schematron-3B -5.8 [-7.7, -4.1] ✱; GLiNER2.5 -22.9 [-26.1, -19.9] ✱; d1-2B -6.3 [-8.3, -4.3] ✱ |
| omniai | 95 | 1,524 | 74.1 | 70.9 | **84.7** | 55.6 | 39.5 | 50.7 | Clairic -3.3 [-6.1, -0.4] ✱; NuExtract3 +10.6 [+5.8, +14.6] ✱; Schematron-3B -18.6 [-23.4, -13.7] ✱; GLiNER2.5 -34.6 [-38.5, -30.8] ✱; d1-2B -23.5 [-26.9, -19.7] ✱ |
| docvqa | 139 | 139 | 73.6 | **75.4** | 71.8 | 49.6 | 11.3 | 61.7 | Clairic +1.8 [-4.5, +8.1]; NuExtract3 -1.8 [-8.6, +4.6]; Schematron-3B -24.0 [-32.1, -15.7] ✱; GLiNER2.5 -62.3 [-69.9, -54.1] ✱; d1-2B -11.9 [-18.7, -5.9] ✱ |
| vrdu | 131 | 971 | 67.1 | 60.0 | **68.7** | 56.2 | 34.1 | 58.4 | Clairic -7.1 [-10.3, -3.7] ✱; NuExtract3 +1.6 [-2.3, +5.6]; Schematron-3B -10.9 [-15.8, -5.8] ✱; GLiNER2.5 -32.9 [-37.4, -28.7] ✱; d1-2B -8.7 [-11.6, -5.7] ✱ |
| realdoc | 70 | 216 | 41.7 | 40.3 | **54.6** | 32.9 | 18.5 | 22.7 | Clairic -1.4 [-8.6, +5.4]; NuExtract3 +13.0 [+4.0, +21.8] ✱; Schematron-3B -8.8 [-18.7, +0.5]; GLiNER2.5 -23.1 [-31.4, -14.5] ✱; d1-2B -19.0 [-27.3, -10.3] ✱ |
| kleister_nda | 31 | 93 | **94.6** | **94.6** | 81.7 | 80.6 | 45.2 | 77.4 | Clairic +0.0 [-5.4, +5.4]; NuExtract3 -12.9 [-21.5, -5.4] ✱; Schematron-3B -14.0 [-21.5, -7.5] ✱; GLiNER2.5 -49.5 [-58.1, -40.9] ✱; d1-2B -17.2 [-28.0, -7.5] ✱ |
| kleister_charity | 44 | 344 | 84.3 | **86.9** | 77.9 | 65.4 | 39.2 | 68.6 | Clairic +2.6 [-0.3, +5.8]; NuExtract3 -6.4 [-9.6, -3.2] ✱; Schematron-3B -18.9 [-23.7, -14.2] ✱; GLiNER2.5 -45.1 [-50.0, -40.4] ✱; d1-2B -15.7 [-20.1, -11.3] ✱ |
| emails | 45 | 45 | 80.0 | 66.7 | 88.9 | **95.6** | 46.7 | 57.8 | Clairic -13.3 [-33.3, +6.7]; NuExtract3 +8.9 [-6.7, +24.4]; Schematron-3B +15.6 [+4.4, +28.9] ✱; GLiNER2.5 -33.3 [-53.3, -13.3] ✱; d1-2B -22.2 [-42.2, -2.2] ✱ |
| tatqa | 24 | 24 | 83.5 | 79.4 | **88.5** | 38.3 | 3.6 | 68.1 | Clairic -4.1 [-19.4, +11.2]; NuExtract3 +5.0 [-0.3, +11.5]; Schematron-3B -45.2 [-66.7, -23.7] ✱; GLiNER2.5 -79.9 [-93.8, -64.7] ✱; d1-2B -15.4 [-31.9, -0.6] ✱ |
| squad2 | 57 | 57 | 92.1 | **94.7** | 59.0 | 41.1 | 52.6 | 87.1 | Clairic +2.7 [-3.1, +9.2]; NuExtract3 -33.1 [-45.8, -19.4] ✱; Schematron-3B -50.9 [-62.8, -37.5] ✱; GLiNER2.5 -39.4 [-53.3, -24.8] ✱; d1-2B -4.9 [-14.2, +4.3] |
| sroie (receipts) | 143 | 516 | 65.7 | 67.1 | **68.0** | 61.0 | 32.8 | 60.5 | Clairic +1.4 [-1.2, +3.8]; NuExtract3 +2.3 [-0.2, +4.9]; Schematron-3B -4.7 [-7.8, -1.2] ✱; GLiNER2.5 -32.9 [-36.8, -28.8] ✱; d1-2B -5.2 [-8.2, -2.3] ✱ |
| cord (receipts) | 79 | 940 | 53.2 | 51.1 | **54.1** | 48.6 | 44.2 | 46.2 | Clairic -2.0 [-4.5, +0.7]; NuExtract3 +0.9 [-1.5, +3.3]; Schematron-3B -4.6 [-7.4, -1.8] ✱; GLiNER2.5 -9.0 [-11.8, -6.2] ✱; d1-2B -7.0 [-9.9, -4.2] ✱ |
| **Mean of 10 sets** | | | **78.3** | **75.7** | **76.6** | **60.1** | **35.9** | **63.8** | Clairic -2.5 [-5.4, +0.4]; NuExtract3 -1.7 [-4.3, +0.9]; Schematron-3B -18.1 [-21.4, -15.0] ✱; GLiNER2.5 -42.3 [-45.5, -38.9] ✱; d1-2B -14.5 [-17.7, -11.3] ✱ |
| "Not in the document" correct (7 sets) | | | 72.2 | 59.0 | 57.0 | 54.3 | 44.1 | 63.6 | |

## image

| Dataset | Items | Fields | Sage 2 | Clairic + image | d1-2B + image | Δ vs Sage 2 [95% CI] |
|---|---:|---:|---:|---:|---:|---|
| fatura | 62 | 606 | 91.6 | **93.6** | 92.1 | Clairic + image +2.0 [-0.7, +4.6]; d1-2B + image +0.5 [-1.3, +2.3] |
| omniai | 95 | 1,524 | **74.1** | 73.4 | 59.2 | Clairic + image -0.8 [-3.6, +2.0]; d1-2B + image -15.0 [-18.3, -11.4] ✱ |
| docvqa | 139 | 139 | 73.6 | **88.3** | 82.2 | Clairic + image +14.7 [+9.1, +21.0] ✱; d1-2B + image +8.6 [+2.7, +14.8] ✱ |
| vrdu | 131 | 971 | **67.1** | 63.4 | 59.1 | Clairic + image -3.6 [-7.5, +0.1]; d1-2B + image -8.0 [-11.0, -4.8] ✱ |
| realdoc | 70 | 216 | 41.7 | **63.0** | 26.9 | Clairic + image +21.3 [+12.4, +30.6] ✱; d1-2B + image -14.8 [-22.9, -5.7] ✱ |
| sroie (receipts) | 143 | 516 | 65.7 | **75.8** | 62.2 | Clairic + image +10.1 [+6.2, +13.9] ✱; d1-2B + image -3.5 [-6.4, -0.6] ✱ |
| cord (receipts) | 79 | 940 | 53.2 | **82.8** | 51.9 | Clairic + image +29.6 [+25.7, +33.5] ✱; d1-2B + image -1.3 [-3.6, +1.1] |
| **Mean of 5 sets** | | | **69.6** | **76.3** | **63.9** | Clairic + image +6.7 [+4.3, +9.3] ✱; d1-2B + image -5.7 [-8.2, -3.3] ✱ |
| "Not in the document" correct (4 sets) | | | 70.9 | 52.4 | 57.2 | |

