from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DATA_FILE, RAW_DATA_FILE, RESULT_DIRECTORY, SPLIT_DIRECTORY
from src.data_pipeline import clean_tox21, random_split, save_splits, scaffold_split, verify_no_scaffold_leakage


def main() -> None:
    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError("Raw data is missing. Run: python scripts/download_data.py")

    clean_data = clean_tox21(
        RAW_DATA_FILE,
        PROCESSED_DATA_FILE,
        RESULT_DIRECTORY / "data_summary.json",
    )
    save_splits(clean_data, scaffold_split(clean_data, seed=42), SPLIT_DIRECTORY, "scaffold")
    save_splits(clean_data, random_split(clean_data, seed=42), SPLIT_DIRECTORY, "random")
    verify_no_scaffold_leakage(SPLIT_DIRECTORY)
    print(f"Prepared {len(clean_data)} unique valid molecules")
    print(f"Saved processed data to {PROCESSED_DATA_FILE}")
    print(f"Saved exact split files to {SPLIT_DIRECTORY}")


if __name__ == "__main__":
    main()
