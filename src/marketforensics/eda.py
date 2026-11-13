"""Step 4: charts and a profile written from cleaned prices and cases."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from marketforensics.config import (
    CASES,
    DEFAULT_TICKER,
    NIFTY_STEM,
    PLOTS_EDA,
    PROCESSED,
    REPORTS,
    ROOT,
    PipelineError,
    ensure_data_dirs,
    ticker_stem,
)
from marketforensics.data import load_processed


def _save(fig: plt.Figure, name: str, files: list[str]) -> None:
    path = PLOTS_EDA / name
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    files.append(str(path))
    print(f"  wrote {path}")


def _example_stem(cases: pd.DataFrame) -> str:
    preferred = ticker_stem(DEFAULT_TICKER)
    if (PROCESSED / f"{preferred}.csv").exists():
        return preferred
    if not cases.empty:
        top = cases["ticker"].value_counts().index[0]
        return str(top)
    stems = [p.stem for p in PROCESSED.glob("*.csv") if p.stem != NIFTY_STEM]
    if not stems:
        raise PipelineError(
            "No cleaned stock file to chart.\nCreate data with:\n  python run_pipeline.py --steps 1-2"
        )
    return stems[0]


def run_eda() -> dict:
    ensure_data_dirs()
    cases_path = CASES / "all_cases.csv"
    if not cases_path.exists():
        raise PipelineError(
            f"Missing {cases_path}\nCreate it with:\n  python run_pipeline.py --steps 3"
        )
    cases = pd.read_csv(cases_path, parse_dates=["date"])
    if cases.empty:
        raise PipelineError("all_cases.csv has no rows. Re-run step 3.")
    nifty = load_processed(NIFTY_STEM)
    stem = _example_stem(cases)
    stock = load_processed(stem)
    files: list[str] = []

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(stock.index, stock["Close"], color="#1f4e79", label="Close")
    ax1.set_ylabel("Close")
    if "Volume" in stock.columns:
        ax2 = ax1.twinx()
        ax2.bar(stock.index, stock["Volume"], color="#9aa8c2", alpha=0.35)
        ax2.set_ylabel("Volume")
    ax1.set_title(f"{stem} close and volume")
    _save(fig, f"{stem}_price_volume.png", files)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(stock["return_pct"].dropna(), bins=40, color="#1f4e79")
    ax.set_title(f"{stem} daily return histogram")
    ax.set_xlabel("Return %")
    _save(fig, f"{stem}_return_hist.png", files)

    joined = pd.concat(
        {
            stem: stock["Close"].astype(float),
            "Nifty": nifty["Close"].astype(float),
        },
        axis=1,
    ).dropna()
    if len(joined) >= 2:
        growth = joined / joined.iloc[0] * 100
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(growth.index, growth[stem], label=stem)
        ax.plot(growth.index, growth["Nifty"], label="Nifty")
        ax.legend()
        ax.set_title(f"{stem} vs Nifty, growth of 100")
        _save(fig, f"{stem}_vs_nifty_growth100.png", files)

    counts = cases.groupby("ticker").size().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 4))
    counts.plot(kind="bar", ax=ax, color="#1f4e79")
    ax.set_title("Big-move cases per stock")
    ax.set_ylabel("Cases")
    _save(fig, "big_moves_per_stock.png", files)

    by_month = cases.assign(month=cases["date"].dt.to_period("M").astype(str)).groupby("month").size()
    fig, ax = plt.subplots(figsize=(10, 4))
    by_month.plot(ax=ax, color="#1f4e79")
    ax.set_title("Big-move cases by month")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "big_moves_by_month.png", files)

    names = [str(t) for t in counts.index[:12]]
    ret_map: dict[str, pd.Series] = {}
    vol_map: dict[str, pd.Series] = {}
    for ticker in names:
        try:
            frame = load_processed(ticker)
        except PipelineError:
            continue
        ret_map[ticker] = frame["return_pct"].replace([np.inf, -np.inf], np.nan)
        if "Volume" not in frame.columns:
            continue
        volume = frame["Volume"].astype(float).where(lambda s: s > 0)
        vol_map[ticker] = np.log(volume).diff().replace([np.inf, -np.inf], np.nan)
    common = [name for name in names if name in ret_map and name in vol_map]
    if common:
        matrix = pd.DataFrame(index=common, columns=common, dtype=float)
        for left in common:
            for right in common:
                pair = pd.concat(
                    [ret_map[left].rename("ret"), vol_map[right].rename("vol")],
                    axis=1,
                ).dropna()
                matrix.loc[left, right] = (
                    float(pair["ret"].corr(pair["vol"])) if len(pair) > 20 else np.nan
                )
        values = matrix.astype(float).to_numpy()
        fig, ax = plt.subplots(figsize=(9.2, 7.4))
        im = ax.imshow(values, cmap="coolwarm", vmin=-0.5, vmax=0.5, aspect="auto")
        ax.set_xticks(range(len(common)), labels=common, rotation=55, ha="right", fontsize=8)
        ax.set_yticks(range(len(common)), labels=common, fontsize=8)
        ax.set_xlabel("Volume log-change")
        ax.set_ylabel("Daily return")
        ax.set_title("Figure 7. Corr(stock return, other stock volume change)")
        for i in range(len(common)):
            for j in range(len(common)):
                cell = values[i, j]
                if np.isnan(cell):
                    continue
                ax.text(j, i, f"{cell:.2f}", ha="center", va="center", fontsize=6.5, color="#111")
        fig.colorbar(im, ax=ax, fraction=0.046, label="correlation")
        _save(fig, "return_vs_volume_corr_heatmap.png", files)

    profile_lines = [
        "# Universe profile",
        "",
        "Computed from cleaned prices. Missing Nifty dates were dropped in step 2, not filled.",
        "",
        "| stock | rows | avg return % | volatility % | best day % | worst day % |",
        "|-------|------|--------------|--------------|------------|-------------|",
    ]
    best_name, best_val = "", -1e9
    worst_name, worst_val = "", 1e9
    for path in sorted(PROCESSED.glob("*.csv")):
        if path.stem.endswith("_returns"):
            continue
        frame = load_processed(path.stem)
        ret = frame["return_pct"].dropna()
        if ret.empty:
            continue
        avg = float(ret.mean())
        vol = float(ret.std())
        best = float(ret.max())
        worst = float(ret.min())
        profile_lines.append(
            f"| {path.stem} | {len(frame)} | {avg:.3f} | {vol:.3f} | {best:.3f} | {worst:.3f} |"
        )
        if path.stem != NIFTY_STEM and best > best_val:
            best_name, best_val = path.stem, best
        if path.stem != NIFTY_STEM and worst < worst_val:
            worst_name, worst_val = path.stem, worst
    profile = REPORTS / "universe_profile.md"
    profile.write_text("\n".join(profile_lines) + "\n", encoding="utf-8")
    files.append(str(profile))

    nifty_ret = nifty["return_pct"]
    merged = cases.copy()
    merged["nifty_return"] = merged["date"].map(lambda d: nifty_ret.get(pd.Timestamp(d), np.nan))
    both = merged.dropna(subset=["nifty_return"])
    beat = float((both["return_pct"].abs() > both["nifty_return"].abs()).mean()) if len(both) else float("nan")
    top_ticker = str(counts.index[0])
    top_n = int(counts.iloc[0])
    top_month = str(by_month.idxmax())
    month_n = int(by_month.max())
    median_abs = float(cases["return_pct"].abs().median())
    insights = [
        "# EDA findings",
        "",
        f"- {len(cases)} big-move cases across {cases['ticker'].nunique()} stocks after the 2.5× shifted-volatility rule.",
        f"- {top_ticker} has the most cases ({top_n}).",
        f"- The month with the most cases is {top_month} ({month_n} cases).",
        f"- Median absolute case return is {median_abs:.2f}%.",
        f"- On {beat:.0%} of cases the stock's absolute return exceeded the Nifty's absolute return that day.",
        f"- Largest single-day gain in the cleaned universe (excluding the index file) is {best_val:.2f}% ({best_name}); largest drop is {worst_val:.2f}% ({worst_name}).",
    ]
    notes = ROOT / "notes" / "eda_findings.md"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text("\n".join(insights) + "\n", encoding="utf-8")
    files.append(str(notes))
    print(f"STEP 4 summary: rows in={len(cases)} cases, charts={len([f for f in files if f.endswith('.png')])}")
    return {"rows_in": int(len(cases)), "rows_out": len(files), "files": files, "notes": stem}
