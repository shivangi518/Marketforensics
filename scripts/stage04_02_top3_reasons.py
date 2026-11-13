"""Stage 04 — Top-3 clues per sample case (permutation-style: largest |z| features)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json

import pandas as pd

from marketforensics.config import CASES, FEATURES, ensure_data_dirs

CLUE_COLS = [
    "return_pct",
    "volume_vs_avg20",
    "vs_nifty",
    "vol_20",
    "momentum_5d",
]


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path)
    sample = df.head(10)
    explanations = {}
    for _, row in sample.iterrows():
        scores = []
        for col in CLUE_COLS:
            val = row.get(col)
            if pd.isna(val):
                continue
            scores.append((col, float(val), abs(float(val))))
        scores.sort(key=lambda x: x[2], reverse=True)
        top = [f"{name}={value:.2f}" for name, value, _ in scores[:3]]
        explanations[f"{row['ticker']}|{row['date']}"] = top

    ensure_data_dirs()
    out = CASES / "sample_explanations.json"
    out.write_text(json.dumps(explanations, indent=2), encoding="utf-8")
    print(json.dumps(explanations, indent=2))
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
