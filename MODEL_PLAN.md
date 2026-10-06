# Model Plan

## Objective

Predict prostate cancer stage using genomic alterations from the MSK 2024 prostate cancer cohort.

Primary classification target:

- `0` = Stage 1-3
- `1` = Stage 4

Samples with `Unknown` or `NA` stage will be excluded.

## Feature Sets

Three genomic feature sets will be compared:

1. Somatic mutations only
2. Copy-number alterations (CNAs) only
3. Combined mutations + CNAs

The same samples and evaluation procedure will be used across all three feature sets where possible.

## Models

Two model families will be compared:

1. Logistic regression
2. Random forest

This gives six primary model configurations total.

## Data Splitting

The data will be divided into:

- 70% training
- 15% validation
- 15% held-out test

Splitting will be performed at the patient level so that samples from the same patient cannot appear in multiple subsets.

The split will be stratified by stage where feasible.

Initial random seed:

`42`

The held-out test set will not be used for model selection or hyperparameter tuning.

## Preprocessing

Before modelling:

- Match genomic data with clinical stage labels
- Remove samples with unknown or unavailable stage
- Confirm patient and sample identifiers
- Check for patients with multiple samples
- Examine gene-panel coverage
- Decide how mutation and CNA features will be encoded
- Remove unusable or non-informative features if necessary

Any preprocessing or feature-selection step that learns information from the data will be fitted using the training data only.

## Model Tuning

Hyperparameters will be selected using the validation data.

Initial logistic regression parameters to investigate:

- Regularization strength `C`
- L2 regularization

Initial random forest parameters to investigate:

- Number of trees
- Maximum tree depth
- Minimum samples per leaf

The test set will only be evaluated after the final modelling choices are fixed.

## Evaluation

### Primary metric

- AUROC

### Secondary metrics

- AUPRC
- F1 score
- Sensitivity
- Specificity
- Confusion matrix

Accuracy may also be reported but will not be used as the only performance measure.

## Uncertainty

Performance uncertainty will be reported using confidence intervals or repeated runs.

Planned approach:

- 95% bootstrap confidence interval for test-set AUROC

## Interpretability

At least one interpretability or error-analysis method will be included.

Planned options:

- Logistic regression coefficients
- Permutation feature importance
- Random forest feature importance
- Confusion matrix with error analysis

SHAP may be added if feasible.

## Key Methodological Considerations

The analysis will specifically account for:

- patient-level data splitting
- prevention of test-set leakage
- differences in gene-panel coverage
- consistent comparison across mutation, CNA, and combined feature sets
- class balance
- reproducibility using fixed random seeds