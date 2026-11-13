"""Stage 01 — Clean raw CSVs: sort dates, drop duplicate days, drop empty rows."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import RAW, ensure_data_dirs
from marketforensics.io import close_column


def clean_one(path: Path) -> int:
    df = pd.read_csv(path, parse_dates=["Date"])
    before = len(df)
    df = df.dropna(how="all")
    df = df.drop_duplicates(subset=["Date"], keep="last")
    df = df.sort_values("Date")
    close = close_column(df.set_index("Date"))
    df = df.dropna(subset=[close] if close in df.columns else df.columns[:1])
    df.to_csv(path, index=False)
    return before - len(df)


def main() -> None:
    ensure_data_dirs()
    files = sorted(RAW.glob("*.csv"))
    if not files:
        raise SystemExit("No CSVs in data/raw. Download first.")
    for path in files:
        dropped = clean_one(path)
        print(f"{path.name}: dropped {dropped} duplicate/empty rows")


if __name__ == "__main__":
    main()
