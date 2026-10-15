from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.chemistry import DESCRIPTOR_NAMES, FINGERPRINT_BITS, featurize_smiles
from src.config import CHECKPOINT_DIRECTORY, RESULT_DIRECTORY, SPLIT_DIRECTORY, TASK_NAMES
from src.evaluation import evaluate_predictions
from src.model import MultiTaskToxicityModel, masked_binary_cross_entropy


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_split(prefix: str, split_name: str) -> pd.DataFrame:
    return pd.read_csv(SPLIT_DIRECTORY / f"{prefix}_{split_name}.csv")


def build_features(data: pd.DataFrame, descriptor_scaler: StandardScaler | None = None, fit_scaler: bool = False):
    fingerprints, descriptors = featurize_smiles(data["canonical_smiles"].tolist())
    if fit_scaler:
        descriptor_scaler = StandardScaler().fit(descriptors)
    if descriptor_scaler is None:
        raise ValueError("A fitted descriptor scaler is required")
    scaled_descriptors = descriptor_scaler.transform(descriptors).astype(np.float32)
    features = np.concatenate([fingerprints, scaled_descriptors], axis=1).astype(np.float32)
    labels = data[TASK_NAMES].to_numpy(dtype=np.float32)
    return features, labels, fingerprints, descriptor_scaler


def prediction_for_model(model, features: np.ndarray, device: torch.device) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(features).to(device))
        return torch.sigmoid(logits).cpu().numpy()


def train_neural_model(
    train_features,
    train_labels,
    validation_features,
    validation_labels,
    epochs,
    batch_size,
    learning_rate,
    seed,
):
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = MultiTaskToxicityModel(train_features.shape[1], len(TASK_NAMES)).to(device)
    label_mask = ~np.isnan(train_labels)
    positive_count = np.nansum(train_labels, axis=0)
    negative_count = np.nansum(1.0 - train_labels, axis=0)
    positive_weights = np.divide(
        negative_count,
        positive_count,
        out=np.ones_like(negative_count, dtype=np.float32),
        where=positive_count > 0,
    )
    positive_weights_tensor = torch.from_numpy(positive_weights.astype(np.float32)).to(device)

    training_dataset = TensorDataset(
        torch.from_numpy(train_features),
        torch.from_numpy(train_labels),
        torch.from_numpy(label_mask.astype(np.float32)),
    )
    generator = torch.Generator().manual_seed(seed)
    training_loader = DataLoader(training_dataset, batch_size=batch_size, shuffle=True, generator=generator)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)

    best_score = -np.inf
    best_state = None
    patience = 12
    epochs_without_improvement = 0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_losses = []
        for features, labels, mask in training_loader:
            features = features.to(device)
            labels = labels.to(device)
            mask = mask.to(device)
            optimizer.zero_grad()
            logits = model(features)
            loss = masked_binary_cross_entropy(logits, labels, mask, positive_weights_tensor)
            loss.backward()
            optimizer.step()
            epoch_losses.append(loss.item())

        validation_probabilities = prediction_for_model(model, validation_features, device)
        validation_metrics = evaluate_predictions(validation_labels, validation_probabilities, "multi_task_mlp", "validation")
        validation_score = float(validation_metrics.loc[validation_metrics["task"] == "MEAN", "roc_auc"].iloc[0])
        history.append({"epoch": epoch, "training_loss": float(np.mean(epoch_losses)), "validation_mean_roc_auc": validation_score})

        if validation_score > best_score + 1e-4:
            best_score = validation_score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            break

    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint")
    model.load_state_dict(best_state)
    model.to(device)
    return model, device, pd.DataFrame(history), positive_weights


def train_single_task_baseline(train_features, train_labels, evaluation_features):
    probabilities = np.full((len(evaluation_features), len(TASK_NAMES)), np.nan, dtype=np.float32)
    models = {}
    for task_index, task_name in enumerate(TASK_NAMES):
        mask = ~np.isnan(train_labels[:, task_index])
        task_labels = train_labels[mask, task_index]
        if len(np.unique(task_labels)) < 2:
            continue
        model = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            solver="liblinear",
            random_state=42,
        )
        model.fit(train_features[mask], task_labels)
        probabilities[:, task_index] = model.predict_proba(evaluation_features)[:, 1]
        models[task_name] = model
    return probabilities, models


