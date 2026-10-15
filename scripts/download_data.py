from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DATA_URL, RAW_DATA_FILE


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the public MoleculeNet Tox21 CSV file.")
    parser.add_argument("--force", action="store_true", help="Download again if the file already exists.")
    arguments = parser.parse_args()

    RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if RAW_DATA_FILE.exists() and not arguments.force:
        print(f"Data already exists: {RAW_DATA_FILE}")
        return
    print(f"Downloading {DATA_URL}")
    urllib.request.urlretrieve(DATA_URL, RAW_DATA_FILE)
    print(f"Saved to {RAW_DATA_FILE}")


if __name__ == "__main__":
    main()
