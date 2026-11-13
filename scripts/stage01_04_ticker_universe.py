"""Stage 01 — Write the Nifty-style ticker universe to JSON."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import NIFTY_INDEX, RAW, UNIVERSE_LIMIT, ensure_data_dirs, universe_tickers


def main() -> None:
    ensure_data_dirs()
    tickers = universe_tickers()
    payload = {
        "benchmark": NIFTY_INDEX,
        "limit": UNIVERSE_LIMIT,
        "tickers": tickers,
        "count": len(tickers),
    }
    out = RAW / "universe.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(tickers)} tickers + benchmark {NIFTY_INDEX} -> {out}")


if __name__ == "__main__":
    main()
