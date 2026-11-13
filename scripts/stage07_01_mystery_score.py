"""Stage 07 — Mystery score: how much of the move is still unexplained."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from marketforensics.config import FEATURES


def mystery_row(r: pd.Series) -> float:
    nifty = abs(float(r["nifty_return_pct"])) if pd.notna(r.get("nifty_return_pct")) else 0.0
    stock = abs(float(r["return_pct"])) if pd.notna(r.get("return_pct")) else 0.0
    volr = float(r["volume_vs_avg20"]) if pd.notna(r.get("volume_vs_avg20")) else 1.0
    market_part = min(nifty, stock)
    volume_part = max(0.0, min(stock * 0.25, (volr - 1) * 0.5 * stock)) if volr > 1 else 0.0
    explained = market_part + volume_part
    explained_pct = 0.0 if stock == 0 else min(100.0, 100.0 * explained / stock)
    return float(np.clip(100.0 - explained_pct, 0, 100))


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path)
    df["mystery_score"] = df.apply(mystery_row, axis=1)
    df["causal_note"] = df.apply(
        lambda r: (
            f"Likely {r.get('label', 'unknown')} because vs_nifty={r.get('vs_nifty')}; "
            f"{r['mystery_score']:.0f}% of the move remains unclear."
        ),
        axis=1,
    )
    df.to_csv(path, index=False)
    print(df[["ticker", "date", "mystery_score"]].head())
    print(f"Updated {path}")


if __name__ == "__main__":
    main()
