"""Mystery score from the same-day Nifty move and volume clue. No future data."""

from __future__ import annotations

import math

import pandas as pd


def explained_and_mystery(return_pct: float, nifty_return_pct: float, volume_vs_avg20: float) -> tuple[float, float]:
    """Share of the absolute move accounted for by the index move and extra volume.

    market_part = min(|Nifty return|, |stock return|)
        The index can explain at most the smaller of the two moves (percentage points).

    volume_part = min(remaining, max(0, volume_ratio - 1) * 0.5 * |stock return|)
        Volume above its 20-day average explains up to half of what the index did not,
        scaled by how far above average volume was. A ratio of 1 adds nothing.

    explained_pct = 100 * (market_part + volume_part) / |stock return|, clipped to 0–100.
    mystery_score = 100 - explained_pct, clipped to 0–100.
    """
    stock = abs(float(return_pct))
    nifty = abs(float(nifty_return_pct)) if pd.notna(nifty_return_pct) else 0.0
    ratio = float(volume_vs_avg20) if pd.notna(volume_vs_avg20) else 1.0
    if stock == 0 or math.isnan(stock):
        return 0.0, 100.0
    market_part = min(nifty, stock)
    remaining = stock - market_part
    volume_part = min(remaining, max(0.0, ratio - 1.0) * 0.5 * stock)
    explained = max(0.0, min(100.0, 100.0 * (market_part + volume_part) / stock))
    mystery = max(0.0, min(100.0, 100.0 - explained))
    return explained, mystery
