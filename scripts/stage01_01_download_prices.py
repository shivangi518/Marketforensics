"""Stage 01 — Download real stock prices (NSE via Yahoo Finance).

Saves CSV + metadata JSON under data/raw/.
Default ticker: RELIANCE.NS (change TICKER below to try others).
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import DEFAULT_TICKER, START_DATE
from marketforensics.download import download_ticker

TICKER = DEFAULT_TICKER
START = START_DATE
END = None


def main() -> None:
    print("=" * 60)
    print("MarketForensics — Stage 01 data download")
    print("=" * 60)
    print(f"Ticker : {TICKER}")
    print(f"Start  : {START}")
    print(f"End    : {END or 'today (latest available)'}")
    print("Source : Yahoo Finance via yfinance")
    print()

    out_path = download_ticker(TICKER, start=START, end=END)
    meta_path = out_path.with_name(f"{TICKER}_meta.json")
    print("SUCCESS")
    print(f"  CSV      : {out_path}")
    print(f"  Metadata : {meta_path}")
    print()
    print("Next:")
    print("  python scripts/stage01_02_plot_close.py")
    print("  python scripts/stage01_03_compute_returns.py")


if __name__ == "__main__":
    main()
