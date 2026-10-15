from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "tox21.csv.gz"
PROCESSED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "tox21_clean.csv"
SPLIT_DIRECTORY = PROJECT_ROOT / "splits"
CHECKPOINT_DIRECTORY = PROJECT_ROOT / "checkpoints"
RESULT_DIRECTORY = PROJECT_ROOT / "results"

DATA_URL = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz"

TASK_NAMES = [
    "NR-AR",
    "NR-AR-LBD",
    "NR-AhR",
    "NR-Aromatase",
    "NR-ER",
    "NR-ER-LBD",
    "NR-PPAR-gamma",
    "SR-ARE",
    "SR-ATAD5",
    "SR-HSE",
    "SR-MMP",
    "SR-p53",
]

TASK_EXPLANATIONS = {
    "NR-AR": "Androgen receptor activity",
    "NR-AR-LBD": "Androgen receptor ligand-binding domain activity",
    "NR-AhR": "Aryl hydrocarbon receptor activity",
    "NR-Aromatase": "Aromatase activity",
    "NR-ER": "Estrogen receptor activity",
    "NR-ER-LBD": "Estrogen receptor ligand-binding domain activity",
    "NR-PPAR-gamma": "PPAR-gamma receptor activity",
    "SR-ARE": "Antioxidant response element pathway activity",
    "SR-ATAD5": "ATAD5 genotoxic stress response",
    "SR-HSE": "Heat-shock response element activity",
    "SR-MMP": "Mitochondrial membrane potential disruption",
    "SR-p53": "p53 stress response activity",
}

