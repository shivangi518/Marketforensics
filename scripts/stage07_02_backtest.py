"""Stage 07 — Simple forward-return sanity check by label (not trading advice)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json

import pandas as pd

from marketforensics.config import FEATURES, REPORTS, RESULTS, ensure_data_dirs
from marketforensics.io import returns_csv


def forward_return(ticker: str, date: str, horizon: int) -> float | None:
    path = returns_csv(ticker)
    if not path.exists():
        return None
    s = pd.read_csv(path, parse_dates=["Date"], index_col="Date")["return_pct"]
    event = pd.Timestamp(date)
    if event not in s.index:
        return None
    loc = s.index.get_loc(event)
    if isinstance(loc, slice):
        return None
    end = loc + horizon
    if end >= len(s):
        return None
    window = s.iloc[loc + 1 : end + 1]
    return float((1 + window / 100).prod() * 100 - 100)


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need case_features.csv")
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        f30 = forward_return(str(r["ticker"]), str(r["date"]), 21)
        f90 = forward_return(str(r["ticker"]), str(r["date"]), 63)
        direction = "up" if r.get("return_pct", 0) >= 0 else "down"
        fwd_dir = None if f30 is None else ("up" if f30 >= 0 else "down")
        rows.append(
            {
                **r.to_dict(),
                "fwd_21d": f30,
                "fwd_63d": f90,
                "event_dir": direction,
                "fwd_dir": fwd_dir,
                "dir_match_21d": None if fwd_dir is None else fwd_dir == direction,
            }
        )
    out_df = pd.DataFrame(rows)
    ensure_data_dirs()
    RESULTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS / "backtest_forward.csv"
    out_df.to_csv(csv_path, index=False)

    valid = out_df.dropna(subset=["dir_match_21d"])
    win = float(valid["dir_match_21d"].mean()) if len(valid) else 0.0
    summary = {
        "n": int(len(valid)),
        "direction_match_21d": win,
        "note": "Educational sanity check only. Not a trading backtest of profit.",
    }
    (RESULTS / "backtest_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md = REPORTS / "backtest_summary.md"
    md.write_text(
        "# Backtest summary\n\n"
        f"- Cases with 21-day forward data: {summary['n']}\n"
        f"- Event-direction vs 21-day forward sign match: {win:.1%}\n\n"
        "This checks whether big-move days continued the same way. "
        "It is **not** evidence of a profitable strategy.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print(f"Wrote {md}")


if __name__ == "__main__":
    main()