def save_predictions(data, labels, probabilities, path: Path) -> None:
    output = data[["compound_id", "canonical_smiles"]].copy()
    for task_index, task_name in enumerate(TASK_NAMES):
        output[f"true_{task_name}"] = labels[:, task_index]
        output[f"probability_{task_name}"] = probabilities[:, task_index]
    output.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate the Tox21 models.")
    parser.add_argument("--split", choices=["scaffold", "random"], default="scaffold")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=42)
    arguments = parser.parse_args()

    set_seed(arguments.seed)
    CHECKPOINT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    RESULT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    train_data = load_split(arguments.split, "train")
    validation_data = load_split(arguments.split, "validation")
    test_data = load_split(arguments.split, "test")

    train_features, train_labels, train_fingerprints, descriptor_scaler = build_features(train_data, fit_scaler=True)
    validation_features, validation_labels, _, _ = build_features(validation_data, descriptor_scaler)
    test_features, test_labels, _, _ = build_features(test_data, descriptor_scaler)

    model, device, history, positive_weights = train_neural_model(
        train_features,
        train_labels,
        validation_features,
        validation_labels,
        arguments.epochs,
        arguments.batch_size,
        arguments.learning_rate,
        arguments.seed,
    )
    validation_probabilities = prediction_for_model(model, validation_features, device)
    test_probabilities = prediction_for_model(model, test_features, device)

    baseline_probabilities, baseline_models = train_single_task_baseline(train_features, train_labels, test_features)
    neural_metrics = evaluate_predictions(test_labels, test_probabilities, "multi_task_mlp", "test")
    baseline_metrics = evaluate_predictions(test_labels, baseline_probabilities, "single_task_logistic", "test")
    metrics = pd.concat([neural_metrics, baseline_metrics], ignore_index=True)

    checkpoint = {
        "state_dict": {key: value.cpu() for key, value in model.state_dict().items()},
        "input_size": train_features.shape[1],
        "task_names": TASK_NAMES,
        "descriptor_names": DESCRIPTOR_NAMES,
        "fingerprint_bits": FINGERPRINT_BITS,
        "split": arguments.split,
        "seed": arguments.seed,
    }
    torch.save(checkpoint, CHECKPOINT_DIRECTORY / f"tox21_multitask_mlp_{arguments.split}.pt")
    joblib.dump(descriptor_scaler, CHECKPOINT_DIRECTORY / f"descriptor_scaler_{arguments.split}.joblib")
    joblib.dump(baseline_models, CHECKPOINT_DIRECTORY / f"single_task_logistic_models_{arguments.split}.joblib")
    np.savez_compressed(
        CHECKPOINT_DIRECTORY / f"training_reference_{arguments.split}.npz",
        fingerprints=train_fingerprints.astype(np.uint8),
        smiles=train_data["canonical_smiles"].to_numpy(),
        compound_ids=train_data["compound_id"].to_numpy(),
    )

    history.to_csv(RESULT_DIRECTORY / f"training_history_{arguments.split}.csv", index=False)
    metrics.to_csv(RESULT_DIRECTORY / f"metrics_{arguments.split}.csv", index=False)
    save_predictions(test_data, test_labels, test_probabilities, RESULT_DIRECTORY / f"test_predictions_{arguments.split}.csv")
    (RESULT_DIRECTORY / f"training_config_{arguments.split}.json").write_text(
        json.dumps(
            {
                "epochs_requested": arguments.epochs,
                "epochs_completed": int(len(history)),
                "batch_size": arguments.batch_size,
                "learning_rate": arguments.learning_rate,
                "seed": arguments.seed,
                "split": arguments.split,
                "device": str(device),
                "positive_weights": dict(zip(TASK_NAMES, positive_weights.tolist())),
            },
            indent=2,
        )
    )

    print(metrics[metrics["task"].isin(["MEAN"])].to_string(index=False))
    print(f"Saved trained model to {CHECKPOINT_DIRECTORY / f'tox21_multitask_mlp_{arguments.split}.pt'}")


if __name__ == "__main__":
    main()
