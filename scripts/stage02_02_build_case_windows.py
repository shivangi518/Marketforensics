"""Stage 02 — Build before/after windows for each big-move case."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.cases import build_windows
from marketforensics.config import DEFAULT_TICKER

TICKER = DEFAULT_TICKER


def main() -> None:
    out = build_windows(TICKER)
    print(f"Built case windows -> {out}")
    df = pd.read_csv(out)
    print(f"{len(df)} rows")
    if not df.empty:
        print(df.tail())


if __name__ == "__main__":
    main()
