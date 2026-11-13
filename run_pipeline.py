"""Run MarketForensics steps in order. Each step reads the previous step's files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

from marketforensics.agents import run_step as step_agents
from marketforensics.backtest import run_backtest
from marketforensics.cases import run_cases
from marketforensics.config import PipelineError
from marketforensics.data import run_clean, run_download
from marketforensics.eda import run_eda
from marketforensics.features import run_features
from marketforensics.ml import run_ml

load_dotenv(ROOT / ".env")

NAMES = {
    1: "Download real prices",
    2: "Clean onto the Nifty calendar",
    3: "Find jump cases",
    4: "EDA charts and profile",
    5: "Build clues",
    6: "Random forest",
    7: "Groq agents",
    8: "Backtest and report",
}


def parse_steps(text: str) -> list[int]:
    text = text.strip()
    if "-" in text and "," not in text:
        start, end = text.split("-", 1)
        return list(range(int(start), int(end) + 1))
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="MarketForensics pipeline")
    parser.add_argument("--steps", help="Example: 1-6 or 7 or 8")
    parser.add_argument("--all", action="store_true", help="Run steps 1 through 8")
    parser.add_argument("--n", type=int, default=50, help="How many latest cases step 7 investigates")
    parser.add_argument("--ticker", default=None, help="With --date, investigate one case in step 7")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD")
    args = parser.parse_args()
    if args.all:
        steps = list(range(1, 9))
    elif args.steps:
        steps = parse_steps(args.steps)
    else:
        raise SystemExit("Pass --steps 1-6 or --all.\nExample:\n  python run_pipeline.py --steps 1-6")

    created: list[tuple[int, str]] = []
    for step in steps:
        if step not in NAMES:
            raise SystemExit(f"Unknown step {step}. Use 1-8.")
        print("=" * 64)
        print(f"STEP {step} — {NAMES[step]}")
        print("=" * 64)
        try:
            if step == 1:
                result = run_download()
            elif step == 2:
                result = run_clean()
            elif step == 3:
                result = run_cases()
            elif step == 4:
                result = run_eda()
            elif step == 5:
                result = run_features()
            elif step == 6:
                result = run_ml()
            elif step == 7:
                result = step_agents(n=args.n, ticker=args.ticker, date=args.date)
            else:
                result = run_backtest()
        except PipelineError as exc:
            print(exc)
            raise SystemExit(1) from exc
        for path in result.get("files", []):
            created.append((step, path))
            print(f"  file {path}")

    print("=" * 64)
    print("Files created this run")
    print("=" * 64)
    for step, path in created:
        print(f"  step {step}: {path}")


if __name__ == "__main__":
    main()
