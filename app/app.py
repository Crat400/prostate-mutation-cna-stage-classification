"""EXSU 500 educational prostate cancer genomic classification interface."""

import csv
import io
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "models" / "combined_random_forest.joblib"
REPOSITORY_URL = "https://github.com/Crat400/prostate-mutation-cna-stage-classification"
MAX_SAMPLES = 20
MAX_BYTES = 2 * 1024 * 1024
CNA_VALUES = (-2, -1.5, 0, 2)
THRESHOLD = 0.5
DISCLAIMER = (
    "COURSE PROTOTYPE: NOT FOR CLINICAL USE. "
    "This application is for research and educational purposes only. "
    "It is not a medical device and must not be used for clinical decisions."
)

PRESETS = {
    "Zero-alteration example": {},
    "Mutation example": {"MUT__TP53": 1, "MUT__SPOP": 1},
    "Combined alteration example": {
        "MUT__TP53": 1,
        "MUT__PTEN": 1,
        "CNA__MYC": 2,
        "CNA__RB1": -2,
    },
}


@st.cache_resource
def load_model():
    # Only load the trusted model distributed with this project.
    return joblib.load(MODEL_PATH)


def validate_schema(model):
    features = list(model.feature_names_in_)
    mutation_cols = [c for c in features if c.startswith("MUT__")]
    cna_cols = [c for c in features if c.startswith("CNA__")]
    if (
        len(features) != 681
        or len(set(features)) != 681
        or len(mutation_cols) != 341
        or len(cna_cols) != 340
        or set(model.classes_) != {0, 1}
    ):
        raise ValueError("The model does not match the expected combined feature schema.")
    return features, mutation_cols, cna_cols


def zero_template(features):
    return pd.DataFrame(np.zeros((1, len(features))), columns=features)


def validate_input(frame, features):
    if frame.columns.duplicated().any():
        raise ValueError("Duplicate column names are not allowed.")
    missing = set(features) - set(frame.columns)
    extra = set(frame.columns) - set(features)
    if missing or extra:
        raise ValueError(
            f"Invalid columns: {len(missing)} missing, {len(extra)} unexpected. "
            "Use the downloadable template with its original column names."
        )
    if frame.empty or len(frame) > MAX_SAMPLES:
        raise ValueError(f"The CSV must contain 1 to {MAX_SAMPLES} samples.")
    X = frame[features].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("All features must contain finite numeric values. Missing values are not allowed.")
    mutation_cols = [c for c in features if c.startswith("MUT__")]
    cna_cols = [c for c in features if c.startswith("CNA__")]
    if not X[mutation_cols].isin([0, 1]).all().all():
        raise ValueError("Mutation features must be 0 or 1.")
    if not X[cna_cols].isin(CNA_VALUES).all().all():
        raise ValueError("CNA features must be -2, -1.5, 0 or 2.")
    return X.astype(float)


def parse_csv(raw, features):
    if len(raw) > MAX_BYTES:
        raise ValueError("The CSV exceeds the 2 MB application limit.")
    try:
        reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
        header = next(reader, None)
        if not header:
            raise ValueError("The CSV is empty or has no header.")
        if len(set(header)) != len(header):
            raise ValueError("Duplicate column names are not allowed.")
        rows = []
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError("Every data row must have the same number of fields as the header.")
            rows.append(row)
            if len(rows) > MAX_SAMPLES:
                raise ValueError(f"Upload at most {MAX_SAMPLES} samples at a time.")
    except (UnicodeError, csv.Error) as exc:
        raise ValueError("Unable to read the CSV. Save it as a UTF-8 comma-separated file.") from exc
    return validate_input(pd.DataFrame(rows, columns=header), features)


def synthetic_input(features, selected_mutations, selected_cnas):
    X = zero_template(features)
    for feature in selected_mutations:
        X.loc[0, feature] = 1
    for feature, value in selected_cnas.items():
        X.loc[0, feature] = value
    return validate_input(X, features)


def model_importance(model, features):
    selector = model.named_steps["nonconstant"]
    forest = model.named_steps["classifier"]
    retained = np.asarray(features)[selector.get_support()]
    return pd.Series(forest.feature_importances_, index=retained).sort_values(ascending=False)


