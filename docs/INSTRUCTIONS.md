# Reproduction Instructions

**EXSU 500 - Prostate Cancer Stage Classification from Mutation and CNA Data**  
**Repository:** https://github.com/Crat400/prostate-mutation-cna-stage-classification  
**Maintainers:** Huibin Benny Ji, Mehdi Haghi, Sachsin Sinnathurai, Parvinder Ahlawat  
**Status:** Research/education only, **not for clinical use**.

## 1. What is being reproduced?

A predefined binary classification task: highest recorded Stage IV (`1`) versus Stage I-III (`0`) prostate cancer. The inputs are somatic mutation indicators and CNA calls from the public MSK 2024 cBioPortal cohort. Six frozen model configurations (two algorithms x three feature sets) are compared on the same patient-level test set, alongside a majority-class baseline. This is *not* prospective stage prediction or metastatic risk estimation.

The **best validation-selected model** is Combined Random Forest. Its reported held-out AUROC is **0.6603 (95% bootstrap CI 0.6003-0.7190)** with AP **0.6637**. These figures are references for reproducibility, not guarantees of bit-for-bit equality across software environments.

## 2. Obtain code and create the environment

Prerequisites: Git, Conda (or an existing Python 3.12 installation with venv), and internet access for dataset retrieval. The primary workflow below uses Windows PowerShell and was successfully executed from a fresh clone on November 24, 2026. No VS Code installation is required. **Run all shell commands from the root of the cloned repository**, not the `notebooks` folder.

```powershell
git clone https://github.com/Crat400/prostate-mutation-cna-stage-classification.git
cd prostate-mutation-cna-stage-classification
conda create -n exsu500-professor-test python=3.12 -y
conda activate exsu500-professor-test
python -m pip install -r requirements.txt
python -m ipykernel install --user --name exsu500-professor-test
```

