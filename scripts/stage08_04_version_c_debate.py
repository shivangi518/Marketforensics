"""Stage 08 — Version C: independent round, rebuttals, then chair report."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import AGENT_CACHE, FEATURES, RESULTS_C, ensure_data_dirs
from marketforensics.llm import chat

PERSONAS = {
    "numbers": "Numbers analyst. JSON: explanation, confidence, cause, direction.",
    "news": "News analyst. JSON: explanation, confidence, cause, direction.",
    "skeptic": "Skeptic. JSON: explanation, confidence, cause, direction.",
}
CHAIR = (
    "You are the chair. Read the three opinions and rebuttals. "
    "Write a final case report JSON with explanation, confidence, cause, direction, mystery_comment."
)


def cached_chat(cache: Path, system: str, user: str) -> str:
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    text = chat(system, user)
    cache.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path).head(50)
    ensure_data_dirs()
    for _, row in df.iterrows():
        stem = f"{row['ticker']}_{row['date']}"
        clues = json.dumps(row.to_dict(), default=str)
        round1 = {
            name: cached_chat(AGENT_CACHE / f"C1_{name}_{stem}.txt", system, clues)
            for name, system in PERSONAS.items()
        }
        others = json.dumps(round1, indent=2)
        round2 = {
            name: cached_chat(
                AGENT_CACHE / f"C2_{name}_{stem}.txt",
                f"{system} Now rebut the others briefly.",
                others,
            )
            for name, system in PERSONAS.items()
        }
        chair = cached_chat(
            AGENT_CACHE / f"C_chair_{stem}.txt",
            CHAIR,
            json.dumps({"round1": round1, "round2": round2}, indent=2),
        )
        out = RESULTS_C / f"{stem}.json"
        out.write_text(
            json.dumps(
                {
                    "version": "C",
                    "round1": round1,
                    "round2": round2,
                    "chair": chair,
                    "ticker": row["ticker"],
                    "date": str(row["date"]),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"C {stem}")
    print(f"Saved Version C -> {RESULTS_C}")


if __name__ == "__main__":
    main()
