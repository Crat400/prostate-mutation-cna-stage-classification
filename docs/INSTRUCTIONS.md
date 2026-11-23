# Reproduction Instructions

**EXSU 500 - Prostate Cancer Stage Classification from Mutation and CNA Data**  
**Repository:** https://github.com/Crat400/prostate-mutation-cna-stage-classification  
**Maintainers:** Huibin Benny Ji, Mehdi Haghi, Sachsin Sinnathurai, Parvinder Ahlawat  
**Status:** Research/education only, **not for clinical use**.

## 1. What is being reproduced?

A predefined binary classification task: highest recorded Stage IV (`1`) versus Stage I-III (`0`) prostate cancer. The inputs are somatic mutation indicators and CNA calls from the public MSK 2024 cBioPortal cohort. Six frozen model configurations (two algorithms x three feature sets) are compared on the same patient-level test set, alongside a majority-class baseline. This is *not* prospective stage prediction or metastatic risk estimation.

The **best validation-selected model** is Combined Random Forest. Its reported held-out AUROC is **0.6603 (95% bootstrap CI 0.6003-0.7190)** with AP **0.6637**. These figures are references for reproducibility, not guarantees of bit-for-bit equality across software environments.

## 2. Obtain code and create the environment

Prerequisites: Git, Python 3.12, internet access for dataset retrieval. **Run all shell commands from the root of the cloned repository**, not the `notebooks` folder.

```powershell
git clone https://github.com/Crat400/prostate-mutation-cna-stage-classification.git
cd prostate-mutation-cna-stage-classification
conda create -n exsu500 python=3.12 -y
conda activate exsu500
python -m pip install -r requirements.txt
python -m ipykernel install --user --name exsu500 --display-name "Python (exsu500)"
```

If Conda is unavailable, use `python -m venv .venv` and activate that environment instead. Register the same `exsu500` Jupyter kernel after installing requirements.

The evaluated local environment reported Python **3.12.15**, NumPy **2.5.3**, Pandas **3.0.6**, scikit-learn **1.9.1**, and joblib **1.6.0**. The `requirements.txt` pins these recorded core versions; exact Jupyter/matplotlib versions were not stored in the evaluation record and must be verified in the successful environment. If package resolution fails, use the team's fully pinned lockfile generated on the successful development machine.

## 3. Download the public data (not included in GitHub)

Study: **Prostate Cancer (MSK, Clinical Cancer Research 2024)**, ID `prostate_msk_2024`.  
Study page: https://www.cbioportal.org/study/summary?id=prostate_msk_2024

Download the **actual study archive**, rather than a GitHub LFS pointer snapshot. Save as:

```text
data/raw/prostate_msk_2024.tar.gz
```

If cBioPortal provides an uncompressed `.tar`, use `--archive data/raw/prostate_msk_2024.tar` in Step 4; the script accepts either `.tar` or `.tar.gz`. Alternatively, extract it until the following directory exists and use `--study-dir`:

```text
data/raw/prostate_msk_2024/data_clinical_patient.txt
```

The study's `data_clinical_patient.txt` must contain a real column-header line with `PATIENT_ID` and `STAGE_HIGHEST_RECORDED`, not `version https://git-lfs.github.com/spec/v1`.

Retrieve the four public gene-panel definitions (used to avoid coding uncovered genes as mutation-negative):

```powershell
python scripts/download_gene_panels.py
```

This downloads the JSON definitions for `IMPACT341`, `IMPACT410`, `IMPACT468`, `IMPACT505` to `data/raw/panels/`. If the API is unavailable, manually save each JSON from `https://www.cbioportal.org/api/gene-panels/<PANEL_ID>` to the same path. Each file must contain a `genes` array with `hugoGeneSymbol` entries. The retrieved `IMPACT468` panel contained **469** records; rely on actual gene lists, not the numeric suffix.

## 4. Prepare and verify the data

For the compressed study archive (replace `.tar.gz` with `.tar` if needed):

```powershell
python scripts/prepare_msk_data.py --archive data/raw/prostate_msk_2024.tar.gz --output-dir data/processed
```

Or, for an extracted study folder, use this **instead of** the previous command:

```powershell
python scripts/prepare_msk_data.py --study-dir data/raw/prostate_msk_2024 --output-dir data/processed
```

Then execute:

```powershell
python scripts/build_msk_masters.py --input-dir data/processed
python scripts/validate_msk_data.py --input-dir data/processed
```

The validator should print **12 PASS checks**. Verify the selected cohort contains **1,967 patients** (943 Stage I-III; 1,024 Stage IV); **9,651** mutation records; **1,064,147** CNA entries across **541** genes; **no missing CNA calls**; and the preserved non-standard CNA category `-1.5` in 174 entries. If these differ, verify the cBioPortal data version before modifying scripts.

## 5. Run the four notebooks in order

From the repository root, start Jupyter:

```powershell
python -m jupyter lab
```

Select kernel **Python (exsu500)**. Open each notebook, select **Restart Kernel -> Run All**, and save. Execute in this order:

