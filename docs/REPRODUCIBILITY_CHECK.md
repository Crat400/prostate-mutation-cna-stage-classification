# Python reproduction check

The Python preprocessing and master-file scripts were executed against the supplied `prostate_msk_2024.tar.gz` archive.

| Output | Python result | Comparison with R output |
|---|---|---|
| `clinical_all_samples.csv` | 2,260 × 16 | Values matched |
| `clinical_manifest.csv` | 1,967 × 16 | Values matched |
| `mutations_long.csv` | 9,651 × 15 | All mutation rows matched (order-independent) |
| `cna_long.csv` | 1,064,147 × 4 | Values matched |
| `gene_panel_matrix.csv` | 1,967 × 5 | Values matched |
| `EXSU500_MSK_master_descriptive.csv` | 1,967 × 1,041 | Values matched |
| `EXSU500_MSK_master_compact.csv` | 1,967 × 44 | Numeric values matched; `0` vs `0.0` string formatting in two CNA columns |

The reproducibility comparison verifies output equivalence for the provided archive, not biological correctness or prospective prediction validity. For updated QC, run `python scripts/validate_msk_data.py --input-dir data/processed`; the console output is generated rather than tracked.

## End-to-end reproduction from a fresh GitHub clone

**Date:** November 24, 2026. **Platform:** Windows PowerShell, new Conda Python 3.12 environment (`exsu500-professor-test`). This test was performed by a team member, following the grader workflow, without using the original local dataset or fitted models. See [INSTRUCTIONS.md](INSTRUCTIONS.md).

| Stage | Observed result |
|---|---|
| Fresh clone and dependency installation | Completed |
| Public panel downloads | Four JSON files present |
| Public study archive | Downloaded and readable |
| Data preparation and validation | Reported cohort and genomic counts matched original analysis |
| Notebook 01 | Executed successfully using nbconvert |
| Notebook 02 | All four required split/feature CSVs present |
| Notebook 03 | All six fitted model files present |
| Notebook 04 | Final held-out comparison table generated |

The rerun reproduced 1,967 eligible patients (943 Stage I–III and 1,024 Stage IV), 9,651 mutation rows and 1,064,147 CNA entries. No CNA calls were missing; 174 entries retained the non-standard -1.5 value. The reported data summary matched the original counts; the individual 12 PASS lines were not included in the shared reproduction transcript.

### Reproduced test metrics

| Features | Model | AUROC | AP | Trapezoidal AUPRC |
|---|---|---:|---:|---:|
| Mutation | Logistic regression | 0.617135 | 0.643574 | 0.641952 |
| Mutation | Random forest | 0.647819 | 0.659436 | 0.659618 |
| CNA | Logistic regression | 0.512827 | 0.533713 | 0.557924 |
| CNA | Random forest | 0.552497 | 0.585910 | 0.615111 |
| Combined | Logistic regression | 0.594499 | 0.633443 | 0.631602 |
| Combined | Random forest | **0.660257** | **0.663716** | **0.663581** |
| None | Majority class | 0.500000 | 0.520270 | 0.760135 |

All three displayed metrics match the original exported evaluation values at the reported precision. The majority-class trapezoidal AUPRC is inflated by interpolation of its constant-score PR curve; AP is the more interpretable baseline comparison. The validation-selected primary model remains Combined Random Forest. No additional tuning or model selection was performed on the test set.

The package snapshot was captured using `python -m pip freeze` from the successful environment and is recorded in `requirements.txt`. This confirms successful reproduction on the tested Windows environment, not external clinical validation or portability to every operating system. Installation from the newly pinned requirements file has not yet been independently retested. Confidence intervals, calibration, and figure files were not separately compared in the shared reproduction transcript.
