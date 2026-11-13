"""Step 8: score saved agent directions against later prices, then write the report."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from marketforensics.config import (
    FEATURES,
    NIFTY_STEM,
    PLOTS,
    REPORTS,
    RESULTS,
    RESULTS_A,
    RESULTS_B,
    RESULTS_C,
    ROOT,
    PipelineError,
    ensure_data_dirs,
)
from marketforensics.data import load_processed

HORIZONS = {"30d": 30, "90d": 90}


def _wilson(wins: int, n: int) -> tuple[float, float] | None:
    if n <= 0:
        return None
    z = 1.96
    p = wins / n
    den = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return ((centre - margin) / den, (centre + margin) / den)


def _forward_return(close: pd.Series, day: pd.Timestamp, calendar_days: int) -> float | None:
    if day not in close.index:
        return None
    target = day + pd.Timedelta(days=calendar_days)
    future = close.index[close.index >= target]
    if len(future) == 0:
        return None
    start_px = float(close.loc[day])
    end_px = float(close.loc[future[0]])
    if start_px <= 0:
        return None
    return (end_px / start_px - 1.0) * 100.0


def _direction_of(payload: dict, version: str) -> str | None:
    if version == "A":
        parsed = payload.get("parsed") or {}
        return parsed.get("direction")
    if version == "B":
        return payload.get("vote_direction")
    chair = payload.get("chair") or {}
    parsed = chair.get("parsed") if isinstance(chair, dict) else None
    if isinstance(parsed, dict):
        return parsed.get("direction")
    return None


def _load_version(folder: Path, version: str) -> list[dict]:
    rows = []
    if not folder.exists():
        return rows
    for path in sorted(folder.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        direction = _direction_of(payload, version)
        if direction not in {"up", "down"}:
            continue
        rows.append(
            {
                "ticker": payload.get("ticker") or path.stem.rsplit("_", 1)[0],
                "date": str(payload.get("date") or path.stem.rsplit("_", 1)[-1])[:10],
                "direction": direction,
            }
        )
    return rows


def _slice_stats(frame: pd.DataFrame, horizon: str) -> dict:
    col = f"fwd_{horizon}"
    match = f"match_{horizon}"
    part = frame.dropna(subset=[col, match])
    n = int(len(part))
    wins = int(part[match].sum()) if n else 0
    rate = wins / n if n else None
    ci = _wilson(wins, n)
    plain = "No scored cases for this slice."
    if rate is not None and ci is not None:
        plain = (
            f"{wins} of {n} direction calls matched the sign of the {horizon} forward return "
            f"({rate:.0%}). A 95% interval for that share is {ci[0]:.0%} to {ci[1]:.0%}. "
            "This describes these cases only. It is not a trading profit."
        )
    up = part[part["direction"] == "up"][col]
    t_plain = "Too few 'up' calls for a t-test."
    if len(up) >= 2:
        test = stats.ttest_1samp(up.to_numpy(), 0.0)
        t_plain = (
            f"Mean {horizon} return after an 'up' call is {float(up.mean()):.2f}%. "
            f"A one-sample t-test against 0 has p={float(test.pvalue):.3f} (n={len(up)}). "
            "A small p does not mean the method beat the market."
        )
    return {
        "n": n,
        "wins": wins,
        "win_rate": rate,
        "ci95": list(ci) if ci else None,
        "plain": plain,
        "t_test_plain": t_plain,
    }


def run_backtest() -> dict:
    ensure_data_dirs()
    missing = [name for name, folder in (("A", RESULTS_A), ("B", RESULTS_B), ("C", RESULTS_C)) if not list(folder.glob("*.json"))]
    if missing:
        raise PipelineError(
            "Missing agent result JSON for versions: " + ", ".join(missing) + ".\n"
            "Create them with a real Groq key in .env:\n  python run_pipeline.py --steps 7 --n 50"
        )
    feat_path = FEATURES / "case_features.csv"
    if not feat_path.exists():
        raise PipelineError(
            f"Missing {feat_path}\nCreate it with:\n  python run_pipeline.py --steps 5"
        )
    features = pd.read_csv(feat_path)
    features["date"] = features["date"].astype(str).str.slice(0, 10)
    summary = {"versions": {}, "note": "Direction match vs later return. Not a claim of beating the market."}
    chart_rates = []
    files = []
    rows_in = 0
    for version, folder in (("A", RESULTS_A), ("B", RESULTS_B), ("C", RESULTS_C)):
        calls = _load_version(folder, version)
        rows_in += len(list(folder.glob("*.json")))
        scored = []
        for call in calls:
            try:
                prices = load_processed(call["ticker"])
            except PipelineError:
                continue
            close = prices["Close"].astype(float)
            day = pd.Timestamp(call["date"])
            row = {"ticker": call["ticker"], "date": call["date"], "direction": call["direction"]}
            for name, days in HORIZONS.items():
                fwd = _forward_return(close, day, days)
                row[f"fwd_{name}"] = fwd
                if fwd is None:
                    row[f"match_{name}"] = None
                else:
                    row[f"match_{name}"] = (fwd >= 0 and call["direction"] == "up") or (
                        fwd < 0 and call["direction"] == "down"
                    )
            vol = features[(features["ticker"] == call["ticker"]) & (features["date"] == call["date"])]
            row["vol_20"] = float(vol["vol_20"].iloc[0]) if len(vol) and pd.notna(vol["vol_20"].iloc[0]) else None
            scored.append(row)
        frame = pd.DataFrame(scored)
        if frame.empty or frame["vol_20"].dropna().empty:
            raise PipelineError(
                f"Version {version} has no scored rows with volatility. Re-run steps 6 and 7."
            )
        median_vol = float(frame["vol_20"].median())
        high = frame[frame["vol_20"] >= median_vol]
        low = frame[frame["vol_20"] < median_vol]
        block = {
            "calls_with_up_or_down": int(len(frame)),
            "vol_median_split": median_vol,
            "all_30d": _slice_stats(frame, "30d"),
            "all_90d": _slice_stats(frame, "90d"),
            "high_vol_30d": _slice_stats(high, "30d"),
            "low_vol_30d": _slice_stats(low, "30d"),
        }
        summary["versions"][version] = block
        rate = block["all_30d"]["win_rate"]
        chart_rates.append(0.0 if rate is None else float(rate) * 100)
        print(f"  version {version}: {block['all_30d']['plain']}")

    out_json = RESULTS / "backtest_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    files.append(str(out_json))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["A solo", "B vote", "C debate"], chart_rates, color=["#E8B86D", "#7EA6FF", "#3DDC97"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("30-day direction match %")
    ax.set_title("Agent direction vs later return (not a profit chart)")
    plot = PLOTS / "backtest_abc_winrate.png"
    fig.tight_layout()
    fig.savefig(plot, dpi=140)
    plt.close(fig)
    files.append(str(plot))

    lines = [
        "# Backtest summary",
        "",
        "Question: after the agents named a direction, did the next 30 and 90 calendar days move that way?",
        "This is not a portfolio backtest and not evidence of beating the market.",
        "",
        "| version | 30d match | 90d match | high-vol 30d | low-vol 30d |",
        "|---------|-----------|-----------|--------------|-------------|",
    ]
    for version, block in summary["versions"].items():
        def pct(node: dict) -> str:
            rate = node.get("win_rate")
            if rate is None:
                return "n/a"
            return f"{rate:.0%} (n={node['n']})"

        lines.append(
            f"| {version} | {pct(block['all_30d'])} | {pct(block['all_90d'])} | "
            f"{pct(block['high_vol_30d'])} | {pct(block['low_vol_30d'])} |"
        )
        lines.append("")
        lines.append(block["all_30d"]["plain"])
        lines.append(block["all_30d"]["t_test_plain"])
        lines.append("")
    md = REPORTS / "backtest_summary.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    files.append(str(md))
    report = write_report(summary)
    files.append(str(report))
    print(f"STEP 8 summary: agent files in={rows_in}, wrote backtest and report")
    return {"rows_in": rows_in, "rows_out": len(summary["versions"]), "files": files, "notes": "backtest"}


def write_report(summary: dict) -> Path:
    metrics_path = RESULTS / "ml_baseline_metrics.json"
    if not metrics_path.exists():
        raise PipelineError(
            f"Missing {metrics_path}\nCreate it with:\n  python run_pipeline.py --steps 6"
        )
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    eda_path = ROOT / "notes" / "eda_findings.md"
    eda_text = eda_path.read_text(encoding="utf-8") if eda_path.exists() else "_EDA notes missing. Run step 4._"
    cases = ROOT / "data" / "cases" / "all_cases.csv"
    n_cases = len(pd.read_csv(cases)) if cases.exists() else 0
    version_lines = []
    for version, block in summary.get("versions", {}).items():
        version_lines.append(f"- Version {version}: {block['all_30d']['plain']}")
    body = f"""# MarketForensics report

