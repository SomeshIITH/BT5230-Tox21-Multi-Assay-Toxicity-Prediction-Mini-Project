from __future__ import annotations

import torch
from torch import nn


class MultiTaskToxicityModel(nn.Module):
    def __init__(self, input_size: int, task_count: int, hidden_size: int = 256, dropout: float = 0.25):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_size),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, task_count),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features)


def masked_binary_cross_entropy(
    logits: torch.Tensor,
    labels: torch.Tensor,
    label_mask: torch.Tensor,
    positive_weights: torch.Tensor,
) -> torch.Tensor:
    safe_labels = torch.nan_to_num(labels, nan=0.0)
    loss_function = nn.BCEWithLogitsLoss(pos_weight=positive_weights, reduction="none")
    element_loss = loss_function(logits, safe_labels)
    masked_loss = element_loss * label_mask
    return masked_loss.sum() / label_mask.sum().clamp_min(1.0)

