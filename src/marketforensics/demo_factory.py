"""Create a small realistic NSE demo bundle for Streamlit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


CAUSES = ["market_wide", "stock_specific", "volume_shock", "unknown"]
TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
INDEX = "^NSEI"


def _walk_prices(start: float, n: int, seed: int, vol: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0004, vol, n)
    shock_idx = [40, 55, 78, 96]
    for i, s in enumerate(shock_idx):
        rets[s] += (0.045 if i % 2 == 0 else -0.052) * (1 + 0.15 * (seed % 3))
    close = start * np.cumprod(1 + rets)
    volu = rng.integers(4_000_000, 18_000_000, n).astype(float)
    for s in shock_idx:
        volu[s] *= 2.4
    return close, volu


def _ohlcv(ticker: str, start_px: float, seed: int, vol: float) -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-02", periods=110)
    close, volume = _walk_prices(start_px, len(dates), seed, vol)
    high = close * 1.012
    low = close * 0.988
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame(
        {"Date": dates, "Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume}
    )


def write_demo_bundle(demo_root: Path) -> None:
    raw = demo_root / "raw"
    processed = demo_root / "processed"
    news = demo_root / "news"
    results = demo_root / "results"
    va, vb, vc = results / "version_a", results / "version_b", results / "version_c"
    for p in (raw, processed, news, va, vb, vc):
        p.mkdir(parents=True, exist_ok=True)

    frames = {
        "RELIANCE.NS": _ohlcv("RELIANCE.NS", 2400, 1, 0.012),
        "TCS.NS": _ohlcv("TCS.NS", 3600, 2, 0.010),
        "HDFCBANK.NS": _ohlcv("HDFCBANK.NS", 1450, 3, 0.011),
        INDEX: _ohlcv(INDEX, 22000, 9, 0.008),
    }
    for ticker, df in frames.items():
        df.to_csv(raw / f"{ticker}.csv", index=False)
        r = df.set_index("Date")["Close"].pct_change() * 100
        pd.DataFrame({"Date": df["Date"], "return_pct": r}).dropna().to_csv(
            processed / f"{ticker}_returns.csv", index=False
        )

    nifty = frames[INDEX].set_index("Date")["Close"]
    rows = []
    explanations: dict[str, list[str]] = {}
    for ticker in TICKERS:
        df = frames[ticker].set_index("Date")
        ret = df["Close"].pct_change() * 100
        vol = ret.rolling(20).std()
        big = ret.abs() >= 2.5 * vol
        events = ret[big.fillna(False)].dropna().tail(4)
        for ts, r in events.items():
            nifty_r = float(nifty.pct_change().loc[ts] * 100) if ts in nifty.index else 0.0
            v = df["Volume"]
            vratio = float(v.loc[ts] / v.rolling(20).mean().loc[ts])
            vs = float(r) - nifty_r
            if abs(nifty_r) >= 1.8:
                lab = "market_wide"
            elif abs(vs) >= 2.2:
                lab = "stock_specific"
            elif vratio >= 1.8:
                lab = "volume_shock"
            else:
                lab = "unknown"
            date = ts.strftime("%Y-%m-%d")
            mystery = float(np.clip(100 - min(92, abs(nifty_r) / max(abs(r), 0.01) * 55 + (vratio - 1) * 12), 12, 88))
            row = {
                "ticker": ticker,
                "date": date,
                "return_pct": float(r),
                "return_5d": float(df["Close"].pct_change(5).loc[ts] * 100),
                "vol_20": float(vol.loc[ts]),
                "volume_vs_avg20": vratio,
                "ma_20": float(df["Close"].rolling(20).mean().loc[ts]),
                "above_ma": int(df["Close"].loc[ts] > df["Close"].rolling(20).mean().loc[ts]),
                "momentum_5d": float(df["Close"].pct_change(5).loc[ts] * 100),
                "vs_nifty": vs,
                "nifty_return_pct": nifty_r,
                "dow": int(ts.dayofweek),
                "label": lab,
                "mystery_score": mystery,
            }
            rows.append(row)
            explanations[f"{ticker}|{date}"] = [
                f"volume vs 20d avg = {vratio:.2f}",
                f"vs Nifty % = {vs:.2f}",
                f"event return % = {float(r):.2f}",
            ]
            _write_agents(va, vb, vc, news, row)

    feat = pd.DataFrame(rows)
    feat.to_csv(demo_root / "case_features.csv", index=False)
    (demo_root / "sample_explanations.json").write_text(json.dumps(explanations, indent=2), encoding="utf-8")
    summary = {
        "n": int(len(feat)),
        "direction_match_21d": 0.54,
        "version_a_win_rate": 0.50,
        "version_b_win_rate": 0.56,
        "version_c_win_rate": 0.62,
        "note": "Demo backtest numbers for UI. Educational only — not a trading result.",
        "demo": True,
    }
    (demo_root / "backtest_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (demo_root / "README.txt").write_text(
        "Demo bundle for MarketForensics Streamlit. Clearly fictional paths around 2024.\n",
        encoding="utf-8",
    )


def _write_agents(va: Path, vb: Path, vc: Path, news: Path, row: dict) -> None:
    ticker, date = row["ticker"], row["date"]
    stem = f"{ticker}_{date}"
    cause = row["label"]
    direction = "up" if row["return_pct"] >= 0 else "down"
    conf_a = 64 if cause != "unknown" else 41
    a = {
        "version": "A",
        "ticker": ticker,
        "date": date,
        "raw": json.dumps(
            {
                "explanation": (
                    f"Solo agent: {ticker} moved {row['return_pct']:.2f}% on {date}. "
                    f"Volume was {row['volume_vs_avg20']:.2f}× the 20-day average and the stock "
                    f"beat/lagged Nifty by {row['vs_nifty']:.2f}%. Working cause: {cause}."
                ),
                "confidence": conf_a,
                "cause": cause,
                "direction": direction,
            }
        ),
    }
    (va / f"{stem}.json").write_text(json.dumps(a, indent=2), encoding="utf-8")
    opinions = {
        "numbers": json.dumps(
            {
                "explanation": f"Numbers desk: vol shock {row['volume_vs_avg20']:.2f}× and vs-Nifty {row['vs_nifty']:.2f}%.",
                "confidence": 70,
                "cause": cause,
                "direction": direction,
            }
        ),
        "news": json.dumps(
            {
                "explanation": "News desk: demo headlines only; do not treat as a complete clip file.",
                "confidence": 45,
                "cause": "unknown" if cause == "unknown" else cause,
                "direction": direction,
            }
        ),
        "skeptic": json.dumps(
            {
                "explanation": "Skeptic: weak labels and daily bars cannot prove a single cause.",
                "confidence": 38,
                "cause": "unknown",
                "direction": "unclear",
            }
        ),
    }
    (vb / f"{stem}.json").write_text(
        json.dumps({"version": "B", "vote": cause, "opinions": opinions, "ticker": ticker, "date": date}, indent=2),
        encoding="utf-8",
    )
    round1 = {
        "numbers": f"Round 1 numbers: {ticker} {row['return_pct']:+.2f}% vs Nifty {row['nifty_return_pct']:+.2f}%.",
        "news": "Round 1 news: only demo RSS-style titles exist; coverage may be missing.",
        "skeptic": "Round 1 skeptic: a 2.5σ rule is a detector, not an explanation.",
    }
    round2 = {
        "numbers": "Round 2 numbers: volume still supports a liquidity/attention spike.",
        "news": "Round 2 news: absence of a filing is not evidence of a clean story.",
        "skeptic": "Round 2 skeptic: keep mystery high until better labels exist.",
    }
    chair = json.dumps(
        {
            "explanation": (
                f"Chair report for {ticker} on {date}: the team leans {cause} "
                f"with mixed confidence. Mystery remains {row['mystery_score']:.0f}%."
            ),
            "confidence": 68,
            "cause": cause,
            "direction": direction,
            "mystery_comment": f"{row['mystery_score']:.0f}% of the move is still unexplained in this demo.",
        }
    )
    (vc / f"{stem}.json").write_text(
        json.dumps(
            {"version": "C", "round1": round1, "round2": round2, "chair": chair, "ticker": ticker, "date": date},
            indent=2,
        ),
        encoding="utf-8",
    )
    (news / f"{stem}.json").write_text(
        json.dumps(
            [
                {
                    "title": f"Demo: markets watch {ticker.replace('.NS', '')} after a sharp session",
                    "link": "",
                    "published": date,
                    "relevance": 0.7,
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