def input_help():
    with st.expander("Input format and accepted genomic values"):
        st.markdown(
            "**Mutation features (`MUT__`):** `0` = no recorded mutation in a covered gene; "
            "`1` = recorded mutation.\n\n"
            "**CNA features (`CNA__`):** `-2` = deletion call; `0` = no copy-number "
            "alteration call; `2` = amplification call. The source dataset also contains "
            "`-1.5`, which is accepted to preserve the original encoding. Its biological "
            "interpretation has not been established in this project.\n\n"
            "The model expects the shared sequencing-panel feature set, not arbitrary "
            "clinical genetic test results. Missing or unmeasured values must not be "
            "replaced with zeros merely to obtain a prediction."
        )


def demo_controls(features, mutation_cols, cna_cols):
    st.info(
        "These are fictional inputs constructed for software demonstration only. "
        "They are not real patient profiles or examples of known cancer stages."
    )
    preset = st.selectbox("Choose a synthetic example", list(PRESETS), index=2)
    defaults = PRESETS[preset]
    with st.expander("Customize gene alterations", expanded=True):
        left, right = st.columns(2)
        with left:
            selected_mutations = st.multiselect(
                "Mutation-positive genes",
                options=sorted(mutation_cols),
                default=[c for c in mutation_cols if defaults.get(c) == 1],
                format_func=lambda c: c.split("__", 1)[1],
                key=f"mutations_{preset}",
            )
        with right:
            selected_cna_genes = st.multiselect(
                "Genes with copy-number alterations",
                options=sorted(cna_cols),
                default=[c for c in cna_cols if defaults.get(c, 0) != 0],
                format_func=lambda c: c.split("__", 1)[1],
                key=f"cna_genes_{preset}",
            )
            selected_cnas = {}
            for feature in selected_cna_genes:
                values = [-2, -1.5, 2]
                default = defaults.get(feature, 2)
                selected_cnas[feature] = st.selectbox(
                    f"{feature.split('__', 1)[1]} CNA value",
                    values,
                    index=values.index(default),
                    key=f"{preset}_{feature}",
                )
        st.caption("All remaining features are set to zero for this synthetic demonstration.")
    X = synthetic_input(features, selected_mutations, selected_cnas)
    st.download_button(
        "Download this synthetic example",
        X.to_csv(index=False),
        file_name="synthetic_genomic_example.csv",
        mime="text/csv",
    )
    return X


def upload_controls(features):
    st.write(
        f"Upload a UTF-8 CSV with exactly {len(features)} genomic feature columns "
        f"and 1 to {MAX_SAMPLES} rows."
    )
    st.warning("Use synthetic inputs only. Do not upload real patient records or identifying information.")
    st.download_button(
        "Download CSV template",
        zero_template(features).to_csv(index=False),
        file_name="genomic_input_template.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=False)
    if uploaded is None:
        st.info("Upload a completed synthetic CSV to view predictions.")
        return None
    try:
        return parse_csv(uploaded.getvalue(), features)
    except ValueError as exc:
        st.error(str(exc))
        return None


def show_predictions(model, X):
    st.subheader("2. Model prediction")
    positive_index = list(model.classes_).index(1)
    probabilities = model.predict_proba(X)[:, positive_index]
    selected = st.selectbox(
        "Choose sample", range(len(X)), format_func=lambda i: f"Sample {i + 1}"
    )
    p = float(probabilities[selected])
    positive = p >= THRESHOLD
    prediction = "Stage IV" if positive else "Stage I-III"
    predicted_probability = p if positive else 1 - p
    a, b = st.columns(2)
    a.metric("Predicted stage", prediction)
    b.metric("Predicted-class probability", f"{predicted_probability:.1%}")
    st.write("**Estimated probability of Stage IV**")
    st.progress(p, text=f"{p:.1%} Stage IV | {1-p:.1%} Stage I-III")
    st.caption(
        "Classification threshold: 0.50 for Stage IV. Probabilities are uncalibrated "
        "model estimates, not clinically validated confidence measures or forecasts of future progression."
    )
    if len(X) > 1:
        summary = pd.DataFrame({
            "Sample": [f"Sample {i+1}" for i in range(len(X))],
            "Predicted stage": np.where(probabilities >= THRESHOLD, "Stage IV", "Stage I-III"),
            "Stage IV probability": [f"{q:.1%}" for q in probabilities],
        })
        st.dataframe(summary, hide_index=True)


def show_importance(model, features):
    st.subheader("3. Model interpretability")
    importance = model_importance(model, features).head(10)
    labels = [c.replace("MUT__", "Mutation: ").replace("CNA__", "CNA: ") for c in importance.index]
    colors = ["#356FA3" if c.startswith("MUT__") else "#C48338" for c in importance.index]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(labels, importance.to_numpy(), color=colors, height=0.65)
    ax.invert_yaxis()
    ax.set_xlabel("Random forest impurity-based importance")
    ax.set_title("Top 10 global genomic features", loc="left", fontweight="bold")
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.18)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption(
        "Global importance is calculated from the trained random forest. It does not explain "
        "why an individual sample received a prediction, indicate the direction of a gene's effect, "
        "or establish causation."
    )


