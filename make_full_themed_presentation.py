"""Create the complete final presentation in the same theme as the midterm."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from pptx import Presentation

from match_midterm_theme import (
    ASSETS,
    DOWNLOADS,
    rebuild_title,
    replace_chart,
    style_slide,
)


SOURCE = DOWNLOADS / "FINAL Term Presentation CAPSTONE.pptx"
OUTPUT = DOWNLOADS / "FINAL Term Presentation CAPSTONE Full Same Theme.pptx"
NOTES_FILE = DOWNLOADS / "FINAL Term Presentation Speaking Notes.md"
BASE = Path(__file__).resolve().parent


SPEAKER_NOTES = [
    """Good morning. My project is MarketForensics. It studies unusually large daily movements in NSE stocks. The system uses real historical prices, transparent detection rules, machine learning, AI agents, and an interactive dashboard. It is an educational investigation tool and not a trading recommendation.""",
    """At the midterm, data collection, case detection, feature engineering, the Random Forest, and the first dashboard were ready. After the midterm, I completed the full eight-step pipeline, integrated three Groq agent designs, added caching and validation, evaluated their direction calls, improved the dashboard, corrected Figure 7, and completed the report.""",
    """The main question is: when a stock moves much more than its own recent volatility, can the available price and volume evidence tell us whether the movement looks market-wide, stock-specific, volume-driven, or still unclear? The objective is explanation and investigation, not price prediction or buy/sell advice.""",
    """This is the final system flow. Yahoo Finance prices are downloaded and cleaned. Unusual days are detected. EDA and features are produced. A Random Forest learns the written label rules. Then three AI designs investigate selected cases. Finally, their direction statements are compared with later returns, and Streamlit displays the saved outputs.""",
    """The final cleaned universe contains 31 NSE stocks plus the Nifty index. Each series has 1,172 trading days from January 2022 to September 2026. The final rerun found 1,332 unusual cases. Titan has 51 cases, January 2025 is the busiest month, and the median absolute move is 3.67 percent.""",
    """A case is detected when the absolute daily return is at least 2.5 times the stock's prior 20-day volatility. The baseline is shifted by one day, so the event return does not make its own threshold larger. Features use only information available through the event-day close, which prevents future leakage.""",
    """The model uses returns, volatility, volume relative to average, moving-average information, momentum, the gap versus Nifty, and weekday. Labels follow a clear order. First market-wide, then stock-specific, then volume shock, otherwise unknown. The first matching rule wins.""",
    """These charts summarize the unusual cases. Events are distributed across the whole sample, not concentrated in only one crash period. Titan has the highest count, and January 2025 has the largest monthly count. This supports using a stock-specific volatility threshold rather than a fixed percentage rule.""",
    """The Random Forest contains 200 trees. It was trained on 938 older cases and tested on 384 later cases. The date split prevents the same calendar period from appearing in both sets. Test accuracy is 91.7 percent, with strong performance for stock-specific cases but only seven volume-shock examples in the test set.""",
    """Permutation importance shows that the gap versus Nifty is the dominant feature. Return, volatility, and volume ratio follow. The important limitation is that the labels were created from some of these same variables. Therefore, 91.7 percent means the model learned my labelling rules on later dates. It does not prove a real news cause.""",
    """The original Figure 7 was blank because volume percentage change produced infinite values when volume was zero. I corrected it by using log-volume change after removing non-positive values. Most correlations are close to zero, so another stock's volume change has little linear relationship with a stock's return.""",
    """After the midterm, I implemented three AI investigation designs. Version A is one solo explanation. Version B uses numbers, news, and skeptic roles, then takes a vote. Version C lets the same roles debate for two rounds and uses a chair to synthesize the result. Every output must contain cause, confidence, direction, and explanation in JSON.""",
    """This is one saved example for Titan on 10 August 2026. The solo agent classified the event as stock-specific with 80 percent confidence. The explanation refers only to supplied price, market, and volume evidence. It is still a model-generated interpretation, not a confirmed corporate cause.""",
    """I evaluated whether each saved up or down direction matched the sign of the 30-day forward return. Solo matched 3 of 14, team vote matched 1 of 5, and debate matched 3 of 13. The samples are small and intervals are wide. Debate did not materially improve direction matching. This is not a profit backtest.""",
    """The final Streamlit terminal has pages for the home summary, market overview, case explorer, case detail, insights, model results, agents, debate, and backtest. It reads saved real files only. Missing outputs produce a friendly instruction instead of an error or fake result. Every page displays the educational-use disclaimer.""",
    """The project has important limitations. Daily bars cannot prove an intraday or corporate cause. Labels are heuristic categories. Historical headlines are only attached when date-matched. Groq can be wrong and is rate-limited. The direction evaluation contains few cases. Therefore, this system must not be interpreted as a trading signal.""",
    """All planned modules are now complete: data collection, cleaning, anomaly detection, EDA, feature engineering, Random Forest, explainability, AI agents, evaluation, dashboard, and final documentation. The live demonstration starts with the command streamlit run app.py.""",
    """In conclusion, MarketForensics provides a reproducible investigation workflow from real prices to cases, labels, model results, AI explanations, and honest evaluation. The main contribution is not a claim of profitable prediction. It is a transparent system that shows what the evidence supports and what remains uncertain.""",
    """These are the main data, software, and research references used in the project. Thank you. I am ready for questions.""",
]


