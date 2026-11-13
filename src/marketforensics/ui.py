"""Streamlit terminal. Reads saved pipeline outputs only."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from marketforensics.agents import provider_label, run_investigation
from marketforensics.charts import (
    accuracy_gauge,
    candlestick,
    cases_by_month,
    cases_per_stock,
    confusion_heatmap,
    importance_bars,
    label_donut,
    moves_by_label,
    mystery_gauge,
    pr_bars,
    rebase,
)
from marketforensics.config import (
    CASES,
    CASES_JSON,
    FEATURES,
    NIFTY_STEM,
    PLOTS_EDA,
    PipelineError,
    PROCESSED,
    REPORTS,
    RESULTS,
    RESULTS_A,
    RESULTS_B,
    RESULTS_C,
)
from marketforensics.data import load_processed
from marketforensics.mystery import explained_and_mystery
from marketforensics.theme import LABEL_COLOR, inject_css

PAGES = [
    "Home",
    "Dashboard",
    "Market Overview",
    "Case Explorer",
    "Case Detail",
    "Insights",
    "Model Lab",
    "Agents",
    "Debate",
    "About",
]


@st.cache_data(show_spinner="Reading saved case files…")
def load_cases() -> pd.DataFrame:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = df["date"].astype(str).str.slice(0, 10)
    return df


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _footer() -> None:
    st.markdown(
        '<div class="foot"><span>Educational use only. Not financial advice.</span>'
        '<span>Real saved data · Transparent rules · Reproducible pipeline</span></div>',
        unsafe_allow_html=True,
    )


def _missing(command: str) -> None:
    st.info("This view needs a pipeline file that is not on disk yet.")
    st.code(command)


def _tape(cases: pd.DataFrame) -> None:
    if cases.empty:
        return
    recent = cases.sort_values("date").tail(16)
    bits = []
    for row in recent.itertuples():
        try:
            value = float(row.return_pct)
        except (TypeError, ValueError):
            continue
        klass = "up" if value >= 0 else "down"
        bits.append(f'{row.ticker} <span class="{klass}">{value:+.2f}%</span>')
    line = " &nbsp;·&nbsp; ".join(bits)
    st.markdown(f'<div class="tape"><span>{line} &nbsp;&nbsp; {line}</span></div>', unsafe_allow_html=True)


def _kpis(cases: pd.DataFrame, metrics: dict | None) -> None:
    stocks = cases["ticker"].nunique() if not cases.empty else 0
    accuracy = f"{metrics['accuracy'] * 100:.1f}%" if metrics and metrics.get("accuracy") is not None else "—"
    days = 0
    sample = PROCESSED / "RELIANCE.NS.csv"
    if sample.exists():
        days = max(0, sum(1 for _ in sample.open(encoding="utf-8")) - 1)
    st.markdown(
        f"""
