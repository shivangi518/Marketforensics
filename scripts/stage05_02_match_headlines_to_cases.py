"""Stage 05 — Attach headlines to the first 50 cases (keyword / ticker match)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import DEFAULT_TICKER, FEATURES, NEWS, ensure_data_dirs


def main() -> None:
    feat = FEATURES / "case_features.csv"
    if not feat.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(feat).head(50)
    pool_path = NEWS / f"{DEFAULT_TICKER}_headlines.json"
    headlines = json.loads(pool_path.read_text(encoding="utf-8")) if pool_path.exists() else []

    ensure_data_dirs()
    for _, row in df.iterrows():
        ticker = str(row["ticker"])
        date = str(row["date"])
        name = ticker.replace(".NS", "").lower()
        matched = []
        for h in headlines:
            title = (h.get("title") or "").lower()
            score = 1.0 if name in title or "reliance" in title else 0.2
            if score >= 0.2:
                matched.append({**h, "relevance": score})
        out = NEWS / f"{ticker}_{date}.json"
        out.write_text(json.dumps(matched[:5], indent=2), encoding="utf-8")
    print(f"Wrote headline files for {len(df)} cases in {NEWS}")


if __name__ == "__main__":
    main()
