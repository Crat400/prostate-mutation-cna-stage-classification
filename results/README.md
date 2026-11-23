# Exported aggregate evaluation results

These results and figures are from the team's previously executed held-out evaluation (November 2026), not synthetic example outputs. The repository does **not** include per-patient predictions or original genomic datasets. To regenerate the tables and figures, follow [`docs/INSTRUCTIONS.md`] and run notebook 04 after completing notebooks 01-03.

- `test_model_comparison.csv`: metrics for the six model configurations and majority-class baseline.
- `paired_auroc_comparisons.csv`: paired bootstrap AUROC differences (exploratory; no multiplicity adjustment).
- `feature_importance.csv`: global model feature scores; impurity importance is not causal.
- `combined_rf_calibration.csv`: five-bin reliability data.
- `exploratory_subgroups.csv`: panel- and sample-type-level descriptive metrics.
- `evaluation_record.json`: provenance, hyperparameters, software versions, and file hashes of the original run.

Figures live in [`figures/`](../figures/). The held-out test was used only for final evaluation, not for hyperparameter selection; do not retune models using the published results.
