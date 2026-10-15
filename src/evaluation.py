from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.config import TASK_NAMES


def evaluate_predictions(labels: np.ndarray, probabilities: np.ndarray, model_name: str, split_name: str) -> pd.DataFrame:
    rows = []
    for task_index, task_name in enumerate(TASK_NAMES):
        task_labels = labels[:, task_index]
        task_probabilities = probabilities[:, task_index]
        mask = ~np.isnan(task_labels)
        observed_labels = task_labels[mask]
        observed_probabilities = task_probabilities[mask]
        if len(np.unique(observed_labels)) < 2:
            roc_auc = np.nan
            pr_auc = np.nan
        else:
            roc_auc = roc_auc_score(observed_labels, observed_probabilities)
            pr_auc = average_precision_score(observed_labels, observed_probabilities)
        rows.append(
            {
                "model": model_name,
                "split": split_name,
                "task": task_name,
                "observed_labels": int(mask.sum()),
                "active_labels": int(np.nansum(observed_labels)),
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
            }
        )
    result = pd.DataFrame(rows)
    mean_row = {
        "model": model_name,
        "split": split_name,
        "task": "MEAN",
        "observed_labels": int(result["observed_labels"].sum()),
        "active_labels": int(result["active_labels"].sum()),
        "roc_auc": float(result["roc_auc"].mean()),
        "pr_auc": float(result["pr_auc"].mean()),
    }
    return pd.concat([result, pd.DataFrame([mean_row])], ignore_index=True)

