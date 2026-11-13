"""Stage 01 — Plot closing price."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from marketforensics.config import DEFAULT_TICKER, PLOTS, ensure_data_dirs
from marketforensics.io import close_column, load_prices

TICKER = DEFAULT_TICKER


def main() -> None:
    df = load_prices(TICKER)
    close_col = close_column(df)

    plt.figure(figsize=(10, 4))
    plt.plot(df.index, df[close_col], label=f"{TICKER} Close")
    plt.title(f"{TICKER} Closing Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()

    ensure_data_dirs()
    plot_path = PLOTS / f"{TICKER}_close.png"
    plt.savefig(plot_path, dpi=140)
    print(f"Saved plot -> {plot_path}")
    plt.show()


if __name__ == "__main__":
    main()
