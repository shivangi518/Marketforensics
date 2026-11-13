"""Stage 08 — Version A: one solo agent reads clues and explains the move."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import AGENT_CACHE, FEATURES, RESULTS_A, ensure_data_dirs
from marketforensics.llm import chat

SYSTEM = (
    "You explain Indian stock jumps using only the numeric clues given. "
    "Reply as JSON with keys explanation, confidence (0-100), cause "
    "(market_wide|stock_specific|volume_shock|unknown), direction (up|down|unclear)."
)


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path).head(50)
    ensure_data_dirs()
    for _, row in df.iterrows():
        stem = f"{row['ticker']}_{row['date']}"
        user = json.dumps(row.to_dict(), default=str)
        cache = AGENT_CACHE / f"A_{stem}.txt"
        if cache.exists():
            text = cache.read_text(encoding="utf-8")
        else:
            text = chat(SYSTEM, user)
            cache.write_text(text, encoding="utf-8")
        out = RESULTS_A / f"{stem}.json"
        out.write_text(
            json.dumps({"version": "A", "raw": text, "ticker": row["ticker"], "date": str(row["date"])}, indent=2),
            encoding="utf-8",
        )
        print(f"A {stem}")
    print(f"Saved Version A -> {RESULTS_A}")


if __name__ == "__main__":
    main()