If Conda is unavailable, create an environment using an existing Python 3.12 installation (`python -m venv .venv`), activate it (`.\.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in Unix shells), and run the same pip installation and kernel-registration commands.

The original evaluation recorded Python **3.12.15**. The fresh reproduction used a Python 3.12 Conda environment with NumPy **2.5.3**, Pandas **3.0.6**, scikit-learn **1.9.1**, joblib **1.6.0**, matplotlib **3.11.2**, ipykernel **7.4.0**, and nbconvert **7.17.2**. `requirements.txt` now records the full package snapshot from that successful environment, with the Windows-only `pywinpty` dependency guarded by a platform marker. The snapshot was captured after the successful run; installation from the newly pinned file and non-Windows platforms have not yet been separately tested.

## 3. Download the public data (not included in GitHub)

Study: **Prostate Cancer (MSK, Clinical Cancer Research 2024)**, ID `prostate_msk_2024`.  
Study page: https://www.cbioportal.org/study/summary?id=prostate_msk_2024

First download the public gene-panel definitions:

```powershell
python scripts/download_gene_panels.py
Get-ChildItem "data/raw/panels"
```

Confirm that `IMPACT341.json`, `IMPACT410.json`, `IMPACT468.json`, and `IMPACT505.json` exist. If the API is unavailable, manually save each response from `https://www.cbioportal.org/api/gene-panels/<PANEL_ID>` to that folder. Each file must contain a `genes` array with `hugoGeneSymbol` entries. The original IMPACT468 panel contained 469 records.

Download the actual study archive (not a Git LFS pointer):

```powershell
New-Item -ItemType Directory -Force "data/raw" | Out-Null
curl.exe -L "https://datahub.assets.cbioportal.org/prostate_msk_2024.tar.gz" -o "data/raw/prostate_msk_2024.tar.gz"
Get-Item "data/raw/prostate_msk_2024.tar.gz" | Select-Object Name, Length
tar -tzf "data/raw/prostate_msk_2024.tar.gz" | Select-Object -First 10
```

The archive listing should contain study files under `prostate_msk_2024/`. If the download fails, obtain the study archive from https://www.cbioportal.org/datasets and save it at the same path. If provided as an uncompressed `.tar`, substitute its filename in Step 4. Alternatively, extract the archive and use `--study-dir` as described below. The clinical patient file must contain real data and the `PATIENT_ID` and `STAGE_HIGHEST_RECORDED` headers, not a Git LFS pointer.

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

The validator should complete without errors and, in the original validation script, print 12 PASS checks followed by the data summary. Verify the selected cohort contains **1,967 patients** (943 Stage I-III; 1,024 Stage IV); **9,651** mutation records; **1,064,147** CNA entries across **541** genes; **no missing CNA calls**; and the preserved non-standard CNA category `-1.5` in 174 entries. If these differ, verify the cBioPortal data version before modifying scripts.

## 5. Run the four notebooks in order

The primary method is terminal execution. Run each command separately from the repository root, in order, with the new environment active. Stop if any command fails. These are the commands used for the successful reproduction test:

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_check.ipynb --ExecutePreprocessor.kernel_name=exsu500-professor-test --ExecutePreprocessor.timeout=600
jupyter nbconvert --to notebook --execute --inplace notebooks/02_split_preprocessing.ipynb --ExecutePreprocessor.kernel_name=exsu500-professor-test --ExecutePreprocessor.timeout=600
jupyter nbconvert --to notebook --execute --inplace notebooks/03_model_training.ipynb --ExecutePreprocessor.kernel_name=exsu500-professor-test --ExecutePreprocessor.timeout=1800
jupyter nbconvert --to notebook --execute --inplace notebooks/04_model_evaluation.ipynb --ExecutePreprocessor.kernel_name=exsu500-professor-test --ExecutePreprocessor.timeout=1800
```

`--inplace` saves executed outputs in the local notebook copies. Do not commit these outputs to the public repository, as they may contain patient-level information. A fresh grading clone can be discarded after use. On Windows, the ZMQ event-loop and local unencrypted-kernel warnings may appear without preventing execution. Use a trusted local machine, not a remotely exposed kernel.

| Order | Notebook | Expected output (under `data/processed/`) |
|---|---|---|
| 1 | `01_data_check.ipynb` | Clinical, mutation, CNA and sample-panel QC checks |
| 2 | `02_split_preprocessing.ipynb` | `patient_splits.csv`; mutation (1967 x 341), CNA (1967 x 340) and combined (1967 x 681) feature matrices, excluding ID columns |
| 3 | `03_model_training.ipynb` | Validation tables and six fitted `.joblib` pipelines under `models/` |
| 4 | `04_model_evaluation.ipynb` | Test metrics, figures, importance, calibration, paired AUROC comparisons and `evaluation_record.json` under `evaluation/` |

Verification commands:

```powershell
Get-ChildItem data/processed/*.csv | Select-Object Name
Get-ChildItem data/processed/models | Select-Object Name
Get-ChildItem data/processed/evaluation | Select-Object Name
Import-Csv data/processed/evaluation/test_model_comparison.csv | Format-Table -AutoSize
```

Alternatively, launch `python -m jupyter lab`, select the registered `exsu500-professor-test` kernel, and run all four notebooks in numerical order. The terminal commands are the verified method; JupyterLab is optional.

On macOS/Linux, use `mkdir -p data/raw`, `curl -L` instead of `curl.exe -L`, `ls` for file listings, and `tar -tzf data/raw/prostate_msk_2024.tar.gz | head -n 10` for archive inspection. The notebook execution commands are otherwise the same. For the results table, use `python -c "import pandas as pd; print(pd.read_csv('data/processed/evaluation/test_model_comparison.csv').to_string(index=False))"`. These Unix adaptations have not been tested.

All data-dependent transformations (constant-feature filtering; LR scaling) must be fitted using development data only. The fixed split is 1,376 train, 295 validation, 296 test; test labels: **142 Stage I-III** and **154 Stage IV**. Tuning uses validation only. Finalized models are refitted on train + validation (1,671 patients) before the test evaluation. **Do not modify models or hyperparameters in response to the held-out test results.**

## 6. Expected held-out output (reference)

The November 24, 2026 fresh-clone reproduction matched the original AUROC, AP and trapezoidal AUPRC values for all six configurations and the majority-class baseline to the displayed precision. See [reproducibility check](REPRODUCIBILITY_CHECK.md). This was a rerun of the fixed analysis, not an additional independent test cohort.

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

Useful outputs: `test_auroc_comparison.png`, `all_models_roc.png`, `all_models_pr.png`, `combined_rf_confusion.png`, `combined_rf_feature_importance.png`, and `combined_rf_calibration.png` under `data/processed/evaluation/`. Figures already included in the public `figures/` folder are from the original evaluation run and do not substitute for rerunning notebooks.

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
- **Missing `exsu500-professor-test` kernel:** Run the `ipykernel install` command from Step 2.
- **Unexpected metrics:** Verify patient split counts, software versions, feature dimensions and source archive version. Do not tune using test performance.
- **No model files:** Complete notebook 03; notebook 04 requires saved pipelines and cannot evaluate using raw CSVs alone.

**Attribution:** Dataset from MSK/cBioPortal. All authors remain responsible for implementation and results. Refer to the course manuscript for references and academic disclosures.
