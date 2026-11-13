"""Write a labelled demo dataset under data/demo/ so Streamlit always has cases."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import ROOT as PROJECT_ROOT
from marketforensics.demo_factory import write_demo_bundle


def main() -> None:
    demo = PROJECT_ROOT / "data" / "demo"
    write_demo_bundle(demo)
    print(f"Demo data written to {demo}")
    print("Open the app with:  streamlit run app.py")
    print("The UI will show a Demo data banner until Stage 03 files exist.")


if __name__ == "__main__":
    main()