<div class="kpis">
  <div class="glass kpi"><div class="n">{len(cases):,}</div><div class="label">Detected cases</div></div>
  <div class="glass kpi"><div class="n">{stocks}</div><div class="label">NSE stocks</div></div>
  <div class="glass kpi"><div class="n">{accuracy}</div><div class="label">Later-date accuracy</div></div>
  <div class="glass kpi"><div class="n">{days:,}</div><div class="label">Trading days</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_dashboard(cases: pd.DataFrame, metrics: dict | None) -> None:
    st.markdown(
        """
<div class="hero">
  <div class="hero-copy">
    <div class="kicker">Evidence board</div>
    <h1>Market signals, clearly framed.</h1>
    <p>Saved cases, labels, and model diagnostics in one view.</p>
  </div>
  <div class="terminal-card">
    <div class="terminal-top"><span>DATA STATUS</span><span>LOCAL FILES</span></div>
    <div class="terminal-row"><b>Prices</b><span>Loaded</span></div>
    <div class="terminal-row"><b>Cases</b><span>Loaded</span></div>
    <div class="terminal-row"><b>Model</b><span>Evaluated</span></div>
    <div class="terminal-row"><b>Claims</b><span>Constrained</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    _kpis(cases, metrics)
    if cases.empty:
        _missing("python run_pipeline.py --steps 5")
        return
    left, right = st.columns(2)
    with left:
        if "label" in cases.columns:
            st.plotly_chart(label_donut(cases["label"].astype(str).value_counts()), use_container_width=True)
    with right:
        if "date" in cases.columns:
            months = cases.assign(month=cases["date"].astype(str).str.slice(0, 7))["month"].value_counts().sort_index()
            st.plotly_chart(cases_by_month(months), use_container_width=True)
    if "ticker" in cases.columns:
        st.plotly_chart(cases_per_stock(cases["ticker"].astype(str).value_counts()), use_container_width=True)
    if "label" in cases.columns and "return_pct" in cases.columns:
        st.plotly_chart(moves_by_label(cases), use_container_width=True)
    if metrics:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(accuracy_gauge(float(metrics["accuracy"])), use_container_width=True)
            st.caption(
                f"Train {metrics.get('n_train')} cases through {metrics.get('train_last_date')}. "
                f"Test {metrics.get('n_test')} cases from {metrics.get('test_first_date')}."
            )
        with c2:
            st.plotly_chart(
                confusion_heatmap(metrics["confusion_matrix"], metrics["confusion_matrix_labels"]),
                use_container_width=True,
            )
        bars = pr_bars(metrics.get("classification_report") or "")
        if bars is not None:
            st.plotly_chart(bars, use_container_width=True)
        scores = metrics.get("permutation_importance_mean") or {}
        if scores:
            st.plotly_chart(importance_bars(scores), use_container_width=True)
        for note in metrics.get("honest_notes") or []:
            st.caption(note)


def page_home(cases: pd.DataFrame, metrics: dict | None) -> None:
    st.markdown(
        """
<div class="hero">
  <div class="hero-copy">
    <div class="kicker">NSE market forensics</div>
    <h1>Investigate the move.</h1>
    <p>Real prices, transparent rules, and later-date model evaluation.</p>
  </div>
  <div class="terminal-card">
    <div class="terminal-top"><span>RELIANCE.NS</span><span>EVENT WINDOW</span></div>
    <svg class="chart-line" viewBox="0 0 420 120" role="img" aria-label="Illustrative event line">
      <defs>
        <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#3B5BFF" stop-opacity=".28"/>
          <stop offset="100%" stop-color="#3B5BFF" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="M0 102 L35 94 L70 97 L105 78 L140 83 L175 66 L210 71 L245 32 L280 49 L315 42 L350 20 L385 29 L420 14 L420 120 L0 120 Z" fill="url(#lineFill)" stroke="none"/>
      <path d="M0 102 L35 94 L70 97 L105 78 L140 83 L175 66 L210 71 L245 32 L280 49 L315 42 L350 20 L385 29 L420 14" fill="none" stroke="#6E8BFF" stroke-width="3"/>
      <circle cx="245" cy="32" r="6" fill="#19C3B1"/>
    </svg>
    <div class="terminal-row"><b>Case rule</b><span>2.5× prior volatility</span></div>
    <div class="terminal-row"><b>Data policy</b><span>No future rows</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    _kpis(cases, metrics)
    if st.button("Explore the Cases"):
        st.session_state.nav = "Case Explorer"
        st.rerun()
    st.markdown(
        """
<div class="bento">
  <div class="glass"><h3>Detect unusual sessions</h3><p>Each stock is judged against its own prior volatility.</p></div>
  <div class="glass"><h3>Compare with Nifty</h3><p>Separate market movement from stock-specific movement.</p></div>
  <div class="glass"><h3>Test on later dates</h3><p>Older cases train the forest; newer cases evaluate it.</p></div>
</div>
<div class="trust-strip">
  <div>Real Yahoo OHLCV</div>
  <div>No forward filling</div>
  <div>Time-based split</div>
  <div>Rules published</div>
</div>
""",
        unsafe_allow_html=True,
    )
    if metrics and metrics.get("honest_notes"):
        st.caption(metrics["honest_notes"][0])


def page_market(cases: pd.DataFrame) -> None:
    st.subheader("Market overview")
    files = sorted(p.stem for p in PROCESSED.glob("*.csv") if p.stem != NIFTY_STEM)
    if not files:
        _missing("python run_pipeline.py --steps 2")
        return
    ticker = st.selectbox("Stock", files, index=files.index("RELIANCE.NS") if "RELIANCE.NS" in files else 0)
    try:
        prices = load_processed(ticker)
        nifty = load_processed(NIFTY_STEM)
    except PipelineError as exc:
        st.warning(str(exc))
        return
    st.plotly_chart(candlestick(prices, cases, ticker), use_container_width=True)
    chart = rebase(prices, nifty, None, ticker)
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)


