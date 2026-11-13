"""Shared settings for MarketForensics (NSE / Nifty focus)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Default stock (Yahoo Finance NSE suffix). Prices still come from Yahoo, not from a fixture.
DEFAULT_TICKER = "RELIANCE.NS"
NIFTY_INDEX = "^NSEI"
NIFTY_STEM = "NSEI"
START_DATE = "2022-01-01"

# Big-move rule: |return| >= K * prior 20-day volatility (baseline shifted by 1 day)
K_BIG_MOVE = 2.5
VOL_WINDOW = 20
CASE_BEFORE = 5
CASE_AFTER = 5

# First-run universe size (raise toward 50 when downloads are stable)
UNIVERSE_LIMIT = 30

# Nifty-50 style universe (Yahoo tickers). Order is stable for beginners.
NIFTY50_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS",
    "ITC.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "BAJFINANCE.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "HCLTECH.NS",
    "AXISBANK.NS",
    "ASIANPAINT.NS",
    "MARUTI.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
    "NESTLEIND.NS",
    "POWERGRID.NS",
    "NTPC.NS",
    "M&M.NS",
    "TATAMOTORS.NS",
    "JSWSTEEL.NS",
    "TATASTEEL.NS",
    "TECHM.NS",
    "COALINDIA.NS",
    "BAJAJFINSV.NS",
    "GRASIM.NS",
    "HINDALCO.NS",
    "CIPLA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "APOLLOHOSP.NS",
    "BPCL.NS",
    "DIVISLAB.NS",
    "HEROMOTOCO.NS",
    "BRITANNIA.NS",
    "TATACONSUM.NS",
    "ADANIPORTS.NS",
    "ONGC.NS",
    "SBILIFE.NS",
    "HDFCLIFE.NS",
    "ADANIENT.NS",
    "INDUSINDBK.NS",
    "BEL.NS",
    "TRENT.NS",
    "JIOFIN.NS",
]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
CASES = DATA / "cases"
CASES_JSON = CASES / "json"
FEATURES = DATA / "features"
PLOTS = DATA / "plots"
PLOTS_EDA = PLOTS / "eda"
REPORTS = DATA / "reports"
NEWS = DATA / "news"
AGENT_CACHE = DATA / "agent_cache"
RESULTS = DATA / "results"
RESULTS_A = RESULTS / "version_a"
RESULTS_B = RESULTS / "version_b"
RESULTS_C = RESULTS / "version_c"
MODELS = ROOT / "models"


def ensure_data_dirs() -> None:
    for path in (
        RAW,
        PROCESSED,
        CASES,
        CASES_JSON,
        FEATURES,
        PLOTS,
        PLOTS_EDA,
        REPORTS,
        NEWS,
        AGENT_CACHE,
        RESULTS_A,
        RESULTS_B,
        RESULTS_C,
        MODELS,
    ):
        path.mkdir(parents=True, exist_ok=True)


# Cause labels (first match wins). Documented thresholds, in percentage points / ratio.
LABEL_MARKET_ABS = 1.5       # |Nifty return| on the event day
LABEL_STOCK_VS = 2.0         # |stock return − Nifty return|
LABEL_VOLUME_RATIO = 2.0     # volume / 20-day average volume

GROQ_MODEL_DEFAULT = "openai/gpt-oss-20b"
GEMINI_MODEL_DEFAULT = "gemini-2.5-flash"


class PipelineError(RuntimeError):
    """Stop a step. The message says what is missing and the command to create it."""


def ticker_stem(ticker: str) -> str:
    """CSV name without extension. ^NSEI is stored as NSEI.csv."""
    text = str(ticker).strip()
    if text in {NIFTY_INDEX, NIFTY_STEM}:
        return NIFTY_STEM
    return text.replace("/", "_")


def universe_tickers(limit: int | None = UNIVERSE_LIMIT) -> list[str]:
    if limit is None:
        return list(NIFTY50_TICKERS)
    return NIFTY50_TICKERS[:limit]
