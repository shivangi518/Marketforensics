"""Stage 03 — Feature clues for each case (no future leakage past event day)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from marketforensics.config import CASES, FEATURES, NIFTY_INDEX, VOL_WINDOW, ensure_data_dirs
from marketforensics.io import close_column, load_prices, volume_column


def _series_until(df: pd.DataFrame, event: pd.Timestamp) -> pd.DataFrame:
    return df.loc[df.index <= event]


def row_features(ticker: str, event: pd.Timestamp, stock_ret: float) -> dict | None:
    prices = _series_until(load_prices(ticker), event)
    if len(prices) < VOL_WINDOW + 6:
        return None
    close = close_column(prices)
    c = prices[close]
    rets = c.pct_change() * 100
    vol = rets.rolling(VOL_WINDOW).std()
    ma = c.rolling(VOL_WINDOW).mean()
    mom5 = (c.iloc[-1] / c.iloc[-6] - 1) * 100 if len(c) >= 6 else np.nan
    ret5 = (c.iloc[-1] / c.iloc[-6] - 1) * 100 if len(c) >= 6 else np.nan

    nifty_ret = np.nan
    try:
        nifty = _series_until(load_prices(NIFTY_INDEX), event)
        nc = nifty[close_column(nifty)]
        if len(nc) >= 2:
            nifty_ret = float(nc.pct_change().iloc[-1] * 100)
    except FileNotFoundError:
        pass

    vcol = volume_column(prices)
    vol_ratio = np.nan
    if vcol:
        v = prices[vcol]
        vol_ratio = float(v.iloc[-1] / v.rolling(VOL_WINDOW).mean().iloc[-1])

    return {
        "ticker": ticker,
        "date": event.date().isoformat(),
        "return_pct": float(stock_ret),
        "return_5d": float(ret5) if pd.notna(ret5) else np.nan,
        "vol_20": float(vol.iloc[-1]) if pd.notna(vol.iloc[-1]) else np.nan,
        "volume_vs_avg20": vol_ratio,
        "ma_20": float(ma.iloc[-1]) if pd.notna(ma.iloc[-1]) else np.nan,
        "above_ma": int(bool(c.iloc[-1] > ma.iloc[-1])) if pd.notna(ma.iloc[-1]) else np.nan,
        "momentum_5d": float(mom5) if pd.notna(mom5) else np.nan,
        "vs_nifty": float(stock_ret - nifty_ret) if pd.notna(nifty_ret) else np.nan,
        "nifty_return_pct": nifty_ret,
        "dow": int(event.dayofweek),
    }


def main() -> None:
    all_path = CASES / "all_cases.csv"
    singles = list(CASES.glob("*_big_moves.csv"))
    if all_path.exists():
        cases = pd.read_csv(all_path, parse_dates=["Date"])
    elif singles:
        parts = []
        for p in singles:
            df = pd.read_csv(p, parse_dates=["Date"])
            df["ticker"] = p.name.replace("_big_moves.csv", "")
            parts.append(df)
        cases = pd.concat(parts, ignore_index=True)
    else:
        raise SystemExit("No case files. Run Stage 02 first.")

    rows = []
    for _, rec in cases.iterrows():
        ticker = str(rec["ticker"])
        event = pd.Timestamp(rec["Date"])
        feat = row_features(ticker, event, float(rec["return_pct"]))
        if feat:
            rows.append(feat)

    ensure_data_dirs()
    out = FEATURES / "case_features.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} feature rows -> {out}")


if __name__ == "__main__":
    main()
