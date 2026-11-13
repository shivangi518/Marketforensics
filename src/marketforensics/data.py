"""Step 1–2: download Yahoo prices and clean them onto the Nifty calendar."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

from marketforensics.config import (
    NIFTY_INDEX,
    NIFTY_STEM,
    RAW,
    PROCESSED,
    REPORTS,
    START_DATE,
    PipelineError,
    ensure_data_dirs,
    ticker_stem,
)


def _flatten(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [c[0] if isinstance(c, tuple) else c for c in out.columns]
    return out


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    idx = pd.to_datetime(out.index, errors="coerce")
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    out.index = pd.DatetimeIndex(idx).normalize()
    out = out[out.index.notna()]
    out = out[~out.index.duplicated(keep="last")]
    return out.sort_index()


def download_one(ticker: str, start: str = START_DATE, end: str | None = None, attempts: int = 3) -> dict:
    """Download one Yahoo symbol with retries. Never writes a stand-in file on failure."""
    ensure_data_dirs()
    stem = ticker_stem(ticker)
    yahoo = NIFTY_INDEX if stem == NIFTY_STEM else ticker
    last_error = "unknown error"
    for attempt in range(attempts):
        try:
            df = yf.download(yahoo, start=start, end=end, auto_adjust=True, progress=False, threads=False)
            if df is None or df.empty:
                raise RuntimeError(f"Yahoo returned no rows for {yahoo}")
            df = _normalize_index(_flatten(df))
            df.index.name = "Date"
            if "Close" not in df.columns:
                raise RuntimeError(f"No Close column for {yahoo}: {list(df.columns)}")
            path = RAW / f"{stem}.csv"
            df.to_csv(path)
            meta = {
                "ticker": yahoo,
                "file_stem": stem,
                "source": "Yahoo Finance (yfinance)",
                "data_type": "daily OHLCV (auto_adjust=True)",
                "start_requested": start,
                "end_requested": end,
                "rows": int(len(df)),
                "date_first": str(df.index.min().date()),
                "date_last": str(df.index.max().date()),
                "columns": [str(c) for c in df.columns],
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                "file": str(path).replace("\\", "/"),
            }
            meta_path = RAW / f"{stem}_meta.json"
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            return {"ticker": yahoo, "stem": stem, "rows": int(len(df)), "file": str(path), "error": None}
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2 ** attempt)
    return {"ticker": yahoo, "stem": stem, "rows": 0, "file": None, "error": last_error}


def run_download(start: str = START_DATE) -> dict:
    """Download until UNIVERSE_LIMIT stocks succeed, then the Nifty index. Failures are skipped."""
    from marketforensics.config import NIFTY50_TICKERS, UNIVERSE_LIMIT

    ok, failed = [], []
    files: list[str] = []
    rows_out = 0
    symbols_tried = 0

    def _take(ticker: str) -> None:
        nonlocal rows_out, symbols_tried
        symbols_tried += 1
        print(f"Downloading {ticker_stem(ticker)} ({ticker})...")
        info = download_one(ticker, start=start)
        if info["error"]:
            print(f"  FAILED {info['ticker']}: {info['error']}")
            failed.append({"ticker": info["ticker"], "error": info["error"]})
            return
        print(f"  rows={info['rows']} -> {info['file']}")
        ok.append(info["ticker"])
        files.append(info["file"])
        files.append(str(RAW / f"{info['stem']}_meta.json"))
        rows_out += int(info["rows"])

    for ticker in NIFTY50_TICKERS:
        if sum(1 for name in ok if ticker_stem(name) != NIFTY_STEM) >= UNIVERSE_LIMIT:
            break
        _take(ticker)
    if ticker_stem(NIFTY_INDEX) not in {ticker_stem(name) for name in ok}:
        _take(NIFTY_INDEX)

    log_path = RAW / "download_failures.json"
    log_path.write_text(json.dumps({"ok": ok, "failed": failed}, indent=2), encoding="utf-8")
    files.append(str(log_path))
    if not any(ticker_stem(t) == NIFTY_STEM for t in ok) and not (RAW / f"{NIFTY_STEM}.csv").exists():
        raise PipelineError(
            "Nifty (^NSEI) did not download, so later steps cannot align dates.\n"
            "Retry:\n  python run_pipeline.py --steps 1"
        )
    if len(ok) < 2:
        raise PipelineError(
            "Fewer than 2 symbols downloaded.\n"
            "Check internet access to Yahoo Finance, then retry:\n  python run_pipeline.py --steps 1"
        )
    notes = f"ok={len(ok)} failed={len(failed)}"
    if failed:
        notes += " | failed: " + ", ".join(item["ticker"] for item in failed)
    print(f"STEP 1 summary: rows in={symbols_tried} symbols, rows out={rows_out} price rows. {notes}")
    return {"rows_in": symbols_tried, "rows_out": rows_out, "files": files, "notes": notes}


def load_price_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df = _normalize_index(df)
    return df


def load_processed(ticker: str) -> pd.DataFrame:
    path = PROCESSED / f"{ticker_stem(ticker)}.csv"
    if not path.exists():
        raise PipelineError(
            f"Missing cleaned file: {path}\n"
            "Create it with:\n  python run_pipeline.py --steps 2"
        )
    return load_price_csv(path)


def run_clean() -> dict:
    ensure_data_dirs()
    for stray in PROCESSED.glob("*.csv"):
        if stray.stem.startswith("^"):
            stray.unlink()
    nifty_path = RAW / f"{NIFTY_STEM}.csv"
    if not nifty_path.exists():
        raise PipelineError(
            f"Missing {nifty_path}\n"
            "Create it with:\n  python run_pipeline.py --steps 1"
        )
    raw_files = sorted(p for p in RAW.glob("*.csv") if not p.name.startswith("universe"))
    if len(raw_files) < 2:
        raise PipelineError(
            "No raw price CSVs found in data/raw.\n"
            "Create them with:\n  python run_pipeline.py --steps 1"
        )

    nifty = load_price_csv(nifty_path)
    if "Close" not in nifty.columns:
        raise PipelineError(f"{nifty_path} has no Close column. Re-download with step 1.")
    nifty = nifty[nifty["Close"].astype(float) > 0]
    calendar = nifty.index

    rows_in = 0
    rows_out = 0
    files: list[str] = []
    report_rows = []
    for path in raw_files:
        stem = ticker_stem(path.stem)
        df = load_price_csv(path)
        rows_in += len(df)
        if "Close" not in df.columns:
            print(f"  skip {stem}: no Close column")
            continue
        df = df[pd.to_numeric(df["Close"], errors="coerce") > 0]
        df = df[~df.index.duplicated(keep="last")].sort_index()
        missing = calendar.difference(df.index)
        aligned = df.reindex(calendar).dropna(subset=["Close"])
        aligned = aligned[aligned["Close"].astype(float) > 0]
        if aligned.empty:
            print(f"  skip {stem}: no overlap with Nifty calendar")
            continue
        aligned["return_pct"] = aligned["Close"].astype(float).pct_change() * 100
        out = PROCESSED / f"{stem}.csv"
        aligned.to_csv(out)
        files.append(str(out))
        rows_out += len(aligned)
        report_rows.append(
            {
                "file": stem,
                "rows_raw": int(len(df)),
                "rows_aligned": int(len(aligned)),
                "first": str(aligned.index.min().date()),
                "last": str(aligned.index.max().date()),
                "nifty_dates_missing_in_stock": int(len(missing)),
            }
        )
        print(f"  {stem}: {len(df)} raw -> {len(aligned)} aligned, gaps vs Nifty={len(missing)}")

    if not (PROCESSED / f"{NIFTY_STEM}.csv").exists():
        raise PipelineError("Cleaned NSEI.csv was not written. Re-run step 1 then step 2.")

    lines = [
        "# Data README",
        "",
        "Cleaned daily NSE prices aligned to the Nifty trading calendar.",
        "Dates the stock does not have are dropped (not forward-filled), so returns are not invented.",
        "",
        f"Source: Yahoo Finance via yfinance, start requested {START_DATE}, auto_adjust=True.",
        "",
        "| file | rows raw | rows aligned | first | last | Nifty dates missing |",
        "|------|----------|--------------|-------|------|---------------------|",
    ]
    for row in report_rows:
        lines.append(
            f"| {row['file']} | {row['rows_raw']} | {row['rows_aligned']} | {row['first']} | "
            f"{row['last']} | {row['nifty_dates_missing_in_stock']} |"
        )
    readme = ROOT_DATA_README()
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    files.append(str(readme))
    print(f"STEP 2 summary: rows in={rows_in}, rows out={rows_out}, files={len(report_rows)} stocks")
    return {"rows_in": rows_in, "rows_out": rows_out, "files": files, "notes": f"stocks={len(report_rows)}"}


def ROOT_DATA_README() -> Path:
    from marketforensics.config import DATA

    return DATA / "DATA_README.md"
