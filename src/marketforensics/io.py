"""Load and save project tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from marketforensics.config import CASES, PROCESSED, RAW, ticker_stem


def prices_csv(ticker: str) -> Path:
    return RAW / f"{ticker_stem(ticker)}.csv"


def returns_csv(ticker: str) -> Path:
    return PROCESSED / f"{ticker}_returns.csv"


def big_moves_csv(ticker: str) -> Path:
    return CASES / f"{ticker}_big_moves.csv"


def load_prices(ticker: str) -> pd.DataFrame:
    path = prices_csv(ticker)
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run stage01 download first.")
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def close_column(df: pd.DataFrame) -> str:
    if "Close" in df.columns:
        return "Close"
    matches = [c for c in df.columns if "close" in str(c).lower()]
    if matches:
        return matches[0]
    return str(df.columns[0])


def volume_column(df: pd.DataFrame) -> str | None:
    if "Volume" in df.columns:
        return "Volume"
    matches = [c for c in df.columns if "volume" in str(c).lower()]
    return matches[0] if matches else None
