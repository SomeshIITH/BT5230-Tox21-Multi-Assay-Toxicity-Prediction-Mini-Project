from __future__ import annotations

import numpy as np
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, Lipinski, rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold


FINGERPRINT_RADIUS = 2
FINGERPRINT_BITS = 2048
DESCRIPTOR_NAMES = [
    "molecular_weight",
    "logp",
    "tpsa",
    "h_bond_donors",
    "h_bond_acceptors",
    "rotatable_bonds",
    "ring_count",
    "heavy_atom_count",
]

_fingerprint_generator = rdFingerprintGenerator.GetMorganGenerator(
    radius=FINGERPRINT_RADIUS,
    fpSize=FINGERPRINT_BITS,
)


def molecule_from_smiles(smiles: str):
    if not isinstance(smiles, str) or not smiles.strip():
        return None
    return Chem.MolFromSmiles(smiles.strip())


def canonicalize_smiles(smiles: str) -> str | None:
    molecule = molecule_from_smiles(smiles)
    if molecule is None:
        return None
    return Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)


def murcko_scaffold(smiles: str) -> str:
    molecule = molecule_from_smiles(smiles)
    if molecule is None:
        return ""
    return MurckoScaffold.MurckoScaffoldSmiles(mol=molecule, includeChirality=False)


def fingerprint(smiles: str) -> np.ndarray:
    molecule = molecule_from_smiles(smiles)
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    bit_vector = _fingerprint_generator.GetFingerprint(molecule)
    output = np.zeros((FINGERPRINT_BITS,), dtype=np.float32)
    DataStructs.ConvertToNumpyArray(bit_vector, output)
    return output


def molecular_descriptors(smiles: str) -> np.ndarray:
    molecule = molecule_from_smiles(smiles)
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return np.asarray(
        [
            Descriptors.MolWt(molecule),
            Descriptors.MolLogP(molecule),
            Descriptors.TPSA(molecule),
            Lipinski.NumHDonors(molecule),
            Lipinski.NumHAcceptors(molecule),
            Lipinski.NumRotatableBonds(molecule),
            Lipinski.RingCount(molecule),
            Lipinski.HeavyAtomCount(molecule),
        ],
        dtype=np.float32,
    )


def featurize_smiles(smiles: list[str]) -> tuple[np.ndarray, np.ndarray]:
    fingerprints = np.stack([fingerprint(value) for value in smiles])
    descriptors = np.stack([molecular_descriptors(value) for value in smiles])
    return fingerprints, descriptors


def tanimoto_similarity(query_smiles: str, reference_fingerprints: np.ndarray) -> np.ndarray:
    query = fingerprint(query_smiles).astype(bool)
    references = reference_fingerprints.astype(bool)
    intersection = np.logical_and(references, query).sum(axis=1)
    union = np.logical_or(references, query).sum(axis=1)
    return np.divide(intersection, union, out=np.zeros_like(intersection, dtype=float), where=union > 0)

