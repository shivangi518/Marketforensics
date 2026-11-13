"""Daily percent returns from close."""

from __future__ import annotations

from marketforensics.config import ensure_data_dirs
from marketforensics.io import close_column, load_prices, returns_csv


def compute_returns(ticker: str) -> None:
    df = load_prices(ticker)
    close_col = close_column(df)
    df["return_pct"] = df[close_col].pct_change() * 100
    ensure_data_dirs()
    out_path = returns_csv(ticker)
    df[["return_pct"]].dropna().to_csv(out_path)
    print(f"{ticker}: saved {out_path} | up {df['return_pct'].max():.2f}% | down {df['return_pct'].min():.2f}%")
