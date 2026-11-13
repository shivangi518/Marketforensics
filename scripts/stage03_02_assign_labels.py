"""Stage 03 — Weak labels: market_wide / stock_specific / volume_shock / unknown."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import FEATURES


def label_row(r: pd.Series) -> str:
    nifty = r.get("nifty_return_pct")
    vs = r.get("vs_nifty")
    volr = r.get("volume_vs_avg20")
    if pd.notna(nifty) and abs(nifty) >= 2.0:
        return "market_wide"
    if pd.notna(vs) and abs(vs) >= 2.5:
        return "stock_specific"
    if pd.notna(volr) and volr >= 2.0:
        return "volume_shock"
    return "unknown"


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Run 01_build_features.py first.")
    df = pd.read_csv(path)
    df["label"] = df.apply(label_row, axis=1)
    df.to_csv(path, index=False)
    print(df["label"].value_counts().to_string())
    print(f"Updated {path}")


if __name__ == "__main__":
    main()