| Order | Notebook | Expected output (under `data/processed/`) |
|---|---|---|
| 1 | `notebooks/01_data_check.ipynb` | Clinical, mutation, CNA and sample-panel QC checks |
| 2 | `notebooks/02_split_preprocessing.ipynb` | `patient_splits.csv`; `mutation_feature_matrix.csv` (1967 x 341); `cna_feature_matrix_common.csv` (1967 x 340); `combined_feature_matrix.csv` (1967 x 681) |
| 3 | `notebooks/03_model_training.ipynb` | Validation tables and six fitted `.joblib` pipelines under `data/processed/models/` |
| 4 | `notebooks/04_model_evaluation.ipynb` | `data/processed/evaluation/test_model_comparison.csv`, figures, importance, calibration, paired AUROC comparisons, and `evaluation_record.json` |

**Optional command-line execution:** From the repository root, after installing and registering the kernel, run the following commands in order. Executed notebook copies are saved in the Git-ignored processed directory rather than overwriting the source notebooks.

```powershell
New-Item -ItemType Directory -Force -Path data/processed/executed_notebooks
python -m jupyter nbconvert --to notebook --execute notebooks/01_data_check.ipynb --output 01_data_check.executed.ipynb --output-dir data/processed/executed_notebooks --ExecutePreprocessor.timeout=1800
python -m jupyter nbconvert --to notebook --execute notebooks/02_split_preprocessing.ipynb --output 02_split_preprocessing.executed.ipynb --output-dir data/processed/executed_notebooks --ExecutePreprocessor.timeout=1800
python -m jupyter nbconvert --to notebook --execute notebooks/03_model_training.ipynb --output 03_model_training.executed.ipynb --output-dir data/processed/executed_notebooks --ExecutePreprocessor.timeout=1800
python -m jupyter nbconvert --to notebook --execute notebooks/04_model_evaluation.ipynb --output 04_model_evaluation.executed.ipynb --output-dir data/processed/executed_notebooks --ExecutePreprocessor.timeout=1800
```

If the environment does not use Windows PowerShell, replace the directory-creation line with `mkdir -p data/processed/executed_notebooks`. The four notebook commands otherwise work in typical Unix shells. This automated path has not been independently executed with the user's original raw dataset in this session.

All data-dependent transformations (constant-feature filtering; LR scaling) must be fitted using development data only. The fixed split is 1,376 train, 295 validation, 296 test; test labels: **142 Stage I-III** and **154 Stage IV**. Tuning uses validation only. Finalized models are refitted on train + validation (1,671 patients) before the test evaluation. **Do not modify models or hyperparameters in response to the held-out test results.**

## 6. Expected held-out output (reference)

| Features | Model | AUROC | AP |
|---|---|---:|---:|
| Combined | Random Forest (selected) | **0.6603** | **0.6637** |
| Mutation | Random Forest | 0.6478 | 0.6594 |
| Mutation | Logistic Regression | 0.6171 | 0.6436 |
| Combined | Logistic Regression | 0.5945 | 0.6334 |
| CNA | Random Forest | 0.5525 | 0.5859 |
| CNA | Logistic Regression | 0.5128 | 0.5337 |
| All Stage IV | Majority baseline | 0.5000 | 0.5203 |

For the selected model, expected threshold = `0.5`; confusion matrix rows (actual Stage I-III, Stage IV) / columns (predicted Stage I-III, Stage IV) = `[[80, 62], [46, 108]]`, giving accuracy **63.5%**, sensitivity **70.1%**, specificity **56.3%**. The 95% AUROC interval uses **1,000** bootstrap resamples; small changes can occur with environment/version differences.

Useful outputs: `test_auroc_comparison.png`, `all_models_roc.png`, `all_models_pr.png`, `combined_rf_confusion.png`, `combined_rf_feature_importance.png`, and `combined_rf_calibration.png` under `data/processed/evaluation/`. Figures already included in the public `figures/` folder are illustrative of the **verified prior run** and do not substitute for rerunning notebooks.

## 7. Scientific and data-handling cautions

- Data are public but patient/sample-level records are intentionally excluded from the repository. **Do not commit** `data/raw/`, `data/processed/`, model artifacts, or patient-level prediction CSVs.
- The outcome is `STAGE_HIGHEST_RECORDED`, which may not correspond to stage at sequencing; 349 Stage I-III-labelled records have metastatic samples.
- A common-gene intersection across panel versions was used; 211 mutation rows not matching their panel definitions were excluded. Gene-symbol aliases may account for some mismatches.
- CNA category `-1.5` is preserved; its source interpretation requires verification. No external cohort or prospective clinical validation has been performed.
- Predicted probabilities are **not** clinically calibrated confidence scores. This software is an educational prototype, not a medical device.

## 8. Troubleshooting

- **Missing `PATIENT_ID` / `STAGE_HIGHEST_RECORDED`:** Inspect the archive for Git LFS pointers; use the official cBioPortal archive.
- **`FileNotFoundError` on `data/processed/...`:** Run preprocessing scripts first, launch Jupyter from the repository root, and ensure the `data/processed/` directory exists.
- **Panel JSON missing or unrecognized:** Rerun `scripts/download_gene_panels.py` or save the four API responses manually. The four filenames are case-sensitive.
- **Missing `exsu500` kernel:** Run the `ipykernel install` command from Step 2.
- **Unexpected metrics:** Verify patient split counts, software versions, feature dimensions and source archive version. Do not tune using test performance.
- **No model files:** Complete notebook 03; notebook 04 requires saved pipelines and cannot evaluate using raw CSVs alone.

**Attribution:** Dataset from MSK/cBioPortal. All authors remain responsible for implementation and results. Refer to the course manuscript for references and academic disclosures.
