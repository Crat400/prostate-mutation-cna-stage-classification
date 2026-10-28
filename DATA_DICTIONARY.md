# EXSU 500 — Compact MSK master data dictionary

One row per selected patient/sample. Source: `clinical_manifest.csv`, `mutations_long.csv`, `cna_long.csv`, and `gene_panel_matrix.csv`.

| Column | Definition | Interpretation / caution |
|---|---|---|
| `PATIENT_ID` | Unique patient identifier | Identifier; not a predictor |
| `SAMPLE_ID` | Selected tumor sample identifier | Identifier; not a predictor |
| `STAGE_RAW` | Highest recorded stage: Stage 1-3 or Stage 4 | Outcome source; not a predictor |
| `stage_binary` | 0 = Stage I–III; 1 = Stage IV | Target outcome, not predictor |
| `CANCER_TYPE_DETAILED` | Detailed histology subtype | Small non-adenocarcinoma groups |
| `SAMPLE_TYPE` | Primary, metastasis, local recurrence, or unknown | May reflect sampling decisions; assess confounding |
| `GENE_PANEL` | MSK-IMPACT panel used | Potential technical confounder |
| `SAMPLE_COVERAGE` | Reported sequencing coverage | Numeric technical metric |
| `TUMOR_PURITY` | Estimated tumor purity | May be missing |
| `MSI_SCORE` | Reported microsatellite instability score | May be missing |
| `MSI_TYPE` | Reported MSI category | May be missing |
| `SOMATIC_STATUS` | Matched vs unmatched sequencing status | Technical descriptor |
| `TMB_NONSYNONYMOUS` | Reported nonsynonymous tumor mutation burden | Potential panel-related differences |
| `N_SAMPLES_PER_PATIENT` | Number of tumor samples for the patient in the raw clinical dataset | Selected one sample per patient |
| `N_MUTATION_RECORDS` | Count of MAF rows for selected sample | 0 means no reported mutation rows; not necessarily wild type |
| `N_GENES_WITH_MUTATIONS` | Count of distinct genes with reported mutations | Coverage dependent |
| `HAS_MUTATION_RECORDS` | 1 if sample has >=1 mutation row, otherwise 0 | 0 does not imply no mutations |
| `MUT_REPORTED_AR` | 1 if a mutation row was reported for AR | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_TP53` | 1 if a mutation row was reported for TP53 | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_PTEN` | 1 if a mutation row was reported for PTEN | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_RB1` | 1 if a mutation row was reported for RB1 | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_SPOP` | 1 if a mutation row was reported for SPOP | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_FOXA1` | 1 if a mutation row was reported for FOXA1 | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_BRCA1` | 1 if a mutation row was reported for BRCA1 | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_BRCA2` | 1 if a mutation row was reported for BRCA2 | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_ATM` | 1 if a mutation row was reported for ATM | Blank = no reported mutation; not verified negative |
| `MUT_REPORTED_CDK12` | 1 if a mutation row was reported for CDK12 | Blank = no reported mutation; not verified negative |
| `CNA_AR` | Original CNA value for AR | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_ATM` | Original CNA value for ATM | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_BRCA1` | Original CNA value for BRCA1 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_BRCA2` | Original CNA value for BRCA2 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_CDK12` | Original CNA value for CDK12 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_FOXA1` | Original CNA value for FOXA1 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_PTEN` | Original CNA value for PTEN | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_RB1` | Original CNA value for RB1 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_SPOP` | Original CNA value for SPOP | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `CNA_TP53` | Original CNA value for TP53 | 0 = source diploid/no CNA call; -2, -1.5, 2 preserved; blank = absent |
| `N_CNA_NONZERO` | Count of nonzero CNA entries across 541 genes | Original source values; panel comparability needs review |
| `N_CNA_DEEP_DEL` | Number of CNA entries equal to -2 | Source-defined deep deletion |
| `N_CNA_AMPLIFICATION` | Number of CNA entries equal to 2 | Source-defined amplification |
| `N_CNA_MINUS_1_5` | Number of CNA entries equal to -1.5 | Unusual value; do not recode until clarified |
| `PANEL_mutations` | Mutation assay panel name from gene panel matrix | Not per-gene coverage |
| `PANEL_cna` | CNA assay panel name from gene panel matrix | Not per-gene coverage |
| `PANEL_structural_variants` | Structural-variant assay panel name | Not per-gene coverage |

## Critical limitations
- Clinical stage reflects highest recorded stage, not necessarily sequencing-time stage.
- Mutational absence cannot be interpreted as wild type without per-gene panel coverage.
- Compact 10-gene set is for descriptive review, not unbiased model feature selection.
- Unexpected CNA value -1.5 requires interpretation.
