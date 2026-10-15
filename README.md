# Tox21 Multi-Assay Toxicity Prediction

This project trains one shared neural network to predict activity in 12 Tox21 nuclear-receptor and stress-response assays from a molecular SMILES string. It was built for BT5230 Challenge 20.

The important point is that an assay-active prediction is not the same as a claim that a molecule is toxic to a person. This is an educational research model for early screening only.

## What the project does

1. Downloads the public MoleculeNet Tox21 CSV.
2. Validates and canonicalizes SMILES with RDKit.
3. Merges duplicate structures. A conflicting duplicate label is marked missing instead of forcing a false answer.
4. Saves exact 80/10/10 random and Murcko-scaffold splits.
5. Converts each molecule into an ECFP4 fingerprint plus eight simple molecular descriptors.
6. Trains a shared 12-output neural network with a masked binary-cross-entropy loss.
7. Handles imbalance with a separate positive-class weight for each assay.
8. Compares the multi-task network with 12 single-task logistic-regression models.
9. Reports per-assay and mean ROC-AUC and PR-AUC.
10. Runs a Streamlit app for single-molecule prediction and an applicability-domain warning.

## Folder guide

```text
app.py                    Streamlit application
scripts/download_data.py Download the public dataset
scripts/prepare_data.py  Clean data and create exact splits
scripts/train.py         Train the baseline and multi-task model
scripts/make_plots.py    Create report-ready result plots
src/                     Reusable chemistry, model, and evaluation code
splits/                  Exact train, validation, and test CSV files
checkpoints/              Saved fitted models and preprocessing objects
results/                  Metrics, predictions, configuration, and figures
tests/                    Small checks for splitting and masked loss
```

Names are intentionally descriptive so the flow can be followed without guessing what a file does.

## Setup on macOS or Linux

Python 3.11 or 3.12 is the safest choice for RDKit and PyTorch.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the app

The trained scaffold model is already saved in `checkpoints`, so after setup you can directly run:

```bash
streamlit run app.py
```

Streamlit will print a local address, normally `http://localhost:8501`. Open it in a browser, enter a SMILES string, and click **Predict assay activity**.

## Retrain from the beginning (optional)

Run these commands from the project root:

```bash
python scripts/download_data.py
python scripts/prepare_data.py
python scripts/train.py --split scaffold
python scripts/make_plots.py --split scaffold
python -m unittest discover -s tests
```

The first training run may take a few minutes on a laptop. The script automatically uses Apple MPS when it is available and otherwise uses the CPU.

To measure the easier random-split setting separately:

```bash
python scripts/train.py --split random
python scripts/make_plots.py --split random
```

The scaffold and random models use separate filenames, so training one setting does not overwrite the other.

## Main outputs

- `results/data_summary.json`: sample counts, missingness, duplicates, and source SHA-256.
- `splits/scaffold_*.csv`: exact leakage-aware split used for the main result.
- `splits/random_*.csv`: comparison split.
- `checkpoints/tox21_multitask_mlp_scaffold.pt`: main trained shared model.
- `checkpoints/descriptor_scaler_scaffold.joblib`: fitted training-only descriptor scaler.
- `results/metrics_scaffold.csv`: per-assay and mean test metrics for both models.
- `results/test_predictions_scaffold.csv`: labels and held-out probabilities for error analysis.
- `results/figures/`: report-ready plots.

## Why labels are masked

Tox21 has many blank assay entries. A blank means the molecule has no label for that assay; it does not mean inactive. During training, the loss is multiplied by a mask, so missing entries contribute exactly zero loss. The `tests/test_pipeline.py` test checks this behavior.

## Why use a scaffold split

A random split can put close chemical analogues in both training and test sets. A scaffold split keeps each Bemis-Murcko core in only one subset, giving a harder and more honest test of generalization to new chemistry. The project saves both settings because the problem statement asks for scaffold-based reporting and a random result is still useful as a comparison.

## How to read the metrics

- ROC-AUC measures how well active compounds rank above inactive compounds over all thresholds.
- PR-AUC is especially useful here because several assays have few active compounds.
- The mean is an unweighted average across assays for which the test subset contains both classes.
- Compare the shared neural model against the single-task logistic baseline assay by assay. Multi-task learning can help some assays and hurt others; that is a result to discuss, not hide.

## Streamlit interpretation

The app gives 12 assay-activity probabilities and finds the most similar training molecule using ECFP4 Tanimoto similarity. A low maximum similarity is an extrapolation warning. It is not a statistically calibrated confidence interval.

## Reproducibility decisions

- Main random seed: 42.
- Split ratio: 80% train, 10% validation, 10% test.
- Feature calculation is deterministic.
- Descriptor scaling is fitted on training data only.
- Early stopping uses validation mean ROC-AUC, never test performance.
- Test results are calculated only after model selection.
- Raw dataset checksum and full training configuration are saved.

## Reference paper and data

Primary reference: Huang R. et al. (2016), *Tox21Challenge to Build Predictive Models of Nuclear Receptor and Stress Response Pathways as Mediated by Exposure to Environmental Chemicals and Drugs*, Frontiers in Environmental Science, 3:85. The paper describes the 12-assay challenge and the structure-only prediction goal.

Dataset redistribution: MoleculeNet Tox21 CSV from DeepChem. The official Tox21 challenge page documents that 1 means active and 0 means inactive.

- Dataset: https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz
- Tox21 challenge: https://tripod.nih.gov/tox21/challenge/data.jsp
- Reference paper: https://doi.org/10.3389/fenvs.2015.00085
- MoleculeNet paper: https://doi.org/10.1039/C7SC02664A

## Limitations and responsible use

- These are in-vitro pathway assays, not direct clinical outcomes.
- Sparse labels and strong class imbalance make some assay estimates unstable.
- Scaffold splitting is more realistic than random splitting but is not a perfect simulation of future chemical discovery.
- Similarity-based applicability is only a warning, not uncertainty calibration.
- Dataset activity can reflect assay interference and experimental noise.
- The system must not be used for medical, regulatory, environmental, or safety decisions.

## AI assistance acknowledgement

AI assistance was used for code organization, documentation, and debugging. Dataset choices, scientific interpretation, experiment execution, result checking, and final conclusions must be reviewed and defended by the student team.
