# Input data and generated outputs

**No patient-level data, genomic matrices, model binaries, predictions, or raw archives are committed to GitHub.** The `.gitignore` excludes `data/raw/` and `data/processed/`.

1. Download the original MSK 2024 study archive (`prostate_msk_2024.tar.gz`) from the [cBioPortal study](https://www.cbioportal.org/study/summary?id=prostate_msk_2024). Put it at `data/raw/prostate_msk_2024.tar.gz`.
2. Open the four public cBioPortal API endpoints and save their full JSON responses as follows:

| Filename under `data/raw/panels/` | Source |
|:--|:--|
| `IMPACT341.json` | `https://www.cbioportal.org/api/gene-panels/IMPACT341` |
| `IMPACT410.json` | `https://www.cbioportal.org/api/gene-panels/IMPACT410` |
| `IMPACT468.json` | `https://www.cbioportal.org/api/gene-panels/IMPACT468` |
| `IMPACT505.json` | `https://www.cbioportal.org/api/gene-panels/IMPACT505` |

The response's `genes` array contains `hugoGeneSymbol` fields. The downloaded `IMPACT468` definition contains 469 gene objects; **use the definition itself**, not the numerical suffix, to identify coverage.

3. From the repository root, run:

```powershell
python scripts/prepare_msk_data.py --archive data/raw/prostate_msk_2024.tar.gz --output-dir data/processed
python scripts/build_msk_masters.py --input-dir data/processed
python scripts/validate_msk_data.py --input-dir data/processed
```

Then run notebooks `01`–`04` in order. The notebooks generate patient split assignments, feature matrices, trained model files and test-set outputs inside `data/processed/`.

**Caution:** The highest registry stage is not necessarily the stage at specimen collection. Dataset access, identifier agreement and missing-value checks do not establish biological label validity. Data are for educational research only.