def _filter(cases: pd.DataFrame) -> pd.DataFrame:
    c1, c2, c3 = st.columns(3)
    tickers = ["All"] + sorted(cases["ticker"].astype(str).unique())
    ticker = c1.selectbox("Stock", tickers)
    labels = ["All"] + sorted(cases["label"].astype(str).unique()) if "label" in cases.columns else ["All"]
    label = c2.selectbox("Label", labels)
    minimum = c3.number_input("Minimum absolute move %", min_value=0.0, value=0.0, step=0.5)
    view = cases
    if ticker != "All":
        view = view[view["ticker"].astype(str) == ticker]
    if label != "All" and "label" in view.columns:
        view = view[view["label"].astype(str) == label]
    if "return_pct" in view.columns:
        view = view[view["return_pct"].abs() >= float(minimum)]
    return view


def page_explorer(cases: pd.DataFrame) -> None:
    st.subheader("Case explorer")
    if cases.empty:
        _missing("python run_pipeline.py --steps 5")
        return
    view = _filter(cases)
    cols = [c for c in ("ticker", "date", "return_pct", "label", "vs_nifty", "volume_vs_avg20") if c in view.columns]
    st.dataframe(view[cols].sort_values("date"), use_container_width=True, hide_index=True, height=460)
    st.caption(f"{len(view):,} rows after filters.")


def _select_case(cases: pd.DataFrame) -> pd.Series | None:
    tickers = sorted(cases["ticker"].astype(str).unique())
    c1, c2 = st.columns(2)
    ticker = c1.selectbox("Stock", tickers, key="detail_ticker")
    dates = cases.loc[cases["ticker"].astype(str) == ticker, "date"].astype(str).tolist()
    date = c2.selectbox("Jump day", dates, index=len(dates) - 1, key="detail_date")
    match = cases[(cases["ticker"].astype(str) == ticker) & (cases["date"].astype(str) == date)]
    if match.empty:
        return None
    return match.iloc[0]


