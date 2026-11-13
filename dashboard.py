"""Chart dashboard. Does not call Gemini or Groq.

Run from the project folder:

    streamlit run dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from marketforensics.theme import inject_css
from marketforensics.ui import _read_json, load_cases, render_dashboard
from marketforensics.config import RESULTS


def main() -> None:
    st.set_page_config(page_title="MarketForensics dashboard", page_icon="MF", layout="wide")
    inject_css()
    st.sidebar.markdown("**MARKETFORENSICS**")
    st.sidebar.caption("Dashboard only. Agents stay in streamlit run app.py")
    cases = load_cases()
    metrics = _read_json(RESULTS / "ml_baseline_metrics.json")
    render_dashboard(cases, metrics)


main()
