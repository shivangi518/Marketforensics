"""Assemble JSON case files from features, labels, clues, and optional agents."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from marketforensics.config import (
    CASES_JSON,
    FEATURES,
    NEWS,
    RESULTS_A,
    RESULTS_B,
    RESULTS_C,
    ensure_data_dirs,
)


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main(limit: int = 20) -> None:
    ensure_data_dirs()
    feat_path = FEATURES / "case_features.csv"
    if not feat_path.exists():
        raise SystemExit("Missing data/features/case_features.csv. Run Stage 03 feature scripts first.")

    df = pd.read_csv(feat_path)
    if df.empty:
        raise SystemExit("case_features.csv is empty.")

    sample = df.head(limit)
    written = 0
    for _, row in sample.iterrows():
        ticker = str(row["ticker"])
        date = str(row["date"])
        stem = f"{ticker}_{date}"
        case = {
            "ticker": ticker,
            "date": date,
            "return_pct": float(row.get("return_pct", 0)),
            "features": {
                k: (None if pd.isna(row[k]) else row[k])
                for k in row.index
                if k not in {"ticker", "date"}
            },
            "ml_cause_guess": row.get("label") if "label" in row else None,
            "top_clues": [],
            "headlines": [],
            "mystery_score": None if "mystery_score" not in row or pd.isna(row.get("mystery_score")) else float(row["mystery_score"]),
            "agents": {
                "A": _load_json(RESULTS_A / f"{stem}.json"),
                "B": _load_json(RESULTS_B / f"{stem}.json"),
                "C": _load_json(RESULTS_C / f"{stem}.json"),
            },
        }
        clues_path = CASES_JSON.parent / "sample_explanations.json"
        if clues_path.exists():
            all_clues = json.loads(clues_path.read_text(encoding="utf-8"))
            key = f"{ticker}|{date}"
            if key in all_clues:
                case["top_clues"] = all_clues[key]

        news_path = NEWS / f"{stem}.json"
        if news_path.exists():
            case["headlines"] = json.loads(news_path.read_text(encoding="utf-8"))

        out = CASES_JSON / f"{stem}.json"
        out.write_text(json.dumps(case, indent=2, default=str), encoding="utf-8")
        written += 1

    print(f"Wrote {written} case JSON files -> {CASES_JSON}")


if __name__ == "__main__":
    main()
