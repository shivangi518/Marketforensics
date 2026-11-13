"""Stage 01 — Download every ticker in universe.json plus the Nifty index."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import NIFTY_INDEX, RAW, START_DATE
from marketforensics.download import download_ticker

START = START_DATE


def main() -> None:
    uni_path = RAW / "universe.json"
    if not uni_path.exists():
        raise SystemExit("Run 04_ticker_universe.py first.")

    payload = json.loads(uni_path.read_text(encoding="utf-8"))
    tickers = list(payload["tickers"]) + [payload.get("benchmark", NIFTY_INDEX)]
    ok, failed = [], []
    for ticker in tickers:
        print(f"Downloading {ticker}...")
        try:
            path = download_ticker(ticker, start=START)
            print(f"  saved {path}")
            ok.append(ticker)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            failed.append({"ticker": ticker, "error": str(exc)})

    summary = RAW / "universe_download_log.json"
    summary.write_text(json.dumps({"ok": ok, "failed": failed}, indent=2), encoding="utf-8")
    print(f"Done. {len(ok)} ok, {len(failed)} failed. Log -> {summary}")


if __name__ == "__main__":
    main()
