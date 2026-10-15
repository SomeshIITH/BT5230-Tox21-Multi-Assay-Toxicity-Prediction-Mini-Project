from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create report-ready figures from saved metrics.")
    parser.add_argument("--split", choices=["scaffold", "random"], default="scaffold")
    arguments = parser.parse_args()

    result_directory = PROJECT_ROOT / "results"
    figure_directory = result_directory / "figures"
    figure_directory.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(result_directory / f"metrics_{arguments.split}.csv")
    task_metrics = metrics[metrics["task"] != "MEAN"].copy()

    sns.set_theme(style="whitegrid")
    figure, axis = plt.subplots(figsize=(11, 6))
    sns.barplot(data=task_metrics, x="task", y="roc_auc", hue="model", ax=axis)
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0.45, 1.0)
    plt.ylabel("ROC-AUC")
    plt.xlabel("Tox21 assay")
    plt.title(f"Per-assay test ROC-AUC ({arguments.split} split)")
    plt.tight_layout()
    figure.savefig(figure_directory / f"roc_auc_by_task_{arguments.split}.png", dpi=200)
    plt.close(figure)

    history = pd.read_csv(result_directory / f"training_history_{arguments.split}.csv")
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.plot(history["epoch"], history["training_loss"], label="Training masked BCE")
    second_axis = axis.twinx()
    second_axis.plot(history["epoch"], history["validation_mean_roc_auc"], color="#d95f02", label="Validation mean ROC-AUC")
    axis.set_xlabel("Epoch")
    axis.set_ylabel("Training loss")
    second_axis.set_ylabel("Validation mean ROC-AUC")
    axis.set_title("Training history")
    figure.tight_layout()
    figure.savefig(figure_directory / f"training_history_{arguments.split}.png", dpi=200)
    plt.close(figure)
    print(f"Saved figures to {figure_directory}")


if __name__ == "__main__":
    main()
