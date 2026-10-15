from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.chemistry import canonicalize_smiles, murcko_scaffold
from src.config import TASK_NAMES


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _consensus_label(values: pd.Series) -> float:
    available = values.dropna().astype(float)
    if available.empty:
        return np.nan
    unique_values = set(available.tolist())
    if len(unique_values) == 1:
        return float(available.iloc[0])
    return np.nan


def clean_tox21(raw_data_file: Path, output_file: Path, summary_file: Path) -> pd.DataFrame:
    raw_data = pd.read_csv(raw_data_file)
    required_columns = {"smiles", *TASK_NAMES}
    missing_columns = required_columns - set(raw_data.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in Tox21 file: {sorted(missing_columns)}")

    clean_data = raw_data[["smiles", *TASK_NAMES]].copy()
    clean_data["canonical_smiles"] = clean_data["smiles"].map(canonicalize_smiles)
    invalid_count = int(clean_data["canonical_smiles"].isna().sum())
    clean_data = clean_data.dropna(subset=["canonical_smiles"])

    conflict_count = 0
    for _, group in clean_data.groupby("canonical_smiles"):
        for task_name in TASK_NAMES:
            available = group[task_name].dropna()
            if available.nunique() > 1:
                conflict_count += 1

    grouped = clean_data.groupby("canonical_smiles", sort=True)
    deduplicated = grouped[TASK_NAMES].agg(_consensus_label).reset_index()
    deduplicated.insert(0, "compound_id", [f"tox21_{number:05d}" for number in range(len(deduplicated))])
    deduplicated["scaffold"] = deduplicated["canonical_smiles"].map(murcko_scaffold)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    deduplicated.to_csv(output_file, index=False)

    task_summary = {}
    for task_name in TASK_NAMES:
        observed = deduplicated[task_name].dropna()
        task_summary[task_name] = {
            "observed": int(len(observed)),
            "active": int((observed == 1).sum()),
            "inactive": int((observed == 0).sum()),
            "missing": int(deduplicated[task_name].isna().sum()),
            "active_fraction": float(observed.mean()),
        }

    summary = {
        "source_sha256": file_sha256(raw_data_file),
        "raw_rows": int(len(raw_data)),
        "invalid_smiles_removed": invalid_count,
        "unique_molecules": int(len(deduplicated)),
        "duplicate_rows_removed": int(len(clean_data) - len(deduplicated)),
        "conflicting_duplicate_task_labels_masked": conflict_count,
        "task_summary": task_summary,
    }
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(json.dumps(summary, indent=2))
    return deduplicated


def random_split(data: pd.DataFrame, seed: int = 42) -> dict[str, np.ndarray]:
    random_generator = np.random.default_rng(seed)
    indices = random_generator.permutation(len(data))
    train_end = int(0.8 * len(data))
    validation_end = int(0.9 * len(data))
    return {
        "train": indices[:train_end],
        "validation": indices[train_end:validation_end],
        "test": indices[validation_end:],
    }


def scaffold_split(data: pd.DataFrame, seed: int = 42) -> dict[str, np.ndarray]:
    groups = [group.index.to_numpy() for _, group in data.groupby("scaffold", sort=True)]
    random_generator = np.random.default_rng(seed)
    random_generator.shuffle(groups)
    groups.sort(key=len, reverse=True)

    train_cutoff = int(0.8 * len(data))
    validation_cutoff = int(0.9 * len(data))
    allocated: dict[str, list[int]] = {"train": [], "validation": [], "test": []}

    # Size-ordered allocation follows the common MoleculeNet/DeepChem scaffold
    # splitter behavior. A scaffold is never divided, so final ratios can vary
    # slightly from 80/10/10 when a scaffold family is large.
    for group in groups:
        if len(allocated["train"]) + len(group) <= train_cutoff:
            destination = "train"
        elif len(allocated["train"]) + len(allocated["validation"]) + len(group) <= validation_cutoff:
            destination = "validation"
        else:
            destination = "test"
        allocated[destination].extend(group.tolist())

    return {name: np.asarray(sorted(indices), dtype=int) for name, indices in allocated.items()}


def save_splits(data: pd.DataFrame, split_indices: dict[str, np.ndarray], directory: Path, prefix: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for split_name, indices in split_indices.items():
        columns = ["compound_id", "canonical_smiles", "scaffold", *TASK_NAMES]
        data.iloc[indices][columns].to_csv(directory / f"{prefix}_{split_name}.csv", index=False)


def verify_no_scaffold_leakage(directory: Path, prefix: str = "scaffold") -> None:
    scaffold_sets = {}
    for split_name in ("train", "validation", "test"):
        split_data = pd.read_csv(directory / f"{prefix}_{split_name}.csv", keep_default_na=False)
        scaffold_sets[split_name] = set(split_data["scaffold"])
    if scaffold_sets["train"] & scaffold_sets["validation"]:
        raise AssertionError("Scaffold overlap found between train and validation")
    if scaffold_sets["train"] & scaffold_sets["test"]:
        raise AssertionError("Scaffold overlap found between train and test")
    if scaffold_sets["validation"] & scaffold_sets["test"]:
        raise AssertionError("Scaffold overlap found between validation and test")
