"""Stage 01 — Compute daily returns for the default ticker."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import DEFAULT_TICKER
from marketforensics.returns import compute_returns

TICKER = DEFAULT_TICKER


def main() -> None:
    compute_returns(TICKER)


if __name__ == "__main__":
    main()
