import unittest

import numpy as np
import pandas as pd

from src.chemistry import canonicalize_smiles
from src.data_pipeline import random_split, scaffold_split
from src.model import masked_binary_cross_entropy


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "scaffold": ["a", "a", "b", "b", "c", "c", "d", "d", "e", "e"],
                "compound_id": [str(index) for index in range(10)],
            }
        )

    def test_random_split_contains_every_row_once(self):
        split = random_split(self.data, seed=42)
        combined = np.concatenate(list(split.values()))
        self.assertEqual(sorted(combined.tolist()), list(range(10)))

    def test_scaffold_groups_do_not_overlap(self):
        split = scaffold_split(self.data, seed=42)
        combined = np.concatenate(list(split.values()))
        self.assertEqual(sorted(combined.tolist()), list(range(10)))
        self.assertEqual(len(combined), len(set(combined.tolist())))
        scaffold_sets = {
            name: set(self.data.iloc[indices]["scaffold"])
            for name, indices in split.items()
        }
        self.assertFalse(scaffold_sets["train"] & scaffold_sets["validation"])
        self.assertFalse(scaffold_sets["train"] & scaffold_sets["test"])
        self.assertFalse(scaffold_sets["validation"] & scaffold_sets["test"])


class LossTests(unittest.TestCase):
    def test_missing_labels_do_not_change_loss(self):
        import torch

        logits = torch.tensor([[0.0, 100.0]])
        labels = torch.tensor([[1.0, float("nan")]])
        mask = torch.tensor([[1.0, 0.0]])
        weights = torch.ones(2)
        loss = masked_binary_cross_entropy(logits, labels, mask, weights)
        self.assertAlmostEqual(float(loss), 0.693147, places=5)


class ChemistryTests(unittest.TestCase):
    def test_canonicalization_and_invalid_input(self):
        self.assertEqual(canonicalize_smiles(" C(C)O "), "CCO")
        self.assertIsNone(canonicalize_smiles("not-a-smiles"))
        self.assertIsNone(canonicalize_smiles(""))


if __name__ == "__main__":
    unittest.main()
