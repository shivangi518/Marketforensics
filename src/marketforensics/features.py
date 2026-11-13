"""Step 5: case clues using only rows on or before the event day."""

from __future__ import annotations

import numpy as np
import pandas as pd

from marketforensics.config import CASES, FEATURES, NIFTY_STEM, VOL_WINDOW, PipelineError, ensure_data_dirs
from marketforensics.data import load_processed


def _history_through(df: pd.DataFrame, day: pd.Timestamp) -> pd.DataFrame | None:
    hist = df.loc[df.index <= day]
    if hist.empty or hist.index.max() != day:
        return None
    return hist


def clues_for(ticker: str, day: pd.Timestamp, nifty: pd.DataFrame, stock: pd.DataFrame | None = None) -> dict | None:
    if stock is None:
        stock = load_processed(ticker)
    hist = _history_through(stock, day)
    nifty_hist = _history_through(nifty, day)
    if hist is None or nifty_hist is None or len(hist) < VOL_WINDOW + 1:
        return None
    close = hist["Close"].astype(float)
    ret = hist["return_pct"].astype(float)
    event_ret = float(ret.iloc[-1])
    if np.isnan(event_ret):
        return None
    vol20 = float(ret.rolling(VOL_WINDOW).std().iloc[-1])
    if np.isnan(vol20):
        return None
    ret_5 = float(close.iloc[-1] / close.iloc[-6] - 1.0) * 100 if len(close) >= 6 else np.nan
    if np.isnan(ret_5):
        return None
    ma = float(close.rolling(VOL_WINDOW).mean().iloc[-1])
    if "Volume" not in hist.columns:
        return None
    volume = hist["Volume"].astype(float)
    avg_vol = float(volume.iloc[-VOL_WINDOW:].mean())
    if not avg_vol or np.isnan(avg_vol):
        return None
    vol_ratio = float(volume.iloc[-1] / avg_vol)
    nifty_ret = float(nifty_hist["return_pct"].iloc[-1])
    if np.isnan(nifty_ret):
        return None
    return {
        "ticker": ticker,
        "date": day.strftime("%Y-%m-%d"),
        "return_pct": event_ret,
        "return_5d": ret_5,
        "vol_20": vol20,
        "volume_vs_avg20": vol_ratio,
        "ma_20": ma,
        "above_ma": int(close.iloc[-1] > ma),
        "momentum_5d": ret_5,
        "vs_nifty": event_ret - nifty_ret,
        "nifty_return_pct": nifty_ret,
        "dow": int(day.dayofweek),
    }


def run_features() -> dict:
    ensure_data_dirs()
    cases_path = CASES / "all_cases.csv"
    if not cases_path.exists():
        raise PipelineError(
            f"Missing {cases_path}\nCreate it with:\n  python run_pipeline.py --steps 3"
        )
    cases = pd.read_csv(cases_path)
    if cases.empty:
        raise PipelineError("all_cases.csv is empty. Re-run step 3.")
    nifty = load_processed(NIFTY_STEM)
    stocks: dict[str, pd.DataFrame] = {}
    rows = []
    skipped = 0
    for rec in cases.itertuples(index=False):
        ticker = str(rec.ticker)
        if ticker not in stocks:
            stocks[ticker] = load_processed(ticker)
        day = pd.Timestamp(rec.date)
        clue = clues_for(ticker, day, nifty, stocks[ticker])
        if clue is None:
            skipped += 1
            continue
        rows.append(clue)
    if not rows:
        raise PipelineError(
            "Every case was skipped (not enough history through the event day).\n"
            "Re-run:\n  python run_pipeline.py --steps 2-3"
        )
    out = FEATURES / "case_features.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(
        f"STEP 5 summary: rows in={len(cases)} cases, rows out={len(rows)} feature rows, skipped={skipped}"
    )
    return {
        "rows_in": int(len(cases)),
        "rows_out": len(rows),
        "files": [str(out)],
        "notes": f"skipped={skipped}",
    }
