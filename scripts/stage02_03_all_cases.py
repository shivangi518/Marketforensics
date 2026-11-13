"""Stage 02 — Run detector + windows for all returns files; combine all_cases.csv."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.cases import build_windows, detect_big_moves
from marketforensics.config import CASES, NIFTY_INDEX, PROCESSED, ensure_data_dirs


def main() -> None:
    files = sorted(PROCESSED.glob("*_returns.csv"))
    if not files:
        raise SystemExit("No returns CSVs. Run Stage 01 first.")

    frames = []
    for path in files:
        ticker = path.name.replace("_returns.csv", "")
        if ticker == NIFTY_INDEX:
            continue
        try:
            detect_big_moves(ticker)
            build_windows(ticker)
            one = pd.read_csv(CASES / f"{ticker}_big_moves.csv", parse_dates=["Date"])
            one.insert(0, "ticker", ticker)
            frames.append(one)
            print(f"{ticker}: {len(one)} cases")
        except Exception as exc:
            print(f"skip {ticker}: {exc}")

    if not frames:
        raise SystemExit("No cases built.")
    ensure_data_dirs()
    all_cases = pd.concat(frames, ignore_index=True)
    out = CASES / "all_cases.csv"
    all_cases.to_csv(out, index=False)
    print(f"Combined {len(all_cases)} cases -> {out}")


if __name__ == "__main__":
    main()
