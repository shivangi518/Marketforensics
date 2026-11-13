"""Download one ticker. File names match the pipeline (`NSEI.csv` for `^NSEI`)."""

from __future__ import annotations

from pathlib import Path

from marketforensics.config import START_DATE
from marketforensics.data import download_one


def download_ticker(ticker: str, start: str = START_DATE, end: str | None = None) -> Path:
    info = download_one(ticker, start=start, end=end)
    if info["error"]:
        raise RuntimeError(info["error"])
    return Path(info["file"])
