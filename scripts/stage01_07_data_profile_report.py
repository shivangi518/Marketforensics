"""Stage 01 — Universe data-profile report (avg return, vol, best/worst, gaps)."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from marketforensics.config import PROCESSED, REPORTS, ensure_data_dirs
from marketforensics.io import close_column, load_prices


def profile_ticker(ticker: str) -> dict:
    prices = load_prices(ticker)
    close = close_column(prices)
    ret = prices[close].pct_change() * 100
    ret = ret.dropna()
    idx = prices.index
    gaps = int((idx.to_series().diff().dt.days.fillna(0) > 5).sum())
    return {
        "ticker": ticker,
        "rows": int(len(prices)),
        "first": str(idx.min().date()),
        "last": str(idx.max().date()),
        "avg_return_pct": round(float(ret.mean()), 4),
        "volatility_pct": round(float(ret.std()), 4),
        "best_day_pct": round(float(ret.max()), 4),
        "worst_day_pct": round(float(ret.min()), 4),
        "possible_gaps": gaps,
    }


def main() -> None:
    ensure_data_dirs()
    tickers = [p.stem.replace("_returns", "") for p in PROCESSED.glob("*_returns.csv")]
    if not tickers:
        # Fall back to any raw CSV that is not a log
        from marketforensics.config import RAW

        tickers = [p.stem for p in RAW.glob("*.csv")]
    if not tickers:
        raise SystemExit("No price/returns files yet. Download and compute returns first.")

    rows = []
    for ticker in sorted(set(tickers)):
        try:
            rows.append(profile_ticker(ticker))
        except Exception as exc:
            print(f"skip {ticker}: {exc}")

    ensure_data_dirs()
    out_md = REPORTS / "universe_profile.md"
    lines = [
        "# Universe profile",
        "",
        "| ticker | rows | first | last | avg ret % | vol % | best % | worst % | gaps |",
        "|--------|------|-------|------|-----------|-------|--------|---------|------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['ticker']} | {r['rows']} | {r['first']} | {r['last']} | "
            f"{r['avg_return_pct']} | {r['volatility_pct']} | {r['best_day_pct']} | "
            f"{r['worst_day_pct']} | {r['possible_gaps']} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(REPORTS / "universe_profile.csv", index=False)
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