def show_performance():
    st.subheader("4. Held-out model performance")
    st.caption("Combined Random Forest | Independent held-out test split of 296 patients within the MSK cohort")
    a, b, c, d = st.columns(4)
    a.metric("AUROC", "0.660")
    b.metric("Average precision", "0.664")
    c.metric("Sensitivity", "70.1%")
    d.metric("Specificity", "56.3%")
    st.caption("AUROC 95% bootstrap CI: 0.600 to 0.719. Accuracy: 63.5%. Sensitivity and specificity use the 0.50 threshold.")
    st.markdown(
        "The model shows modest discrimination and makes substantial classification errors. "
        "These are fixed research results from the held-out cohort, not measures of accuracy on your uploaded inputs."
    )
    with st.expander("Model development and limitations"):
        st.markdown(
            "- Public MSK 2024 prostate cancer cohort (cBioPortal): 1,967 patients.\n"
            "- Patient-level split: 1,376 training, 295 validation and 296 test patients.\n"
            "- Random Forest trained on combined mutation and CNA features, selected using validation AUROC.\n"
            "- Highest recorded stage may differ from the stage at specimen collection.\n"
            "- Sparse genomic features and variable panel coverage limit predictive information.\n"
            "- No external or prospective clinical validation was performed.\n"
            "- Probabilities are not clinically calibrated. Do not use this prototype to guide care."
        )


def main():
    st.set_page_config(page_title="Prostate Cancer Genomic Classifier", layout="wide")
    st.title("Prostate Cancer Genomic Classifier")
    st.error(DISCLAIMER)
    st.sidebar.warning(DISCLAIMER)
    st.sidebar.markdown(f"[Project repository]({REPOSITORY_URL})")
    st.sidebar.caption("McGill University | EXSU 500 | Fall 2026")
    st.write(
        "Explore a trained Random Forest that classifies the highest recorded prostate cancer "
        "stage as Stage I-III or Stage IV using somatic mutations and copy-number alterations."
    )
    st.caption("This is retrospective stage classification, not a diagnosis or prediction of future metastasis.")
    try:
        model = load_model()
        features, mutation_cols, cna_cols = validate_schema(model)
    except Exception:
        st.error("Unable to load the expected trained model. Check that the model artifact and matching package versions are installed.")
        st.stop()
        return

    st.subheader("1. Genomic input")
    mode = st.radio("Input method", ["Try a synthetic demo", "Upload a synthetic CSV"], horizontal=True)
    input_help()
    if mode == "Try a synthetic demo":
        X = demo_controls(features, mutation_cols, cna_cols)
    else:
        X = upload_controls(features)
    if X is not None:
        try:
            show_predictions(model, X)
        except Exception:
            st.error("Unable to generate a prediction. Check the input and model configuration.")
    try:
        show_importance(model, features)
    except Exception:
        st.error("Unable to display feature importance. Check the trained model configuration.")
    show_performance()
    st.divider()
    st.caption("EXSU 500 | Research and educational prototype | McGill University")
    st.markdown(f"[Code, model card and reproduction instructions]({REPOSITORY_URL})")


if __name__ == "__main__":
    main()
