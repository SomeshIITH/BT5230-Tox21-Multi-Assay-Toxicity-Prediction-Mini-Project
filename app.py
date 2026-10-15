from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import torch
from rdkit import Chem
from rdkit.Chem import Draw

from src.chemistry import featurize_smiles, molecular_descriptors, tanimoto_similarity
from src.config import CHECKPOINT_DIRECTORY, TASK_EXPLANATIONS, TASK_NAMES
from src.model import MultiTaskToxicityModel


st.set_page_config(page_title="Tox21 Multi-Assay Predictor", page_icon="🧪", layout="wide")


@st.cache_resource
def load_project_files():
    checkpoint_path = CHECKPOINT_DIRECTORY / "tox21_multitask_mlp_scaffold.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError("Model checkpoint is missing. Run the training commands in README.md.")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    model = MultiTaskToxicityModel(checkpoint["input_size"], len(checkpoint["task_names"]))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    scaler = joblib.load(CHECKPOINT_DIRECTORY / "descriptor_scaler_scaffold.joblib")
    references = np.load(CHECKPOINT_DIRECTORY / "training_reference_scaffold.npz", allow_pickle=True)
    return model, scaler, references, checkpoint


def applicability_message(maximum_similarity: float) -> tuple[str, str]:
    if maximum_similarity >= 0.60:
        return "Inside the model's familiar chemical space", "success"
    if maximum_similarity >= 0.35:
        return "Moderate similarity to training chemistry; use caution", "warning"
    return "Outside the familiar chemical space; prediction is unreliable", "error"


st.title("Tox21 Multi-Assay Toxicity Predictor")
st.caption("A student-built research prototype trained on 12 Tox21 pathway assays")
st.info(
    "This app predicts assay activity, not human toxicity or clinical safety. "
    "Use it only for educational and early research screening."
)

try:
    model, scaler, references, checkpoint = load_project_files()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

example_smiles = {
    "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Caffeine": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
    "Acetaminophen": "CC(=O)NC1=CC=C(O)C=C1O",
}

left_column, right_column = st.columns([2, 1])
with left_column:
    selected_example = st.selectbox("Optional example", ["Custom", *example_smiles.keys()])
    default_smiles = example_smiles.get(selected_example, "CC(=O)OC1=CC=CC=C1C(=O)O")
    smiles = st.text_input("Enter one SMILES string", value=default_smiles)
    predict_button = st.button("Predict assay activity", type="primary")

if predict_button:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        st.error("The SMILES string is not valid. Please check the structure and try again.")
        st.stop()

    canonical_smiles = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)
    fingerprints, descriptors = featurize_smiles([canonical_smiles])
    scaled_descriptors = scaler.transform(descriptors).astype(np.float32)
    features = np.concatenate([fingerprints, scaled_descriptors], axis=1).astype(np.float32)
    with torch.no_grad():
        probabilities = torch.sigmoid(model(torch.from_numpy(features))).numpy()[0]

    similarities = tanimoto_similarity(canonical_smiles, references["fingerprints"])
    nearest_index = int(np.argmax(similarities))
    maximum_similarity = float(similarities[nearest_index])
    applicability_text, applicability_level = applicability_message(maximum_similarity)

    with right_column:
        st.image(Draw.MolToImage(molecule, size=(360, 260)), caption=canonical_smiles)
        st.metric("Nearest training similarity", f"{maximum_similarity:.2f}")
        getattr(st, applicability_level)(applicability_text)
        st.caption(f"Nearest training compound: {references['compound_ids'][nearest_index]}")

    result_data = pd.DataFrame(
        {
            "Assay": TASK_NAMES,
            "Meaning": [TASK_EXPLANATIONS[name] for name in TASK_NAMES],
            "Predicted activity probability": probabilities,
        }
    ).sort_values("Predicted activity probability", ascending=False)
    st.subheader("Predicted assay activity")
    st.dataframe(
        result_data,
        hide_index=True,
        width="stretch",
        column_config={
            "Predicted activity probability": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="%.3f",
            )
        },
    )
    st.bar_chart(result_data.set_index("Assay")["Predicted activity probability"])

    descriptor_values = molecular_descriptors(canonical_smiles)
    descriptor_table = pd.DataFrame(
        {"Descriptor": checkpoint["descriptor_names"], "Value": descriptor_values}
    )
    with st.expander("Molecular descriptors used with the fingerprint"):
        st.dataframe(descriptor_table, hide_index=True, width="stretch")

with st.expander("How to interpret this page"):
    st.write(
        "The model returns the probability that a compound is active in each in-vitro pathway assay. "
        "The values are not interchangeable with organ-level or patient-level toxicity. The nearest-training "
        "similarity is a simple applicability-domain warning: low similarity means the model is extrapolating."
    )