def make_light_backtest() -> Path:
    summary = json.loads((BASE / "data/results/backtest_summary.json").read_text(encoding="utf-8"))
    names = ["A · Solo", "B · Team", "C · Debate"]
    keys = ["A", "B", "C"]
    rates = [summary["versions"][key]["all_30d"]["win_rate"] * 100 for key in keys]
    ns = [summary["versions"][key]["all_30d"]["n"] for key in keys]
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="white")
    bars = ax.bar(names, rates, color=["#5B9BD5", "#ED7D31", "#70AD47"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("30-day direction match (%)")
    ax.set_title("Agent direction check")
    ax.grid(axis="y", alpha=0.2)
    for bar, rate, n in zip(bars, rates, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 3, f"{rate:.0f}%\nn={n}", ha="center")
    fig.tight_layout()
    path = ASSETS / "agent_backtest_light.png"
    fig.savefig(path, dpi=170, facecolor="white")
    plt.close(fig)
    return path


def set_notes(slide, text: str) -> None:
    frame = slide.notes_slide.notes_text_frame
    frame.text = text


def write_notes_markdown() -> None:
    titles = [
        "Title", "What changed after the midterm", "Problem and final objective",
        "Completed system architecture", "Final dataset and event profile",
        "Case detection and no-leakage rule", "Features and rule-based labels",
        "Exploratory findings", "Random Forest test results", "What the model learned",
        "Corrected Figure 7", "Completed Groq agent designs",
        "Example saved AI investigation", "Agent direction check",
        "Final Streamlit terminal", "Limitations", "Final completion status",
        "Conclusion", "References",
    ]
    lines = ["# MarketForensics final presentation speaking notes", ""]
    for index, (title, note) in enumerate(zip(titles, SPEAKER_NOTES), start=1):
        lines.extend([f"## Slide {index}: {title}", note, ""])
    NOTES_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    from match_midterm_theme import make_light_charts

    confusion, importance = make_light_charts()
    backtest = make_light_backtest()
    prs = Presentation(SOURCE)
    rebuild_title(prs.slides[0])
    for number, slide in enumerate(list(prs.slides)[1:], start=2):
        if number == 9:
            replace_chart(slide, confusion)
        elif number == 10:
            replace_chart(slide, importance)
        elif number == 14:
            replace_chart(slide, backtest)
        style_slide(slide, number)
    for slide, note in zip(prs.slides, SPEAKER_NOTES):
        set_notes(slide, note)
    prs.save(OUTPUT)
    write_notes_markdown()
    print(OUTPUT)
    print(NOTES_FILE)
    print(f"slides={len(prs.slides)} notes={len(SPEAKER_NOTES)}")


if __name__ == "__main__":
    main()
