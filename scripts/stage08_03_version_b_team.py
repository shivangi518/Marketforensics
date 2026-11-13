"""Stage 08 — Version B: three personas vote, no debate."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import AGENT_CACHE, FEATURES, RESULTS_B, ensure_data_dirs
from marketforensics.llm import chat

PERSONAS = {
    "numbers": "You are a numbers analyst. Use volume, volatility, and vs-Nifty clues only. JSON: explanation, confidence, cause, direction.",
    "news": "You are a news analyst. If headlines are missing, say so. JSON: explanation, confidence, cause, direction.",
    "skeptic": "You are a risk skeptic. Challenge overconfidence. JSON: explanation, confidence, cause, direction.",
}


def parse_cause(text: str) -> str:
    try:
        data = json.loads(text)
        return str(data.get("cause", "unknown"))
    except json.JSONDecodeError:
        for key in ("market_wide", "stock_specific", "volume_shock", "unknown"):
            if key in text:
                return key
        return "unknown"


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path).head(50)
    ensure_data_dirs()
    for _, row in df.iterrows():
        stem = f"{row['ticker']}_{row['date']}"
        user = json.dumps(row.to_dict(), default=str)
        opinions = {}
        for name, system in PERSONAS.items():
            cache = AGENT_CACHE / f"B_{name}_{stem}.txt"
            if cache.exists():
                text = cache.read_text(encoding="utf-8")
            else:
                text = chat(system, user)
                cache.write_text(text, encoding="utf-8")
            opinions[name] = text
        causes = [parse_cause(t) for t in opinions.values()]
        vote = Counter(causes).most_common(1)[0][0]
        out = RESULTS_B / f"{stem}.json"
        out.write_text(
            json.dumps({"version": "B", "vote": vote, "opinions": opinions, "ticker": row["ticker"], "date": str(row["date"])}, indent=2),
            encoding="utf-8",
        )
        print(f"B {stem} vote={vote}")
    print(f"Saved Version B -> {RESULTS_B}")


if __name__ == "__main__":
    main()
