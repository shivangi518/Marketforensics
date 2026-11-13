"""Stage 02 — Six EDA charts for NSE cases (saved under data/plots/eda/)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import pandas as pd

from marketforensics.config import CASES, DEFAULT_TICKER, NIFTY_INDEX, PLOTS_EDA, PROCESSED, ensure_data_dirs
from marketforensics.io import close_column, load_prices, volume_column

TICKER = DEFAULT_TICKER


def _save(name: str) -> None:
    path = PLOTS_EDA / name
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"saved {path}")


def main() -> None:
    ensure_data_dirs()
    prices = load_prices(TICKER)
    close = close_column(prices)
    vol_col = volume_column(prices)
    ret_path = PROCESSED / f"{TICKER}_returns.csv"
    if not ret_path.exists():
        raise SystemExit("Compute returns first.")
    rets = pd.read_csv(ret_path, parse_dates=["Date"], index_col="Date")

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(prices.index, prices[close], color="tab:blue")
    ax1.set_ylabel("Close")
    if vol_col:
        ax2 = ax1.twinx()
        ax2.bar(prices.index, prices[vol_col], alpha=0.3, color="tab:gray")
        ax2.set_ylabel("Volume")
    plt.title(f"{TICKER} price + volume")
    _save(f"{TICKER}_price_volume.png")

    plt.figure(figsize=(8, 4))
    plt.hist(rets["return_pct"].dropna(), bins=50, color="tab:purple")
    plt.title(f"{TICKER} daily return histogram")
    plt.xlabel("Return %")
    _save(f"{TICKER}_return_hist.png")

    nifty_path = PROCESSED / f"{NIFTY_INDEX}_returns.csv"
    if nifty_path.exists():
        nifty = pd.read_csv(nifty_path, parse_dates=["Date"], index_col="Date")
        aligned = pd.concat(
            {
                TICKER: (1 + rets["return_pct"] / 100).cumprod() * 100,
                "Nifty": (1 + nifty["return_pct"] / 100).cumprod() * 100,
            },
            axis=1,
        ).dropna()
        plt.figure(figsize=(10, 4))
        plt.plot(aligned.index, aligned[TICKER], label=TICKER)
        plt.plot(aligned.index, aligned["Nifty"], label="Nifty 50")
        plt.title("Growth of 100")
        plt.legend()
        _save("stock_vs_nifty_growth100.png")

    all_path = CASES / "all_cases.csv"
    single = CASES / f"{TICKER}_big_moves.csv"
    cases = None
    if all_path.exists():
        cases = pd.read_csv(all_path, parse_dates=["Date"])
    elif single.exists():
        cases = pd.read_csv(single, parse_dates=["Date"])
        cases["ticker"] = TICKER

    if cases is not None and not cases.empty:
        counts = cases.groupby("ticker").size().sort_values(ascending=False)
        plt.figure(figsize=(10, 4))
        counts.plot(kind="bar")
        plt.title("Big moves per stock")
        plt.ylabel("Count")
        _save("big_moves_per_stock.png")

        cases["month"] = cases["Date"].dt.to_period("M").astype(str)
        by_month = cases.groupby("month").size()
        plt.figure(figsize=(10, 4))
        by_month.plot()
        plt.title("Big moves by month")
        plt.xticks(rotation=45)
        _save("big_moves_by_month.png")

        if vol_col:
            joined = cases.set_index("Date").join(prices[[vol_col]], how="left")
            vol_chg = prices[vol_col].pct_change()
            tmp = pd.DataFrame(
                {"return_pct": joined["return_pct"], "volume_chg": vol_chg.reindex(joined.index)}
            ).dropna()
            plt.figure(figsize=(5, 5))
            plt.scatter(tmp["volume_chg"], tmp["return_pct"], alpha=0.4)
            plt.xlabel("Volume change")
            plt.ylabel("Event return %")
            plt.title("Return vs volume change (event days)")
            _save("return_vs_volume_scatter.png")

    print("EDA charts done.")


if __name__ == "__main__":
    main()
