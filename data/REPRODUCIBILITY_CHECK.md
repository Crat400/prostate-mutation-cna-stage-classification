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

The reproducibility comparison verifies output equivalence for the provided archive, not biological correctness or prospective prediction validity. The standalone QC validation log is in `QC_validation_console.txt`.
