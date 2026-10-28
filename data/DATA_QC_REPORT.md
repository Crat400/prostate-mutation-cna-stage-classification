# EXSU 500 — MSK 2024 Data Lead validation

## Scope
Validated uploaded processed CSV files and compact patient-level master. These checks do not establish correctness of biological labels or gene-level panel coverage.

## Structural QC
- Patients / samples: **1967 / 1967**
- Compact master columns: **44**
- Unique patient/sample IDs: **PASS**
- Master sample IDs match clinical manifest: **PASS**
- Stage I–III (0): **943**; Stage IV (1): **1024**
- Mutation rows: **9651**; samples with calls: **1853**; no mutation rows: **114**
- Mutation sample IDs outside manifest: **0**
- CNA rows: **1064147**; samples: **1967**; duplicate sample/gene pairs: **0**
- Panel assignment mismatches (clinical vs mapping): **0**
- Nonstandard CNA entries in all selected genes: **{'-1.5': 174}**

## Selected sample types
| Type | Stage I–III | Stage IV | Total |
|---|---:|---:|---:|
| Local Recurrence | 0 | 2 | 2 |
| Metastasis | 349 | 378 | 727 |
| Primary | 594 | 643 | 1237 |
| Unknown | 0 | 1 | 1 |

## Sequencing panel distribution
| Panel | Stage I–III | Stage IV | Total |
|---|---:|---:|---:|
| IMPACT341 | 47 | 84 | 131 |
| IMPACT410 | 206 | 219 | 425 |
| IMPACT468 | 623 | 642 | 1265 |
| IMPACT505 | 67 | 79 | 146 |

## Missing values (excluding intentional blank mutation indicators)
| Variable | Missing |
|---|---:|
| `TUMOR_PURITY` | 13 (0.7%) |
| `MSI_SCORE` | 9 (0.5%) |
| `MSI_TYPE` | 9 (0.5%) |

## Reported mutation counts by stage
These are reported calls divided by all stage-labelled patients, **not coverage-adjusted mutation frequencies**.
| Gene | Stage I–III | Stage IV |
|---|---:|---:|
| AR | 49/943 (5.2%) | 35/1024 (3.4%) |
| TP53 | 217/943 (23.0%) | 351/1024 (34.3%) |
| PTEN | 58/943 (6.2%) | 103/1024 (10.1%) |
| RB1 | 25/943 (2.7%) | 35/1024 (3.4%) |
| SPOP | 160/943 (17.0%) | 123/1024 (12.0%) |
| FOXA1 | 150/943 (15.9%) | 156/1024 (15.2%) |
| BRCA1 | 12/943 (1.3%) | 4/1024 (0.4%) |
| BRCA2 | 40/943 (4.2%) | 42/1024 (4.1%) |
| ATM | 30/943 (3.2%) | 56/1024 (5.5%) |
| CDK12 | 48/943 (5.1%) | 69/1024 (6.7%) |

## Unresolved issues / required decisions
1. **Temporal ambiguity:** `STAGE_HIGHEST_RECORDED` is not stage at sequencing. Do not interpret this dataset as a validated prospective metastasis-prediction cohort.
2. **Metastasis specimen vs stage:** Some Stage I–III-labelled patients have `SAMPLE_TYPE=Metastasis`. Verify clinical definitions with the study documentation and team before treating this as biological consistency.
3. **Panel coverage:** `PANEL_mutations` and `PANEL_cna` give panel names, not per-gene assay coverage. Blank mutation indicators cannot be recoded to negative until coverage is established.
4. **CNA encoding:** Preserve the observed `-1.5` entries and verify source meaning before model encoding.
5. **Preselected genes:** Compact master is descriptive; full mutation/CNA tables should be used for unbiased feature development, with training-only selection.
6. **Leakage:** Do not use `STAGE_RAW` as a predictor. Avoid using clinical fields representing consequences of advanced disease when claiming genomic-only prediction.
7. **Validation:** Model Lead should use patient-level held-out data and assess panel/batch and sample-type confounding.

## Data Lead status
Technical file-level QC complete. Biological label semantics and panel coverage remain open; package suitable for team handoff with these caveats.
