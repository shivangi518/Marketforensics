"""Stage 01 — Compute returns for every price CSV in data/raw."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import RAW
from marketforensics.returns import compute_returns


def main() -> None:
    files = sorted(RAW.glob("*.csv"))
    if not files:
        raise SystemExit("No CSVs in data/raw.")
    for path in files:
        compute_returns(path.stem)


if __name__ == "__main__":
    main()