Educational research. Not financial advice.

## Problem

Daily NSE prices sometimes jump far more than that stock's recent volatility. This project explains those days with evidence. It does not try to sell a trading rule.

## Related work

Event studies treat a large return as something to explain with information around that date (Fama, Fisher, Jensen and Roll, 1969; MacKinlay, 1997). Interpretable models ask which inputs drove a prediction (Ribeiro, Singh and Guestrin, 2016; Lundberg and Lee, 2017). Multi-agent debate asks whether several model roles change the answer (Du et al., 2023). This project is a small student-scale combination of those ideas on NSE daily bars.

## Method

Prices are Yahoo Finance daily bars (`auto_adjust=True`) from 2022-01-01 for Nifty-style tickers plus `^NSEI`, saved as `NSEI.csv`. Cleaning drops non-positive closes and dates that are not on the Nifty calendar. No prices are forward-filled.

A case is a day where the absolute return is at least 2.5 times the prior 20-day standard deviation. The volatility window is shifted by one day so the event return is not inside its own baseline.

Features use only rows on or before the event day: return, 5-day return, 20-day volatility, volume versus its 20-day average, 20-day moving average, above or below that average, 5-day momentum, stock return minus Nifty return, and weekday.

Labels are rules: market-wide if the absolute Nifty return is at least 1.5 percentage points, else stock-specific if the absolute gap versus Nifty is at least 2.0, else volume shock if volume is at least 2.0 times its 20-day average, else unknown. A random forest is trained on older cases and tested on newer cases.

