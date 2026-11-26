from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Prostate Cancer Genomic Classifier",
    layout="centered"
)

st.title("Prostate Cancer Genomic Classifier")

st.error(
    "COURSE PROTOTYPE — NOT FOR CLINICAL USE. "
    "This application is for research and educational purposes only. "
    "It is not a medical device and must not be used for clinical decisions."
)

st.write(
    "This application uses a trained Random Forest model to "
    "classify prostate cancer as Stage I-III or Stage IV "
    "based on somatic mutations and copy-number alterations."
)

st.caption(
    "The prediction target is the highest recorded cancer stage, "
    "which may differ from the stage at specimen collection."
)

# Load trained model
MODEL_PATH = Path(__file__).parent / "models" / "combined_random_forest.joblib"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


try:
    model = load_model()
    feature_names = list(model.feature_names_in_)
except Exception as e:
    st.error(f"Unable to load model: {e}")
    st.stop()

st.subheader("1. Upload genomic data")

st.write(
    f"Upload a CSV containing exactly {len(feature_names)} genomic "
    "features. Do not upload identifying patient information."
)

# Downloadable template
template = pd.DataFrame(
    np.zeros((1, len(feature_names))),
    columns=feature_names
)

st.download_button(
    "Download CSV Template",
    template.to_csv(index=False),
    file_name="genomic_input_template.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        uploaded = pd.read_csv(uploaded_file)

        missing = set(feature_names) - set(uploaded.columns)
        extra = set(uploaded.columns) - set(feature_names)

        if missing or extra:
            st.error(
                f"Invalid columns: {len(missing)} missing, "
                f"{len(extra)} unexpected."
            )
            st.stop()

        if uploaded.empty:
            st.error("The CSV must contain at least one row.")
            st.stop()

        if len(uploaded) > 20:
            st.error("Upload at most 20 samples at a time.")
            st.stop()

        X = uploaded[feature_names].apply(
            pd.to_numeric, errors="coerce"
        )

        if not np.isfinite(X.to_numpy()).all():
            st.error("All features must contain finite numeric values.")
            st.stop()

        mutation_cols = [
            c for c in feature_names if c.startswith("MUT__")
        ]
        cna_cols = [
            c for c in feature_names if c.startswith("CNA__")
        ]

        if not X[mutation_cols].isin([0, 1]).all().all():
            st.error("Mutation features must be 0 or 1.")
            st.stop()

        if not X[cna_cols].isin([-2, -1.5, 0, 2]).all().all():
            st.error("Unexpected CNA encoding.")
            st.stop()

        st.subheader("2. Prediction")

        positive_index = list(model.classes_).index(1)
        probabilities = model.predict_proba(X)[:, positive_index]

        selected = st.selectbox(
            "Choose sample",
            range(len(X)),
            format_func=lambda i: f"Sample {i + 1}"
        )

        probability = float(probabilities[selected])
        prediction = "Stage IV" if probability >= 0.5 else "Stage I–III"
        confidence = max(probability, 1 - probability)

        st.metric("Predicted Stage", prediction)
        st.metric(
            "Predicted-class Probability",
            f"{confidence:.1%}"
        )

        st.caption(
            "Probabilities are uncalibrated model estimates, "
            "not clinically validated confidence measures."
        )

        st.subheader("3. Model Interpretability")

        # Feature importance from the trained Random Forest
        selector = model.named_steps["nonconstant"]
        forest = model.named_steps["classifier"]

        retained_features = np.array(feature_names)[
            selector.get_support()
        ]

        importance = pd.Series(
            forest.feature_importances_,
            index=retained_features
        ).sort_values(ascending=False)

        st.write("Top 10 globally important genomic features")
        st.bar_chart(importance.head(10))

        st.caption(
            "These are global feature importances, not explanations "
            "of an individual prediction or evidence of causation."
        )

    except Exception as e:
        st.error(f"Unable to process input: {e}")