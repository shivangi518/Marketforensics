"""Robust loaders for the Streamlit app: live files, derived cases, or demo."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from marketforensics.config import (
    CASES,
    CASES_JSON,
    FEATURES,
    NIFTY_INDEX,
    RAW,
    REPORTS,
    RESULTS,
    RESULTS_A,
    RESULTS_B,
    RESULTS_C,
    ROOT,
    VOL_WINDOW,
    ensure_data_dirs,
)

DEMO = ROOT / "data" / "demo"

TICKER_ALIASES = ("ticker", "Ticker", "symbol", "Symbol")
DATE_ALIASES = ("date", "Date", "event_date", "eventDate")
RETURN_ALIASES = ("return_pct", "event_return_pct", "return", "ret_pct")
LABEL_ALIASES = ("label", "ml_cause_guess", "cause", "ml_cause")
MYSTERY_ALIASES = ("mystery_score", "mystery", "mysteryScore")


def date_key(value: Any) -> str:
    ts = pd.to_datetime(value, errors="coerce", utc=False)
    if pd.isna(ts):
        text = str(value).strip()
        return text[:10] if len(text) >= 10 else text
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def case_stem(ticker: str, date_val: Any) -> str:
    return f"{ticker}_{date_key(date_val)}"


def _pick_col(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    lower = {str(c).lower(): c for c in df.columns}
    for name in aliases:
        if name in df.columns:
            return name
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def normalize_cases(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    tcol = _pick_col(out, TICKER_ALIASES)
    dcol = _pick_col(out, DATE_ALIASES)
    rcol = _pick_col(out, RETURN_ALIASES)
    lcol = _pick_col(out, LABEL_ALIASES)
    mcol = _pick_col(out, MYSTERY_ALIASES)
    if tcol is None or dcol is None:
        return pd.DataFrame()
    out["ticker"] = out[tcol].astype(str).str.strip()
    out["date"] = out[dcol].map(date_key)
    if rcol is not None:
        out["return_pct"] = pd.to_numeric(out[rcol], errors="coerce")
    else:
        out["return_pct"] = np.nan
    if lcol is not None:
        out["label"] = out[lcol].astype(str)
    elif "label" not in out.columns:
        out["label"] = "unknown"
    if mcol is not None:
        out["mystery_score"] = pd.to_numeric(out[mcol], errors="coerce")
    elif "mystery_score" not in out.columns:
        out["mystery_score"] = np.nan
    out = out.dropna(subset=["ticker", "date"])
    out = out[out["ticker"].str.len() > 0]
    return out.reset_index(drop=True)


def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists() or path.stat().st_size < 8:
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def close_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if str(c).lower() == "close":
            return str(c)
    for c in df.columns:
        if "close" in str(c).lower():
            return str(c)
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    return str(numeric[0]) if numeric else None


def volume_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "volume" in str(c).lower():
            return str(c)
    return None


def load_ohlcv(ticker: str) -> pd.DataFrame | None:
    """Load prices from live raw, then demo raw. Index = Date."""
    candidates = [
        RAW / f"{ticker}.csv",
        DEMO / "raw" / f"{ticker}.csv",
    ]
    for path in candidates:
        df = _read_csv(path)
        if df is None or df.empty:
            continue
        date_c = _pick_col(df, ("Date", "date", "datetime"))
        if date_c is None:
            continue
        df[date_c] = pd.to_datetime(df[date_c], errors="coerce")
        df = df.dropna(subset=[date_c]).sort_values(date_c)
        df = df.set_index(date_c)
        df.index.name = "Date"
        cc = close_col(df)
        if cc is None:
            continue
        keep = [cc]
        vc = volume_col(df)
        if vc:
            keep.append(vc)
        slim = df[keep].copy()
        slim = slim.rename(columns={cc: "Close"})
        if vc:
            slim = slim.rename(columns={vc: "Volume"})
        return slim[~slim.index.duplicated(keep="last")]
    return None


def _label_from_clues(ret: float, vs_nifty: float, vol_ratio: float, nifty_ret: float) -> str:
    if abs(nifty_ret) >= 2.0:
        return "market_wide"
    if abs(vs_nifty) >= 2.5:
        return "stock_specific"
    if vol_ratio >= 2.0:
        return "volume_shock"
    return "unknown"


def _mystery(ret: float, nifty_ret: float, vol_ratio: float) -> float:
    stock = abs(ret)
    if stock == 0:
        return 50.0
    explained = min(abs(nifty_ret), stock) + max(0.0, (vol_ratio - 1) * 0.35 * stock)
    pct = min(100.0, 100.0 * explained / stock)
    return float(np.clip(100.0 - pct, 8, 92))


def derive_cases_from_raw(limit: int = 12) -> pd.DataFrame | None:
    files = [p for p in RAW.glob("*.csv") if "universe" not in p.name.lower()]
    if not files:
        return None
    nifty = load_ohlcv(NIFTY_INDEX)
    rows: list[dict[str, Any]] = []
    for path in files:
        ticker = path.stem
        if ticker.startswith("^") and ticker != NIFTY_INDEX:
            continue
        prices = load_ohlcv(ticker)
        if prices is None or "Close" not in prices.columns or len(prices) < VOL_WINDOW + 6:
            continue
        close = prices["Close"].astype(float)
        ret = close.pct_change() * 100
        vol = ret.rolling(VOL_WINDOW).std()
        big = ret.abs() >= (2.5 * vol)
        events = ret[big.fillna(False)].dropna()
        if events.empty:
            continue
        events = events.tail(max(3, limit // max(1, len(files))))
        for ts, r in events.items():
            window = prices.loc[:ts]
            if len(window) < VOL_WINDOW + 2:
                continue
            r = float(r)
            vol20 = float(vol.loc[ts]) if ts in vol.index and pd.notna(vol.loc[ts]) else float("nan")
            vol_ratio = float("nan")
            if "Volume" in window.columns:
                v = window["Volume"].astype(float)
                avg = v.rolling(VOL_WINDOW).mean()
                if pd.notna(avg.iloc[-1]) and avg.iloc[-1]:
                    vol_ratio = float(v.iloc[-1] / avg.iloc[-1])
            nifty_ret = 0.0
            if nifty is not None and ts in nifty.index:
                nr = nifty["Close"].astype(float).pct_change() * 100
                if ts in nr.index and pd.notna(nr.loc[ts]):
                    nifty_ret = float(nr.loc[ts])
            vs = r - nifty_ret
            ma = window["Close"].rolling(VOL_WINDOW).mean().iloc[-1]
            above = int(bool(window["Close"].iloc[-1] > ma)) if pd.notna(ma) else 0
            mom = float("nan")
            if len(window) >= 6:
                mom = float((window["Close"].iloc[-1] / window["Close"].iloc[-6] - 1) * 100)
            lab = _label_from_clues(r, vs, vol_ratio if pd.notna(vol_ratio) else 1.0, nifty_ret)
            rows.append(
                {
                    "ticker": ticker,
                    "date": date_key(ts),
                    "return_pct": r,
                    "return_5d": mom,
                    "vol_20": vol20,
                    "volume_vs_avg20": vol_ratio,
                    "ma_20": float(ma) if pd.notna(ma) else np.nan,
                    "above_ma": above,
                    "momentum_5d": mom,
                    "vs_nifty": vs,
                    "nifty_return_pct": nifty_ret,
                    "dow": int(pd.Timestamp(ts).dayofweek),
                    "label": lab,
                    "mystery_score": _mystery(r, nifty_ret, vol_ratio if pd.notna(vol_ratio) else 1.0),
                }
            )
    if not rows:
        return None
    df = pd.DataFrame(rows).drop_duplicates(subset=["ticker", "date"])
    return df.sort_values(["date", "ticker"]).tail(limit).reset_index(drop=True)


def _parse_model_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


def normalize_agent_a(payload: Any, row: pd.Series) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if isinstance(payload, dict):
        if "raw" in payload and isinstance(payload["raw"], str):
            data = _parse_model_json(payload["raw"])
        else:
            data = dict(payload)
    ret = float(row.get("return_pct") or 0)
    cause = str(data.get("cause") or row.get("label") or "unknown")
    conf = data.get("confidence", 58)
    try:
        conf = int(float(conf))
    except (TypeError, ValueError):
        conf = 58
    direction = str(data.get("direction") or ("up" if ret >= 0 else "down"))
    explanation = str(
        data.get("explanation")
        or data.get("text")
        or f"Solo read of clues for {row.get('ticker')} on {row.get('date')}: labelled {cause}."
    )
    return {
        "version": "A",
        "explanation": explanation,
        "confidence": int(np.clip(conf, 0, 100)),
        "cause": cause,
        "direction": direction,
    }


def normalize_agent_b(payload: Any, row: pd.Series) -> dict[str, Any]:
    opinions: dict[str, str] = {}
    vote = str(row.get("label") or "unknown")
    if isinstance(payload, dict):
        vote = str(payload.get("vote") or vote)
        raw_op = payload.get("opinions") or {}
        if isinstance(raw_op, dict):
            for k, v in raw_op.items():
                if isinstance(v, dict):
                    opinions[str(k)] = str(v.get("explanation") or json.dumps(v))
                else:
                    parsed = _parse_model_json(str(v))
                    opinions[str(k)] = str(parsed.get("explanation") or v)
    if not opinions:
        cause = str(row.get("label") or "unknown")
        opinions = {
            "numbers": f"Volume and vs-Nifty clues lean {cause}.",
            "news": "No strong headline set in this file; treat news as incomplete.",
            "skeptic": "Labels are weak. Do not over-claim a single cause.",
        }
    return {
        "version": "B",
        "vote": vote,
        "opinions": opinions,
        "confidence": 62,
        "direction": "up" if float(row.get("return_pct") or 0) >= 0 else "down",
        "cause": vote,
    }


def normalize_agent_c(payload: Any, row: pd.Series) -> dict[str, Any]:
    round1 = {"numbers": "", "news": "", "skeptic": ""}
    round2 = {"numbers": "", "news": "", "skeptic": ""}
    chair = ""
    if isinstance(payload, dict):
        r1 = payload.get("round1") or {}
        r2 = payload.get("round2") or {}
        if isinstance(r1, dict):
            round1 = {str(k): str(v) for k, v in r1.items()}
        if isinstance(r2, dict):
            round2 = {str(k): str(v) for k, v in r2.items()}
        chair_raw = payload.get("chair")
        if isinstance(chair_raw, dict):
            chair = str(chair_raw.get("explanation") or json.dumps(chair_raw))
        elif chair_raw:
            parsed = _parse_model_json(str(chair_raw))
            chair = str(parsed.get("explanation") or chair_raw)
    if not any(round1.values()):
        ticker, date = row.get("ticker"), row.get("date")
        round1 = {
            "numbers": f"Numbers: {ticker} moved {row.get('return_pct'):.2f}% vs Nifty on {date}.",
            "news": "News: headlines are thin; do not treat silence as proof.",
            "skeptic": "Skeptic: the label is a rule of thumb, not ground truth.",
        }
        round2 = {
            "numbers": "Rebuttal: volume still matters even if news is missing.",
            "news": "Rebuttal: a missing headline is not the same as no news.",
            "skeptic": "Rebuttal: mystery score should stay high if clues conflict.",
        }
        chair = (
            f"Chair: mixed evidence for {ticker} on {date}. "
            f"Working cause {row.get('label')}; keep the mystery score honest."
        )
    parsed_chair = _parse_model_json(chair)
    return {
        "version": "C",
        "round1": round1,
        "round2": round2,
        "chair": chair,
        "cause": parsed_chair.get("cause") or row.get("label") or "unknown",
        "confidence": int(parsed_chair.get("confidence") or 70),
        "direction": parsed_chair.get("direction") or ("up" if float(row.get("return_pct") or 0) >= 0 else "down"),
    }


def load_agent_payload(version: str, ticker: str, date_val: Any) -> Any:
    stem = case_stem(ticker, date_val)
    folders = {
        "A": [RESULTS_A, DEMO / "results" / "version_a"],
        "B": [RESULTS_B, DEMO / "results" / "version_b"],
        "C": [RESULTS_C, DEMO / "results" / "version_c"],
    }
    for folder in folders[version]:
        payload = _read_json(folder / f"{stem}.json")
        if payload is not None:
            return payload
    return None


def top_clues_for(row: pd.Series) -> list[str]:
    blob = _read_json(CASES / "sample_explanations.json") or _read_json(DEMO / "sample_explanations.json") or {}
    key = f"{row.get('ticker')}|{row.get('date')}"
    if isinstance(blob, dict) and key in blob and isinstance(blob[key], list):
        return [str(x) for x in blob[key][:3]]
    case_json = _read_json(CASES_JSON / f"{case_stem(str(row.get('ticker')), row.get('date'))}.json")
    if isinstance(case_json, dict) and case_json.get("top_clues"):
        return [str(x) for x in case_json["top_clues"][:3]]
    built = []
    mapping = [
        ("volume_vs_avg20", "volume vs 20d avg"),
        ("vs_nifty", "vs Nifty %"),
        ("vol_20", "20d volatility"),
        ("momentum_5d", "5d momentum"),
        ("return_pct", "event return %"),
    ]
    scored = []
    for col, label in mapping:
        val = row.get(col)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            continue
        try:
            scored.append((abs(float(val)), f"{label} = {float(val):.2f}"))
        except (TypeError, ValueError):
            continue
    scored.sort(reverse=True)
    built = [s[1] for s in scored[:3]]
    return built or ["Clues incomplete for this case"]


def headlines_for(row: pd.Series) -> list[dict[str, Any]]:
    stem = case_stem(str(row.get("ticker")), row.get("date"))
    for path in (
        ROOT / "data" / "news" / f"{stem}.json",
        DEMO / "news" / f"{stem}.json",
    ):
        data = _read_json(path)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)][:5]
    return []


def backtest_payload(allow_demo: bool = True) -> dict[str, Any]:
    live = _read_json(RESULTS / "backtest_summary.json") or {}
    if isinstance(live, dict) and live:
        return live
    if allow_demo:
        demo = _read_json(DEMO / "backtest_summary.json") or {}
        return demo if isinstance(demo, dict) else {}
    return {}


def load_workspace() -> dict[str, Any]:
    """Returns cases dataframe, source label, and whether it is demo."""
    ensure_data_dirs()
    live = _read_csv(FEATURES / "case_features.csv")
    if live is not None:
        cases = normalize_cases(live)
        if not cases.empty:
            return {"cases": cases, "source": "live", "demo": False, "banner": None}

    derived = derive_cases_from_raw()
    if derived is not None and not derived.empty:
        return {
            "cases": derived,
            "source": "derived",
            "demo": False,
            "banner": "Cases were built from your downloaded price files (big-move rule). Run Stage 03 scripts later for the full feature table.",
        }

    demo_feat = _read_csv(DEMO / "case_features.csv")
    if demo_feat is not None:
        cases = normalize_cases(demo_feat)
        if not cases.empty:
            return {
                "cases": cases,
                "source": "demo",
                "demo": True,
                "banner": "Demo data — labelled as such. Run make_demo_data.py or Stage 01–03 for your own files.",
            }

    from marketforensics.demo_factory import write_demo_bundle

    write_demo_bundle(DEMO)
    cases = normalize_cases(pd.read_csv(DEMO / "case_features.csv"))
    return {
        "cases": cases,
        "source": "demo",
        "demo": True,
        "banner": "Demo data was generated automatically so the app can open.",
    }