Mystery score subtracts a capped share explained by the same-day Nifty move and above-average volume from 100. The formula is in `src/marketforensics/mystery.py`.

Agents A (solo), B (three roles, majority vote), and C (same roles, rebuttal, chair) call Groq. Replies that are not the required JSON are retried. They are not replaced with handwritten text. Responses are cached by version, persona, ticker, date, and prompt hash.

The backtest checks whether the stated direction matches the sign of the return to the next trading day on or after 30 and 90 calendar days. High-vol and low-vol splits use the median 20-day volatility of the scored cases.

## Results

Cases found: {n_cases}.

Random-forest test accuracy: {metrics.get("accuracy")}.
Train rows: {metrics.get("n_train")}. Test rows: {metrics.get("n_test")}.
Train ends {metrics.get("train_last_date")}; test starts {metrics.get("test_first_date")}.
Class counts: {metrics.get("class_counts")}.

Notes from the model step:

{chr(10).join("- " + note for note in metrics.get("honest_notes", []))}

EDA notes from disk:

{eda_text}

Agent direction check:

{chr(10).join(version_lines) if version_lines else "- No backtest block was passed in."}

## Limitations

Daily bars hide intraday causes. The labels are rules on the same style of numbers the model sees, not confirmed corporate events. Historical headlines are not attached unless a real item is dated within a day of the case, so many news-analyst prompts see an empty list. Groq outputs can still be wrong. Sample sizes for the direction check may be small, so the interval can be wide. Nothing here is a portfolio or a recommendation to trade.

## Conclusion

Read the accuracy and the direction-match sentences above as a description of this sample. If debate (C) matches direction more often than solo (A), that is a comparison on these cases only. If it does not, that result stands. The project is for learning how to explain a move and how to admit what is still unexplained.
"""
    path = ROOT / "docs" / "MarketForensics_Report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    print(f"  wrote {path}")
    return path
