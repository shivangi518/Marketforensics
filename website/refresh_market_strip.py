"""Refresh the real cross-market strip without slowing page requests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "market_strip.json"
SYMBOLS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "BTC": "BTC-USD",
}


def main() -> None:
    rows = []
    for name, symbol in SYMBOLS.items():
        try:
            frame = yf.Ticker(symbol).history(period="7d", interval="1d", auto_adjust=True)
            closes = frame["Close"].dropna()
            if len(closes) < 2:
                continue
            last = float(closes.iloc[-1])
            prior = float(closes.iloc[-2])
            rows.append(
                {
                    "ticker": name,
                    "symbol": symbol,
                    "close": last,
                    "change": (last / prior - 1) * 100,
                    "date": str(closes.index[-1].date()),
                }
            )
        except Exception as exc:
            print(f"skip {name}: {exc}")
    OUTPUT.write_text(
        json.dumps(
            {"updated_at_utc": datetime.now(timezone.utc).isoformat(), "items": rows},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT} ({len(rows)} markets)")


if __name__ == "__main__":
    main()
