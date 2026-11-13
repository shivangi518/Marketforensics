"""Plotly figures. Series must already be real prices or saved metrics."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from marketforensics.theme import LABEL_COLOR, PALETTE

NAVY = PALETTE["bg"]
AMBER = PALETTE["amber"]
TEAL = PALETTE["green"]
INK = PALETTE["ink"]
MUTED = PALETTE["muted"]
GRID = PALETTE["grid"]


def _base(fig: go.Figure, title: str, height: int) -> go.Figure:
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,16,28,0.55)",
        font=dict(color=INK, family="IBM Plex Sans, Segoe UI, sans-serif"),
        margin=dict(l=10, r=10, t=48, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def candlestick(prices: pd.DataFrame, cases: pd.DataFrame, ticker: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04)
    fig.add_trace(
        go.Candlestick(
            x=prices.index,
            open=prices["Open"],
            high=prices["High"],
            low=prices["Low"],
            close=prices["Close"],
            name="Price",
            increasing_line_color=PALETTE["green"],
            decreasing_line_color=PALETTE["red"],
        ),
        row=1,
        col=1,
    )
    marks = cases[cases["ticker"].astype(str) == ticker].copy()
    if not marks.empty and "date" in marks.columns:
        marks["date"] = pd.to_datetime(marks["date"])
        joined = marks.merge(prices[["Close"]].rename_axis("date").reset_index(), on="date", how="inner")
        up = joined[joined["return_pct"] >= 0]
        down = joined[joined["return_pct"] < 0]
        if not up.empty:
            fig.add_trace(
                go.Scatter(x=up["date"], y=up["Close"], mode="markers", name="Up case", marker=dict(size=9, color=PALETTE["green"], line=dict(width=1, color="#FFFFFF"))),
                row=1,
                col=1,
            )
        if not down.empty:
            fig.add_trace(
                go.Scatter(x=down["date"], y=down["Close"], mode="markers", name="Down case", marker=dict(size=9, color=PALETTE["red"], line=dict(width=1, color="#FFFFFF"))),
                row=1,
                col=1,
            )
    if "Volume" in prices.columns:
        fig.add_trace(go.Bar(x=prices.index, y=prices["Volume"], name="Volume", marker_color="#35506E"), row=2, col=1)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(xaxis_rangeslider_visible=True)
    return _base(fig, f"{ticker} price, volume, and case days", 560)


def price_volume(prices: pd.DataFrame, event: pd.Timestamp, ticker: str) -> go.Figure:
    window = prices.loc[event - pd.Timedelta(days=50) : event + pd.Timedelta(days=20)]
    if window.empty:
        window = prices.tail(80)
    return candlestick(window, pd.DataFrame(columns=["ticker", "date", "return_pct"]), ticker)


def rebase(stock: pd.DataFrame, nifty: pd.DataFrame, event: pd.Timestamp | None, ticker: str) -> go.Figure | None:
    if event is None:
        frame = pd.concat({"stock": stock["Close"], "nifty": nifty["Close"]}, axis=1).dropna()
        title = f"{ticker} vs Nifty, growth of 100"
    else:
        start = event - pd.Timedelta(days=40)
        end = event + pd.Timedelta(days=15)
        frame = pd.concat({"stock": stock.loc[start:end, "Close"], "nifty": nifty.loc[start:end, "Close"]}, axis=1).dropna()
        title = "Growth of 100 around the case"
    if len(frame) < 5 or float(frame["stock"].iloc[0]) == 0 or float(frame["nifty"].iloc[0]) == 0:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame.index, y=frame["stock"] / frame["stock"].iloc[0] * 100, name=ticker, line=dict(color=AMBER, width=2)))
    fig.add_trace(go.Scatter(x=frame.index, y=frame["nifty"] / frame["nifty"].iloc[0] * 100, name="Nifty", line=dict(color=PALETTE["cyan"], width=2)))
    if event is not None:
        fig.add_vline(x=event, line_dash="dash", line_color=PALETTE["red"])
    fig.update_layout(yaxis_title="Index = 100")
    return _base(fig, title, 380)


def mystery_gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(score),
            number={"suffix": "%", "font": {"color": INK, "size": 28}},
            title={"text": "Unexplained share of the move", "font": {"color": MUTED, "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": MUTED},
                "bar": {"color": AMBER},
                "bgcolor": "#121A2A",
                "steps": [
                    {"range": [0, 35], "color": "#123226"},
                    {"range": [35, 65], "color": "#3A2E12"},
                    {"range": [65, 100], "color": "#3A1820"},
                ],
            },
        )
    )
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=16, r=16, t=48, b=8), font={"color": INK})
    return fig


def label_donut(counts: pd.Series) -> go.Figure:
    labels = list(counts.index.astype(str))
    fig = go.Figure(go.Pie(labels=labels, values=counts.values, hole=0.62, marker=dict(colors=[LABEL_COLOR.get(name, MUTED) for name in labels]), textinfo="label+value"))
    return _base(fig, "Label counts", 380)


def cases_per_stock(counts: pd.Series) -> go.Figure:
    ordered = counts.sort_values()
    fig = go.Figure(go.Bar(x=ordered.values, y=ordered.index.astype(str), orientation="h", marker_color=PALETTE["cyan"]))
    return _base(fig, "Cases per stock", max(420, 18 * len(ordered)))


def cases_by_month(counts: pd.Series) -> go.Figure:
    fig = go.Figure(go.Bar(x=counts.index.astype(str), y=counts.values, marker_color=PALETTE["violet"]))
    return _base(fig, "Cases by month", 360)


def moves_by_label(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, part in frame.groupby("label"):
        fig.add_trace(go.Box(y=part["return_pct"], name=str(label), marker_color=LABEL_COLOR.get(str(label), MUTED)))
    return _base(fig, "Case move by label (%)", 380)


def confusion_heatmap(matrix: list, labels: list) -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale=[[0, "#0E1624"], [1, PALETTE["amber"]]],
            text=matrix,
            texttemplate="%{text}",
            hovertemplate="true %{y}<br>predicted %{x}<br>count %{z}<extra></extra>",
        )
    )
    fig.update_yaxes(title="True label", autorange="reversed")
    fig.update_xaxes(title="Predicted")
    return _base(fig, "Test confusion matrix", 420)


def importance_bars(scores: dict) -> go.Figure:
    items = sorted(scores.items(), key=lambda item: item[1])
    fig = go.Figure(go.Bar(x=[v for _, v in items], y=[k for k, _ in items], orientation="h", marker_color=PALETTE["green"]))
    return _base(fig, "Permutation importance on the test set", 380)


def pr_bars(report: str) -> go.Figure | None:
    rows = []
    for line in report.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[0] in LABEL_COLOR:
            rows.append((parts[0], float(parts[1]), float(parts[2])))
    if not rows:
        return None
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Precision", x=[r[0] for r in rows], y=[r[1] for r in rows], marker_color=PALETTE["cyan"]))
    fig.add_trace(go.Bar(name="Recall", x=[r[0] for r in rows], y=[r[2] for r in rows], marker_color=PALETTE["amber"]))
    fig.update_layout(barmode="group", yaxis=dict(range=[0, 1.05]))
    return _base(fig, "Test precision and recall", 380)


def accuracy_gauge(accuracy: float) -> go.Figure:
    fig = go.Figure(go.Indicator(mode="gauge+number", value=accuracy * 100, number={"suffix": "%"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": PALETTE["green"]}, "bgcolor": "#121A2A"}))
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", font={"color": INK}, margin=dict(l=16, r=16, t=30, b=8))
    return fig


def win_rate_bars(summary: dict) -> go.Figure | None:
    versions = summary.get("versions") or {}
    names, rates = [], []
    for key, label in (("A", "A solo"), ("B", "B vote"), ("C", "C debate")):
        rate = ((versions.get(key) or {}).get("all_30d") or {}).get("win_rate")
        if rate is None:
            continue
        names.append(label)
        rates.append(float(rate) * 100)
    if not names:
        return None
    fig = go.Figure(go.Bar(x=names, y=rates, marker_color=[AMBER, PALETTE["cyan"], TEAL], text=[f"{v:.0f}%" for v in rates], textposition="outside"))
    fig.update_layout(yaxis=dict(range=[0, 110], title="30-day direction match %", gridcolor=GRID))
    return _base(fig, "Saved backtest rates", 360)
