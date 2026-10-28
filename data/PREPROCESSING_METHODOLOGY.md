# Data Lead preprocessing methodology — MSK prostate cancer 2024

## Objective and provenance

Prepare aligned clinical and tumor genomic records for EXSU 500's research question: whether somatic mutations and copy-number alterations can distinguish patients labelled Stage I–III from Stage IV. Source: cBioPortal **Prostate Cancer (MSK, Clinical Cancer Research 2024)**, study ID `prostate_msk_2024`. The original cBioPortal archive is downloaded locally and is **not committed to GitHub**.

## Source inputs

- `data_clinical_patient.txt`: `PATIENT_ID`, `STAGE_HIGHEST_RECORDED`.
- `data_clinical_sample.txt`: `SAMPLE_ID`, `PATIENT_ID`, sample type, panel, coverage and other sample-level annotations.
- `data_mutations.txt` (specified by `meta_mutations.txt`): long-form MAF.
- `data_CNA.txt` (specified by `meta_CNA.txt`): wide discrete CNA matrix.
- `data_gene_panel_matrix.txt`: sample-to-profile panel assignments.

## Eligibility and stage definition

- Stage label source: **`STAGE_HIGHEST_RECORDED`**, which is *not necessarily stage at sample collection*.
- `Stage 1-3` → `stage_binary=0`; `Stage 4` → `stage_binary=1`.
- Exclude `Unknown` or missing stage from `clinical_manifest.csv` and genomic outputs; retain all stages in `clinical_all_samples.csv`.
- Of 2,257 patients (2,260 samples), 943 have Stage I–III, 1,024 Stage IV, and 290 unknown/missing stage. The selected cohort has 1,967 patients.

## One sample per patient

Sort by patient ID, descending numeric `SAMPLE_COVERAGE`, then ascending `SAMPLE_ID` to break ties or missing-coverage cases. Retain one selected sample per patient. Preserve original IDs and `N_SAMPLES_PER_PATIENT`. There are 3 patients with more than one raw sample.

## Mutation preparation

Filter MAF to selected `SAMPLE_ID`s. Preserve `HUGO_SYMBOL`, variant classification, protein changes, coordinates, alleles and counts where available. **Do not convert absent mutation records into wild-type calls.** There are 9,651 selected MAF rows, representing 1,853 samples and 480 genes; 114 selected samples have no reported mutation row. Those 114 are not necessarily mutation-negative.

## CNA preparation

Read discrete CNA data in wide format and pivot to long form: `PATIENT_ID`, `SAMPLE_ID`, `HUGO_SYMBOL`, `CNA_VALUE`. Do not impute, round or collapse CNA values. Selected output contains 1,064,147 sample–gene records (1,967 × 541), with no missing values. Observed values include `-2`, **`-1.5`**, `0`, and `2`. The 174 entries equal to `-1.5` are preserved and flagged. The source's biological meaning for `-1.5` requires clarification before recoding.

## Gene-panel metadata

Retain sample-level panel assignments (`mutations`, `cna`, `structural_variants`). The four selected sample panels are IMPACT341, IMPACT410, IMPACT468 and IMPACT505. **Panel identifiers are not gene-level coverage definitions.** A negative mutation feature requires confirmation that the relevant gene was assayed and adequately covered.

## Master files

- `EXSU500_MSK_master_descriptive.csv`: one row per patient, all observed mutation-gene counts and all CNA gene columns (1,967 × 1,041). Mutation no-call cells are missing; original CNA values retained.
- `EXSU500_MSK_master_compact.csv`: one row per patient (1,967 × 44), with selected clinical variables, mutation totals, ten prespecified prostate cancer gene mutation indicators (`1` if reported; missing otherwise), ten corresponding CNA columns, CNA summary counts and panel metadata. Genes: AR, TP53, PTEN, RB1, SPOP, FOXA1, BRCA1, BRCA2, ATM, CDK12. These were chosen for interpretability, **not by stage association or model feature selection**.
- `N_MUTATION_RECORDS=0` means zero reported rows, not a confirmed absence of mutations.

## QC and unresolved limitations

Validation checks unique patient/sample IDs, aligned sample sets, stage recoding, duplicate CNA sample/gene pairs, panel assignment agreement, missingness and CNA value distributions. See `DATA_QC_REPORT.md`, `DATA_DICTIONARY.md` and `QC_validation_console.txt`.

Unresolved scientific questions: timing of highest recorded stage relative to sequencing; 349 Stage I–III-labelled patients with `SAMPLE_TYPE=Metastasis`; gene-by-gene assay coverage; source interpretation of CNA `-1.5`; possible panel and specimen-type confounding. **File-level QC passing does not resolve these issues.**

## Scope boundaries

Data Lead does not impute, scale, select genes using outcomes, split train/test data, fit models or claim prediction performance. Model Lead should define coverage-aware mutation encoding, leakage-safe feature handling, patient-level validation and panel/sampling sensitivity analyses. Keep source archive outside GitHub.