def page_detail(cases: pd.DataFrame) -> None:
    st.subheader("Case detail")
    if cases.empty:
        _missing("python run_pipeline.py --steps 5")
        return
    row = _select_case(cases)
    if row is None:
        return
    label = str(row.get("label") or "unknown")
    color = LABEL_COLOR.get(label, "#93A0B8")
    st.markdown(f'<span class="chip" style="color:{color};border-color:{color}">{label}</span>', unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("Return", f"{float(row['return_pct']):+.2f}%")
    b.metric("vs Nifty", f"{float(row['vs_nifty']):+.2f}%")
    c.metric("Volume vs avg", f"{float(row['volume_vs_avg20']):.2f}×")
    d.metric("20d vol", f"{float(row['vol_20']):.2f}%")
    try:
        explained, mystery = explained_and_mystery(float(row["return_pct"]), float(row["nifty_return_pct"]), float(row["volume_vs_avg20"]))
        st.plotly_chart(mystery_gauge(mystery), use_container_width=True)
        st.caption(f"Share tied to the index move and extra volume by the documented formula: {explained:.0f}%.")
    except (TypeError, ValueError, KeyError):
        st.caption("This row is missing a number the gauge needs.")
    clues = _read_json(CASES / "sample_explanations.json") or {}
    top = clues.get(f"{row['ticker']}|{str(row['date'])[:10]}")
    if isinstance(top, list) and top:
        st.markdown("**Saved top clues**")
        for item in top:
            st.markdown(f'<span class="chip">{item}</span>', unsafe_allow_html=True)
    try:
        prices = load_processed(str(row["ticker"]))
        nifty = load_processed(NIFTY_STEM)
    except PipelineError as exc:
        st.warning(str(exc))
        return
    event = pd.Timestamp(str(row["date"])[:10])
    window = cases[(cases["ticker"].astype(str) == str(row["ticker"]))]
    st.plotly_chart(candlestick(prices.loc[event - pd.Timedelta(days=40) : event + pd.Timedelta(days=15)], window, str(row["ticker"])), use_container_width=True)
    chart = rebase(prices, nifty, event, str(row["ticker"]))
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
    case_json = _read_json(CASES_JSON / f"{row['ticker']}_{str(row['date'])[:10]}.json")
    if case_json and case_json.get("headlines"):
        st.markdown("**Headlines dated within a day of the case**")
        for item in case_json["headlines"]:
            st.write(item.get("title", ""))


def page_insights(cases: pd.DataFrame) -> None:
    st.subheader("Insights")
    if cases.empty:
        _missing("python run_pipeline.py --steps 5")
        return
    counts = cases["ticker"].astype(str).value_counts()
    st.plotly_chart(cases_per_stock(counts), use_container_width=True)
    months = cases.assign(month=cases["date"].astype(str).str.slice(0, 7))["month"].value_counts().sort_index()
    st.plotly_chart(cases_by_month(months), use_container_width=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(label_donut(cases["label"].astype(str).value_counts()), use_container_width=True)
    with right:
        st.plotly_chart(moves_by_label(cases), use_container_width=True)
    for name in ("big_moves_per_stock.png", "big_moves_by_month.png", "return_vs_volume_corr_heatmap.png"):
        path = PLOTS_EDA / name
        if path.exists():
            st.image(str(path), use_container_width=True)


def page_model(metrics: dict | None) -> None:
    st.subheader("Model lab")
    if not metrics:
        _missing("python run_pipeline.py --steps 6")
        return
    st.plotly_chart(accuracy_gauge(float(metrics["accuracy"])), use_container_width=True)
    st.caption(f"Train {metrics.get('n_train')} cases through {metrics.get('train_last_date')}. Test {metrics.get('n_test')} cases from {metrics.get('test_first_date')}.")
    st.plotly_chart(confusion_heatmap(metrics["confusion_matrix"], metrics["confusion_matrix_labels"]), use_container_width=True)
    bars = pr_bars(metrics.get("classification_report") or "")
    if bars is not None:
        st.plotly_chart(bars, use_container_width=True)
    scores = metrics.get("permutation_importance_mean") or {}
    if scores:
        st.plotly_chart(importance_bars(scores), use_container_width=True)
    with st.expander("What does this accuracy mean?"):
        for note in metrics.get("honest_notes") or []:
            st.write(note)


def _coming(title: str) -> None:
    st.markdown(
        f"""
<div class="hero">
  <div class="kicker">Final phase</div>
  <h1>{title}</h1>
  <p>This desk is locked until the matching pipeline files are on disk. No sample answer is shown in their place.</p>
</div>
""",
        unsafe_allow_html=True,
    )


def _agent_text(title: str, parsed: dict | None) -> None:
    st.markdown(f"**{title}**")
    if not parsed:
        st.caption("No saved reply.")
        return
    st.write(parsed.get("explanation", ""))
    cause = str(parsed.get("cause") or "")
    color = LABEL_COLOR.get(cause, "#93A0B8")
    st.markdown(f'<span class="chip" style="color:{color}">{cause}</span> <span class="chip">{parsed.get("direction")}</span>', unsafe_allow_html=True)
    st.caption(f"Confidence {parsed.get('confidence')}")


def page_agents(cases: pd.DataFrame) -> None:
    files = sorted(RESULTS_A.glob("*.json"))
    if not files:
        _coming("Agents")
        st.code("python run_pipeline.py --steps 7 --n 50")
        return
    st.subheader("Agents")
    stems = [p.stem for p in files]
    choice = st.selectbox("Saved investigation", stems, index=len(stems) - 1)
    ticker, date = choice.rsplit("_", 1)
    a = _read_json(RESULTS_A / f"{choice}.json")
    b = _read_json(RESULTS_B / f"{choice}.json")
    c = _read_json(RESULTS_C / f"{choice}.json")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        _agent_text("A · Solo", (a or {}).get("parsed"))
    with col_b:
        st.markdown("**B · Team vote**")
        if b:
            st.write(f"Vote {b.get('vote_cause')} · {b.get('vote_direction')}")
            for name, payload in (b.get("personas") or {}).items():
                text = (payload.get("parsed") or {}).get("explanation", "")
                st.markdown(f'<div class="glass"><b>{name}</b><br>{text}</div>', unsafe_allow_html=True)
    with col_c:
        _agent_text("C · Chair", ((c or {}).get("chair") or {}).get("parsed"))
    st.caption(f"Saved case · {ticker} · {date}")
    if cases.empty:
        return
    who = provider_label()
    with st.expander(f"Call {who} for the case selected under Case Detail"):
        st.caption("Uses the configured provider and saves valid JSON.")
        if st.button("Run investigation", type="primary"):
            detail_ticker = st.session_state.get("detail_ticker")
            detail_date = st.session_state.get("detail_date")
            if not detail_ticker or not detail_date:
                st.warning("Open Case Detail once so a stock and day are selected.")
            else:
                try:
                    with st.status(f"Calling {who}…", expanded=True) as status:
                        run_investigation(str(detail_ticker), str(detail_date)[:10], log=lambda message: status.write(message))
                        status.update(label="Saved", state="complete")
                    st.cache_data.clear()
                except PipelineError as exc:
                    st.error(str(exc))


def page_debate() -> None:
    files = sorted(RESULTS_C.glob("*.json"))
    if not files:
        _coming("Debate")
        st.code("python run_pipeline.py --steps 7 --n 50")
        return
    st.subheader("Debate")
    choice = st.selectbox("Saved debate", [p.stem for p in files], index=len(files) - 1)
    payload = _read_json(RESULTS_C / f"{choice}.json") or {}
    for title, block in (("Round 1", payload.get("round1")), ("Round 2", payload.get("round2"))):
        st.markdown(f"#### {title}")
        for name, item in (block or {}).items():
            text = ((item or {}).get("parsed") or {}).get("explanation", "")
            st.markdown(f'<div class="glass"><b>{name}</b><br>{text}</div>', unsafe_allow_html=True)
    chair = ((payload.get("chair") or {}).get("parsed") or {}).get("explanation", "")
    st.markdown(f'<div class="glass"><b>Chair</b><br>{chair}</div>', unsafe_allow_html=True)


def page_about() -> None:
    st.subheader("About")
    st.write("A reproducible case file for unusual NSE sessions.")
    st.markdown(
        '<span class="chip">Python</span><span class="chip">pandas</span><span class="chip">yfinance</span>'
        '<span class="chip">scikit-learn</span><span class="chip">Plotly</span><span class="chip">Streamlit</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="bento">
  <div class="glass"><h3>Data provenance</h3><p>Yahoo daily prices aligned to the Nifty calendar.</p></div>
  <div class="glass"><h3>Method</h3><p>Published thresholds, no future rows, date-based evaluation.</p></div>
  <div class="glass"><h3>Scope</h3><p>Educational analysis. No recommendations or profit claims.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.expander("Method FAQ"):
        st.markdown(
            "**What is a case?**  \nA move at least 2.5× prior 20-day volatility.\n\n"
            "**Is the accuracy causal proof?**  \nNo. It shows the forest reproduced the label rules.\n\n"
            "**Does the site recommend trades?**  \nNo."
        )


def main() -> None:
    st.set_page_config(page_title="MarketForensics", page_icon="MF", layout="wide")
    inject_css()
    st.sidebar.markdown(
        '<div class="brand-lockup"><strong>MARKETFORENSICS</strong>'
        '<span>Evidence before explanation.</span></div>',
        unsafe_allow_html=True,
    )
    if "nav" not in st.session_state:
        st.session_state.nav = "Home"
    page = st.sidebar.radio("Pages", PAGES, key="nav")
    cases = load_cases()
    metrics = _read_json(RESULTS / "ml_baseline_metrics.json")
    _tape(cases)
    try:
        if page == "Home":
            page_home(cases, metrics)
        elif page == "Dashboard":
            render_dashboard(cases, metrics)
        elif page == "Market Overview":
            page_market(cases)
        elif page == "Case Explorer":
            page_explorer(cases)
        elif page == "Case Detail":
            page_detail(cases)
        elif page == "Insights":
            page_insights(cases)
        elif page == "Model Lab":
            page_model(metrics)
        elif page == "Agents":
            page_agents(cases)
        elif page == "Debate":
            page_debate()
        else:
            page_about()
    except PipelineError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error("This page failed while reading saved files.")
        st.caption(str(exc))
    _footer()
