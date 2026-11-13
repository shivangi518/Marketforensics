"""Step 3: volatility-scaled jump days. Baseline excludes the event day."""

from __future__ import annotations

import pandas as pd

from marketforensics.config import (
    CASE_AFTER,
    CASE_BEFORE,
    CASES,
    K_BIG_MOVE,
    NIFTY_STEM,
    VOL_WINDOW,
    PipelineError,
    ensure_data_dirs,
    ticker_stem,
)
from marketforensics.data import load_processed


def _processed_stems() -> list[str]:
    from marketforensics.config import PROCESSED

    stems = []
    for path in sorted(PROCESSED.glob("*.csv")):
        if ticker_stem(path.stem) == NIFTY_STEM or path.stem.endswith("_returns"):
            continue
        stems.append(path.stem)
    return stems


def detect_frame(ticker: str, k: float = K_BIG_MOVE) -> pd.DataFrame:
    """|return| >= k * rolling std shifted by 1 day, so the event is not inside its own baseline."""
    df = load_processed(ticker)
    if "return_pct" not in df.columns:
        raise PipelineError(f"{ticker} cleaned file has no return_pct. Re-run step 2.")
    ret = df["return_pct"].astype(float)
    baseline = ret.rolling(VOL_WINDOW).std().shift(1)
    threshold = k * baseline
    mask = ret.abs() >= threshold
    out = pd.DataFrame(
        {
            "ticker": ticker_stem(ticker),
            "date": ret.index[mask.fillna(False)].strftime("%Y-%m-%d"),
            "return_pct": ret[mask.fillna(False)].to_numpy(),
            "volatility_baseline": baseline[mask.fillna(False)].to_numpy(),
            "threshold": threshold[mask.fillna(False)].to_numpy(),
        }
    )
    return out.reset_index(drop=True)


def windows_for(ticker: str, cases: pd.DataFrame, before: int = CASE_BEFORE, after: int = CASE_AFTER) -> pd.DataFrame:
    df = load_processed(ticker)
    ret = df["return_pct"].astype(float)
    rows = []
    for raw_date in cases["date"]:
        day = pd.Timestamp(raw_date)
        if day not in ret.index:
            continue
        loc = ret.index.get_loc(day)
        if isinstance(loc, slice):
            continue
        start = max(0, loc - before)
        end = min(len(ret) - 1, loc + after)
        window = ret.iloc[start : end + 1]
        pre = window.iloc[: loc - start]
        post = window.iloc[loc - start + 1 :]
        rows.append(
            {
                "ticker": ticker_stem(ticker),
                "event_date": day.strftime("%Y-%m-%d"),
                "event_return_pct": float(ret.loc[day]),
                "window_start": ret.index[start].strftime("%Y-%m-%d"),
                "window_end": ret.index[end].strftime("%Y-%m-%d"),
                "pre_mean_return": float(pre.mean()) if len(pre) else None,
                "post_mean_return": float(post.mean()) if len(post) else None,
            }
        )
    return pd.DataFrame(rows)


def run_cases() -> dict:
    ensure_data_dirs()
    stems = _processed_stems()
    if not stems:
        raise PipelineError(
            "No cleaned stock files in data/processed (besides NSEI).\n"
            "Create them with:\n  python run_pipeline.py --steps 1-2"
        )
    frames = []
    window_frames = []
    files: list[str] = []
    rows_in = 0
    for stem in stems:
        px = load_processed(stem)
        rows_in += len(px)
        found = detect_frame(stem)
        per = CASES / f"{stem}_big_moves.csv"
        save = found.copy()
        save = save.rename(columns={"date": "Date"})
        save.to_csv(per, index=False)
        files.append(str(per))
        frames.append(found)
        window_frames.append(windows_for(stem, found))
        print(f"  {stem}: {len(found)} big-move days")

    all_cases = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if all_cases.empty:
        raise PipelineError(
            "The big-move rule found zero cases.\n"
            "Check that cleaned files have return_pct and more than 21 rows, then re-run:\n"
            "  python run_pipeline.py --steps 3"
        )
    all_path = CASES / "all_cases.csv"
    all_cases.to_csv(all_path, index=False)
    windows = pd.concat(window_frames, ignore_index=True) if window_frames else pd.DataFrame()
    win_path = CASES / "case_windows.csv"
    windows.to_csv(win_path, index=False)
    files.extend([str(all_path), str(win_path)])
    print(f"STEP 3 summary: rows in={rows_in} price rows, rows out={len(all_cases)} cases")
    return {"rows_in": rows_in, "rows_out": int(len(all_cases)), "files": files, "notes": f"windows={len(windows)}"}


def detect_big_moves(ticker: str, k: float = K_BIG_MOVE):
    """Stage-02 compatible wrapper. Writes the per-ticker case file."""
    found = detect_frame(ticker, k=k)
    ensure_data_dirs()
    path = CASES / f"{ticker_stem(ticker)}_big_moves.csv"
    save = found.rename(columns={"date": "Date"})
    save.to_csv(path, index=False)
    return path


def build_windows(ticker: str, before: int = CASE_BEFORE, after: int = CASE_AFTER):
    path = CASES / f"{ticker_stem(ticker)}_big_moves.csv"
    if not path.exists():
        raise PipelineError(
            f"Missing {path}\nCreate it with:\n  python run_pipeline.py --steps 3"
        )
    cases = pd.read_csv(path).rename(columns={"Date": "date"})
    windows = windows_for(ticker, cases, before=before, after=after)
    out = CASES / f"{ticker_stem(ticker)}_case_windows.csv"
    windows.to_csv(out, index=False)
    return out
