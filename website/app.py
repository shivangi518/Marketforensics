"""Public-facing MarketForensics website.

Run from the project root:
    python website/app.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from flask import Flask, Response, abort, render_template, request
from plotly.offline import get_plotlyjs
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATA = ROOT / "data"
FEATURES = DATA / "features" / "case_features.csv"
PROCESSED = DATA / "processed"
METRICS = DATA / "results" / "ml_baseline_metrics.json"
RESULTS_A = DATA / "results" / "version_a"
MARKET_STRIP = DATA / "market_strip.json"

app = Flask(__name__)

COLORS = {
    "navy": "#0B1220",
    "blue": "#3B5BFF",
    "teal": "#0F9F92",
    "amber": "#C98A16",
    "slate": "#64748B",
    "red": "#C94B57",
    "grid": "#E5EAF2",
}

LABEL_COLORS = {
    "market_wide": COLORS["blue"],
    "stock_specific": COLORS["amber"],
    "volume_shock": COLORS["teal"],
    "unknown": COLORS["slate"],
}


@lru_cache(maxsize=1)
def load_cases() -> pd.DataFrame:
    if not FEATURES.exists():
        return pd.DataFrame()
    frame = pd.read_csv(FEATURES)
    frame["date"] = frame["date"].astype(str).str.slice(0, 10)
    return frame


@lru_cache(maxsize=1)
def load_metrics() -> dict:
    if not METRICS.exists():
        return {}
    return json.loads(METRICS.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def load_prices(ticker: str) -> pd.DataFrame:
    if ticker not in set(load_cases()["ticker"].astype(str).unique()):
        raise KeyError(ticker)
    path = PROCESSED / f"{ticker}.csv"
    if not path.exists():
        raise KeyError(ticker)
    return pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()


@lru_cache(maxsize=1)
def load_market_snapshot() -> list[dict]:
    """Latest saved close, return and recent path for each processed stock."""
    snapshot = []
    for path in sorted(PROCESSED.glob("*.csv")):
        if path.stem.endswith("_returns"):
            continue
        try:
            frame = pd.read_csv(path, parse_dates=["Date"]).sort_values("Date")
        except (OSError, ValueError):
            continue
        if frame.empty or "Close" not in frame:
            continue
        valid = frame.dropna(subset=["Close"]).tail(24)
        if valid.empty:
            continue
        last = valid.iloc[-1]
        change = last.get("return_pct")
        if pd.isna(change) and len(valid) > 1:
            change = (float(valid["Close"].iloc[-1]) / float(valid["Close"].iloc[-2]) - 1) * 100
        snapshot.append(
            {
                "ticker": "NIFTY 50" if path.stem == "NSEI" else path.stem,
                "stem": path.stem,
                "close": float(last["Close"]),
                "change": float(change) if pd.notna(change) else 0.0,
                "date": str(pd.Timestamp(last["Date"]).date()),
                "spark": [round(float(value), 4) for value in valid["Close"].tolist()],
            }
        )
    return snapshot


@lru_cache(maxsize=1)
def load_cross_market_strip() -> tuple[list[dict], str | None]:
    if not MARKET_STRIP.exists():
        return [], None
    try:
        payload = json.loads(MARKET_STRIP.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], None
    return payload.get("items") or [], payload.get("updated_at_utc")


def figure_json(fig: go.Figure) -> str:
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#273449", "size": 12},
        margin={"l": 38, "r": 20, "t": 48, "b": 38},
        hoverlabel={"bgcolor": COLORS["navy"], "font_color": "white"},
        legend={"orientation": "h", "y": 1.12},
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def overview_context() -> dict:
    cases = load_cases()
    metrics = load_metrics()
    days = 0
    sample = PROCESSED / "RELIANCE.NS.csv"
    if sample.exists():
        days = max(0, sum(1 for _ in sample.open(encoding="utf-8")) - 1)
    return {
        "case_count": len(cases),
        "stock_count": int(cases["ticker"].nunique()) if not cases.empty else 0,
        "accuracy": float(metrics.get("accuracy", 0)) * 100,
        "days": days,
        "last_date": str(cases["date"].max()) if not cases.empty else "—",
    }


def empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, annotations=[{"text": "Pipeline output unavailable", "showarrow": False}])
    return fig


@app.context_processor
def shared_context() -> dict:
    snapshot = load_market_snapshot()
    market_strip, market_updated = load_cross_market_strip()
    if not market_strip:
        preferred = ["NIFTY 50", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
        by_ticker = {item["ticker"]: item for item in snapshot}
        market_strip = [by_ticker[name] for name in preferred if name in by_ticker]
    return {
        "active_path": request.path,
        "overview": overview_context(),
        "market_strip": market_strip,
        "market_updated": market_updated,
        "search_tickers": sorted(
            item["ticker"] for item in snapshot if item["ticker"] != "NIFTY 50"
        ),
    }


@app.get("/plotly.js")
@lru_cache(maxsize=1)
def plotly_js() -> Response:
    return Response(get_plotlyjs(), mimetype="application/javascript")


@app.get("/")
def overview():
    cases = load_cases()
    if cases.empty:
        label_fig = monthly_fig = stock_fig = empty_figure("No cases")
    else:
        counts = cases["label"].value_counts()
        label_fig = go.Figure(
            go.Pie(
                labels=counts.index,
                values=counts.values,
                hole=0.62,
                marker_colors=[LABEL_COLORS.get(str(name), COLORS["slate"]) for name in counts.index],
                textinfo="label+percent",
            )
        )
        label_fig.update_layout(title="Case labels")

        months = cases.assign(month=cases["date"].str.slice(0, 7)).groupby("month").size()
        monthly_fig = go.Figure(
            go.Scatter(
                x=months.index,
                y=months.values,
                mode="lines",
                line={"color": COLORS["blue"], "width": 2.5},
                fill="tozeroy",
                fillcolor="rgba(59,91,255,.08)",
            )
        )
        monthly_fig.update_layout(title="Cases by month", yaxis_title="Cases")

        stocks = cases["ticker"].value_counts().head(12).sort_values()
        stock_fig = go.Figure(
            go.Bar(x=stocks.values, y=stocks.index, orientation="h", marker_color=COLORS["teal"])
        )
        stock_fig.update_layout(title="Most active stocks", xaxis_title="Cases")

        activity = (
            cases.groupby("ticker")
            .agg(case_count=("ticker", "size"), median_move=("return_pct", "median"))
            .reset_index()
        )
        activity_fig = go.Figure(
            go.Treemap(
                labels=activity["ticker"],
                parents=[""] * len(activity),
                values=activity["case_count"],
                marker={
                    "colors": activity["median_move"],
                    "colorscale": [[0, "#C9656E"], [0.5, "#CBD5E1"], [1, "#2E9F91"]],
                    "cmid": 0,
                    "colorbar": {"title": "Median move %"},
                },
                customdata=activity[["case_count", "median_move"]],
                hovertemplate="%{label}<br>Cases: %{customdata[0]}<br>Median move: %{customdata[1]:+.2f}%<extra></extra>",
            )
        )
        activity_fig.update_layout(title="Case activity map")

    snapshot = [item for item in load_market_snapshot() if item["ticker"] != "NIFTY 50"]
    dated = [item for item in snapshot if item["change"] is not None]
    gainers = sorted(dated, key=lambda item: item["change"], reverse=True)[:5]
    losers = sorted(dated, key=lambda item: item["change"])[:5]

    return render_template(
        "overview.html",
        label_chart=figure_json(label_fig),
        monthly_chart=figure_json(monthly_fig),
        stock_chart=figure_json(stock_fig),
        activity_chart=figure_json(activity_fig if not cases.empty else empty_figure("Activity")),
        gainers=gainers,
        losers=losers,
    )


@app.get("/cases")
def cases_page():
    cases = load_cases()
    if cases.empty:
        return render_template("cases.html", rows=[], tickers=[], labels=[], selected={})

    ticker = request.args.get("ticker", "")
    label = request.args.get("label", "")
    min_move_text = request.args.get("min_move", "0")
    try:
        min_move = max(0.0, float(min_move_text))
    except ValueError:
        min_move = 0.0

    view = cases
    if ticker:
        view = view[view["ticker"] == ticker]
    if label:
        view = view[view["label"] == label]
    view = view[view["return_pct"].abs() >= min_move]
    view = view.sort_values("date", ascending=False).head(250)

    rows = view[
        ["ticker", "date", "return_pct", "label", "vs_nifty", "volume_vs_avg20"]
    ].to_dict("records")
    snapshot = {item["ticker"]: item for item in load_market_snapshot()}
    for row in rows:
        row["spark"] = (snapshot.get(row["ticker"]) or {}).get("spark", [])
    return render_template(
        "cases.html",
        rows=rows,
        tickers=sorted(cases["ticker"].unique()),
        labels=sorted(cases["label"].unique()),
        selected={"ticker": ticker, "label": label, "min_move": min_move},
        total=len(view),
    )


@app.get("/case")
def case_detail():
    ticker = request.args.get("ticker", "")
    date_text = request.args.get("date", "")
    cases = load_cases()
    match = cases[(cases["ticker"] == ticker) & (cases["date"] == date_text)]
    if match.empty:
        abort(404)
    row = match.iloc[0].to_dict()
    prices = load_prices(ticker)
    event = pd.Timestamp(date_text)
    range_key = request.args.get("range", "3m").lower()
    days = {"1m": 31, "3m": 92, "1y": 366, "5y": 1827}.get(range_key)
    if days is None:
        window = prices
        range_key = "max"
    else:
        window = prices.loc[event - pd.Timedelta(days=days) : event + pd.Timedelta(days=days)]

    window = window.copy()
    window["MA20"] = window["Close"].rolling(20).mean()
    window["MA50"] = window["Close"].rolling(50).mean()
    delta = window["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    window["RSI"] = 100 - (100 / (1 + gain / loss.replace(0, pd.NA)))

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.67, 0.22, 0.11],
        vertical_spacing=0.035,
    )
    fig.add_trace(
        go.Candlestick(
            x=window.index,
            open=window["Open"],
            high=window["High"],
            low=window["Low"],
            close=window["Close"],
            increasing_line_color=COLORS["teal"],
            decreasing_line_color=COLORS["red"],
            name="OHLC",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=window.index,
            y=window["Close"],
            mode="lines",
            name="Line",
            visible="legendonly",
            line={"color": COLORS["blue"], "width": 2},
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=window.index, y=window["MA20"], name="MA20", visible="legendonly", line={"color": COLORS["amber"]}),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=window.index, y=window["MA50"], name="MA50", visible="legendonly", line={"color": COLORS["slate"]}),
        row=1,
        col=1,
    )
    volume_colors = [COLORS["teal"] if close >= open_ else COLORS["red"] for close, open_ in zip(window["Close"], window["Open"])]
    fig.add_trace(
        go.Bar(x=window.index, y=window["Volume"], name="Volume", marker_color=volume_colors),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=window.index, y=window["RSI"], name="RSI (14)", visible="legendonly", line={"color": COLORS["blue"]}),
        row=3,
        col=1,
    )
    if event in window.index:
        fig.add_vline(x=event, line_color=COLORS["blue"], line_width=2)
    fig.update_layout(
        title=f"{ticker} around {date_text}",
        xaxis_rangeslider_visible=False,
        height=650,
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)

    return render_template(
        "case_detail.html",
        case=row,
        price_chart=figure_json(fig),
        selected_range=range_key,
        ranges=[("1m", "1M"), ("3m", "3M"), ("1y", "1Y"), ("5y", "5Y"), ("max", "Max")],
    )


@app.get("/model")
def model_page():
    metrics = load_metrics()
    if not metrics:
        return render_template("model.html", metrics={}, confusion_chart=None, importance_chart=None)

    labels = metrics["confusion_matrix_labels"]
    confusion = go.Figure(
        go.Heatmap(
            z=metrics["confusion_matrix"],
            x=labels,
            y=labels,
            colorscale=[[0, "#EEF2FF"], [1, COLORS["blue"]]],
            text=metrics["confusion_matrix"],
            texttemplate="%{text}",
            hovertemplate="True: %{y}<br>Predicted: %{x}<br>Cases: %{z}<extra></extra>",
        )
    )
    confusion.update_layout(title="Test confusion matrix", xaxis_title="Predicted", yaxis_title="True")

    importance = metrics.get("permutation_importance_mean", {})
    ordered = sorted(importance.items(), key=lambda item: item[1])
    importance_fig = go.Figure(
        go.Bar(
            x=[value for _, value in ordered],
            y=[name for name, _ in ordered],
            orientation="h",
            marker_color=COLORS["blue"],
        )
    )
    importance_fig.update_layout(title="Permutation importance", xaxis_title="Accuracy decrease")

    return render_template(
        "model.html",
        metrics=metrics,
        confusion_chart=figure_json(confusion),
        importance_chart=figure_json(importance_fig),
    )


@app.get("/export/case")
def export_case():
    ticker = request.args.get("ticker", "")
    date_text = request.args.get("date", "")
    cases = load_cases()
    match = cases[(cases["ticker"] == ticker) & (cases["date"] == date_text)]
    if match.empty:
        abort(404)
    response = Response(match.to_csv(index=False), mimetype="text/csv")
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{ticker.replace("&", "_")}_{date_text}_case.csv"'
    )
    return response


@app.get("/investigations")
def investigations_page():
    items = []
    for path in sorted(RESULTS_A.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        parsed = payload.get("parsed") or {}
        items.append(
            {
                "ticker": payload.get("ticker"),
                "date": payload.get("date"),
                "cause": parsed.get("cause"),
                "confidence": parsed.get("confidence"),
                "direction": parsed.get("direction"),
                "explanation": parsed.get("explanation"),
            }
        )
    return render_template("investigations.html", items=items)


@app.get("/methodology")
def methodology_page():
    return render_template("methodology.html")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
