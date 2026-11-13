"""Stage 02 — Detect big-move days using volatility scaling."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.cases import detect_big_moves
from marketforensics.config import DEFAULT_TICKER
from marketforensics.io import big_moves_csv

TICKER = DEFAULT_TICKER


def main() -> None:
    out_path = detect_big_moves(TICKER)
    cases = pd.read_csv(out_path, parse_dates=["Date"], index_col="Date")
    print(f"Found {len(cases)} big-move days for {TICKER}")
    print(cases[["return_pct", "threshold"]].tail(10))
    print(f"Saved -> {big_moves_csv(TICKER)}")


if __name__ == "__main__":
    main()
