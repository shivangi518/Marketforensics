"""Create the MarketForensics final-term PowerPoint from verified saved outputs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads")
ASSETS = ROOT / "docs" / "presentation_assets"
ASSETS.mkdir(parents=True, exist_ok=True)

METRICS = json.loads((ROOT / "data/results/ml_baseline_metrics.json").read_text(encoding="utf-8"))
BACKTEST = json.loads((ROOT / "data/results/backtest_summary.json").read_text(encoding="utf-8"))
TITAN = json.loads(
    (ROOT / "data/results/version_a/TITAN.NS_2026-08-10.json").read_text(encoding="utf-8")
)

NAVY = RGBColor(6, 12, 22)
PANEL = RGBColor(14, 24, 40)
PANEL_2 = RGBColor(21, 34, 53)
WHITE = RGBColor(235, 241, 249)
MUTED = RGBColor(159, 173, 194)
CYAN = RGBColor(0, 229, 255)
GREEN = RGBColor(0, 230, 118)
RED = RGBColor(255, 82, 82)
AMBER = RGBColor(255, 179, 0)
VIOLET = RGBColor(124, 77, 255)


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False, font="Aptos",
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = valign
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_bullets(slide, items, x, y, w, h, size=17, color=WHITE):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    for index, item in enumerate(items):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = item
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.level = 0
        p.space_after = Pt(8)
        p.text = "• " + p.text
    return box


def rect(slide, x, y, w, h, fill=PANEL, line=CYAN, radius=True):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.transparency = 35
    shape.line.width = Pt(1)
    return shape


def base_slide(prs, title, section=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY
    slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.12), prs.slide_height).fill.solid()
    bar = slide.shapes[-1]
    bar.fill.fore_color.rgb = CYAN
    bar.line.fill.background()
    if section:
        add_text(slide, section.upper(), 0.45, 0.2, 4.5, 0.35, 10, CYAN, True)
    add_text(slide, title, 0.45, 0.55, 12.3, 0.62, 26, WHITE, True)
    add_text(slide, "MarketForensics · Final Term Presentation", 9.4, 7.12, 3.35, 0.2, 8, MUTED, False, align=PP_ALIGN.RIGHT)
    return slide


def title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY
    slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.13))
    slide.shapes[-1].fill.solid()
    slide.shapes[-1].fill.fore_color.rgb = CYAN
    slide.shapes[-1].line.fill.background()
    add_text(slide, "MARKETFORENSICS", 0.7, 1.15, 11.9, 0.75, 34, WHITE, True)
    add_text(slide, "Explaining unusual NSE stock moves with rules, machine learning and AI agents",
             0.72, 2.05, 10.8, 0.75, 22, CYAN, False)
    rect(slide, 0.72, 3.05, 5.8, 2.1, PANEL, AMBER)
    add_text(slide, "FINAL TERM PRESENTATION", 1.02, 3.35, 5.2, 0.38, 15, AMBER, True)
    add_text(slide, "Shivangi Padhi\nEnrollment No. 24BCAHH010160\nFaculty Mentor: Mr. P Senthil Raja",
             1.02, 3.9, 5.1, 1.05, 16, WHITE)
    add_text(slide, "Department of AI & DS · November 2026", 0.72, 6.75, 6.0, 0.3, 12, MUTED)
    add_text(slide, "Educational use only.\nNot financial advice.", 9.35, 5.85, 3.1, 0.7, 15, RED, True, align=PP_ALIGN.RIGHT)


def kpi(slide, x, y, value, label, accent=CYAN):
    rect(slide, x, y, 2.75, 1.22, PANEL, accent)
    add_text(slide, value, x + 0.18, y + 0.16, 2.35, 0.47, 24, accent, True, font="Aptos Mono")
    add_text(slide, label, x + 0.18, y + 0.72, 2.35, 0.25, 11, MUTED)


def arrow(slide, x1, y1, x2, y2, color=CYAN):
    line = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(2)
    line.line.end_arrowhead = True
    return line


def add_picture(slide, path, x, y, w=None, h=None):
    path = Path(path)
    if not path.exists():
        return None
    kwargs = {}
    if w is not None:
        kwargs["width"] = Inches(w)
    if h is not None:
        kwargs["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kwargs)


def make_result_charts():
    plt.style.use("dark_background")
    labels = METRICS["confusion_matrix_labels"]
    matrix = np.array(METRICS["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(matrix, cmap="viridis")
    ax.set_xticks(range(len(labels)), [x.replace("_", "\n") for x in labels])
    ax.set_yticks(range(len(labels)), [x.replace("_", "\n") for x in labels])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", color="white", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    cm = ASSETS / "confusion_matrix.png"
    fig.savefig(cm, dpi=160, transparent=True)
    plt.close(fig)

    imp = METRICS["permutation_importance_mean"]
    items = sorted(imp.items(), key=lambda item: item[1])
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.barh([k for k, _ in items], [v for _, v in items], color="#00E5FF")
    ax.axvline(0, color="white", linewidth=0.7)
    ax.set_xlabel("Decrease in test accuracy after permutation")
    ax.set_title("Permutation importance")
    fig.tight_layout()
    importance = ASSETS / "permutation_importance.png"
    fig.savefig(importance, dpi=160, transparent=True)
    plt.close(fig)

    names = ["A · Solo", "B · Vote", "C · Debate"]
    rates = [BACKTEST["versions"][v]["all_30d"]["win_rate"] * 100 for v in ("A", "B", "C")]
    ns = [BACKTEST["versions"][v]["all_30d"]["n"] for v in ("A", "B", "C")]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(names, rates, color=["#00E5FF", "#FFB300", "#7C4DFF"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("30-day direction match (%)")
    ax.set_title("Agent direction check")
    for bar, rate, n in zip(bars, rates, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 3, f"{rate:.0f}%\nn={n}", ha="center", color="white")
    fig.tight_layout()
    bt = ASSETS / "agent_backtest.png"
    fig.savefig(bt, dpi=160, transparent=True)
    plt.close(fig)
    return cm, importance, bt


def build():
    cm, importance, bt = make_result_charts()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    title_slide(prs)

    slide = base_slide(prs, "What changed after the midterm", "Completion")
    add_bullets(slide, [
        "The eight-step pipeline now runs end to end on saved real NSE data.",
        "Groq integration is complete: solo, team-vote and debate designs write structured JSON.",
        "Agent responses are cached; invalid JSON is retried; API rate limits stop honestly.",
        "A 30-day direction check evaluates the saved agent calls without calling it a trading strategy.",
        "The Streamlit terminal now includes market, case, insight, model, agent, debate and backtest views.",
        "Figure 7 was corrected by replacing unstable volume percentage change with log-volume change.",
    ], 0.7, 1.45, 11.7, 4.9, 19)
    add_text(slide, "Midterm status: AI in progress → Final status: implemented and evaluated",
             0.7, 6.45, 11.7, 0.4, 16, GREEN, True)

    slide = base_slide(prs, "Problem and final objective", "Project")
    rect(slide, 0.7, 1.35, 5.7, 4.8, PANEL, CYAN)
    add_text(slide, "Problem", 1.0, 1.7, 4.9, 0.4, 20, CYAN, True)
    add_text(slide, "When an NSE stock moves far more than its own recent volatility, can same-day price and volume clues describe whether the event looks market-wide, stock-specific, volume-driven or still unclear?",
             1.0, 2.25, 4.9, 2.0, 19, WHITE)
    rect(slide, 6.85, 1.35, 5.7, 4.8, PANEL, AMBER)
    add_text(slide, "Final objective", 7.15, 1.7, 4.9, 0.4, 20, AMBER, True)
    add_bullets(slide, [
        "Detect unusual days without future leakage.",
        "Test a rule-learning model on later dates.",
        "Generate evidence-bounded AI case notes.",
        "Evaluate direction calls honestly.",
        "Present all saved evidence interactively.",
    ], 7.15, 2.25, 4.9, 3.25, 17)

    slide = base_slide(prs, "Completed system architecture", "Method")
    nodes = [
        ("1", "Yahoo prices", 0.55, CYAN),
        ("2", "Clean + align", 2.6, CYAN),
        ("3", "Detect cases", 4.65, AMBER),
        ("4", "EDA", 6.7, AMBER),
        ("5", "Features", 8.75, VIOLET),
        ("6", "Random Forest", 10.8, VIOLET),
    ]
    for num, name, x, color in nodes:
        rect(slide, x, 1.55, 1.75, 1.25, PANEL, color)
        add_text(slide, num, x + 0.12, 1.7, 0.28, 0.3, 14, color, True)
        add_text(slide, name, x + 0.12, 2.08, 1.5, 0.4, 13, WHITE, True)
    for left, right in zip(nodes, nodes[1:]):
        arrow(slide, left[2] + 1.75, 2.18, right[2], 2.18)
    for num, name, x, color in [
        ("7A", "Solo agent", 2.15, GREEN),
        ("7B", "Team vote", 5.0, GREEN),
        ("7C", "Debate + chair", 7.85, GREEN),
        ("8", "Direction check", 10.7, RED),
    ]:
        rect(slide, x, 4.0, 2.25, 1.35, PANEL, color)
        add_text(slide, num, x + 0.15, 4.15, 0.5, 0.3, 13, color, True)
        add_text(slide, name, x + 0.15, 4.58, 1.95, 0.4, 14, WHITE, True)
    arrow(slide, 11.68, 2.8, 3.25, 4.0, GREEN)
    arrow(slide, 4.4, 4.68, 5.0, 4.68, GREEN)
    arrow(slide, 7.25, 4.68, 7.85, 4.68, GREEN)
    arrow(slide, 10.1, 4.68, 10.7, 4.68, RED)
    add_text(slide, "Streamlit reads saved outputs; missing stages show a command, never invented data.",
             1.2, 6.2, 10.9, 0.4, 16, MUTED, False, align=PP_ALIGN.CENTER)

    slide = base_slide(prs, "Final dataset and event profile", "Data")
    kpi(slide, 0.7, 1.45, "31 + Nifty", "cleaned stock universe", CYAN)
    kpi(slide, 3.75, 1.45, "1,172", "trading days per series", CYAN)
    kpi(slide, 6.8, 1.45, "1,332", "final detected cases", AMBER)
    kpi(slide, 9.85, 1.45, "3.67%", "median absolute case move", AMBER)
    add_bullets(slide, [
        "Date range: 3 January 2022 to 30 September 2026.",
        "Titan has the most cases in the final rerun: 51.",
        "Busiest month: January 2025, with 47 cases.",
        "On 98% of cases, the stock moved more than Nifty in absolute terms.",
        "Largest rise: Bajaj Finance +10.63%. Largest fall: NTPC −15.45%.",
    ], 0.9, 3.25, 11.5, 2.8, 18)
    add_text(slide, "Final rerun note: this supersedes the earlier midterm snapshot.",
             0.9, 6.45, 11.2, 0.3, 13, RED, True)

    slide = base_slide(prs, "Case detection and no-leakage rule", "Method")
    rect(slide, 0.8, 1.45, 5.35, 2.0, PANEL, AMBER)
    add_text(slide, "|daily return| ≥ 2.5 × prior 20-day volatility",
             1.1, 2.03, 4.75, 0.6, 22, AMBER, True, font="Aptos Mono", align=PP_ALIGN.CENTER)
    rect(slide, 6.75, 1.45, 5.75, 2.0, PANEL, CYAN)
    add_text(slide, "The 20-day baseline is shifted by one day.",
             7.1, 1.85, 5.05, 0.5, 20, CYAN, True, align=PP_ALIGN.CENTER)
    add_text(slide, "The event return is not allowed to inflate its own threshold.",
             7.1, 2.48, 5.05, 0.48, 15, WHITE, align=PP_ALIGN.CENTER)
    add_bullets(slide, [
        "Features use observations available through the event-day close only.",
        "Prices are aligned to the Nifty calendar; non-positive closes are removed.",
        "No forward-filling and no post-event return enters model training.",
        "Train and test are separated by calendar date.",
    ], 1.0, 4.05, 11.2, 2.2, 18)

    slide = base_slide(prs, "Features and rule-based labels", "Method")
    rect(slide, 0.7, 1.4, 5.95, 4.9, PANEL, CYAN)
    add_text(slide, "Eight model features", 1.0, 1.75, 5.2, 0.4, 20, CYAN, True)
    add_bullets(slide, [
        "Daily return and 5-day return",
        "20-day volatility",
        "Volume ÷ 20-day average volume",
        "20-day moving average and above/below flag",
        "5-day momentum",
        "Stock return minus Nifty return",
        "Day of week",
    ], 1.0, 2.3, 5.2, 3.5, 16)
    rect(slide, 6.9, 1.4, 5.75, 4.9, PANEL, AMBER)
    add_text(slide, "Label order", 7.2, 1.75, 5.0, 0.4, 20, AMBER, True)
    add_bullets(slide, [
        "market_wide: |Nifty| ≥ 1.5%",
        "stock_specific: |stock − Nifty| ≥ 2.0%",
        "volume_shock: volume ratio ≥ 2.0×",
        "unknown: no earlier rule matched",
    ], 7.2, 2.3, 5.0, 2.5, 17)
    add_text(slide, "First matching rule wins.", 7.2, 5.35, 4.8, 0.35, 15, RED, True)

    plot_dir = ROOT / "data/plots/eda"
    slide = base_slide(prs, "Exploratory findings from real prices", "Results")
    add_picture(slide, plot_dir / "big_moves_per_stock.png", 0.55, 1.35, w=6.1)
    add_picture(slide, plot_dir / "big_moves_by_month.png", 6.8, 1.35, w=5.95)
    add_text(slide, "Cases occur throughout the sample—not only during one crash period.",
             0.8, 6.35, 11.8, 0.35, 15, MUTED, align=PP_ALIGN.CENTER)

    slide = base_slide(prs, "Random Forest test results", "Results")
    kpi(slide, 0.65, 1.35, "200", "trees", VIOLET)
    kpi(slide, 3.7, 1.35, "938", "training cases", VIOLET)
    kpi(slide, 6.75, 1.35, "384", "later test cases", CYAN)
    kpi(slide, 9.8, 1.35, "91.7%", "test accuracy", GREEN)
    add_picture(slide, cm, 0.8, 2.9, w=6.0)
    add_bullets(slide, [
        "Train ends: 9 May 2025",
        "Test begins: 12 May 2025",
        "Stock-specific recall: 0.97",
        "Market-wide recall: 0.72",
        "Volume-shock test support: only 7 cases",
    ], 7.25, 3.15, 4.9, 2.7, 17)

    slide = base_slide(prs, "What the model learned", "Explainability")
    add_picture(slide, importance, 0.65, 1.35, w=6.6)
    rect(slide, 7.55, 1.55, 5.0, 4.8, PANEL, RED)
    add_text(slide, "Honest interpretation", 7.9, 1.9, 4.3, 0.45, 20, RED, True)
    add_text(slide, "vs_nifty dominates permutation importance (≈0.46). Return, volatility and volume ratio follow.",
             7.9, 2.55, 4.25, 1.05, 17, WHITE)
    add_text(slide, "The labels were built from some of the same numbers the model sees. Therefore 91.7% means the forest reproduced the written rules on later dates—not that it discovered or verified a news cause.",
             7.9, 3.85, 4.25, 1.7, 17, AMBER, True)

    slide = base_slide(prs, "Corrected Figure 7: return vs volume correlation", "EDA correction")
    add_picture(slide, plot_dir / "return_vs_volume_corr_heatmap.png", 0.65, 1.25, w=7.75)
    add_bullets(slide, [
        "The midterm image was blank because volume percentage change produced infinities on zero-volume values.",
        "The final figure uses log-volume change after removing non-positive volume.",
        "Values are mostly close to zero: another stock's volume change has little linear relation with a stock's return.",
        "This is descriptive correlation, not causality.",
    ], 8.75, 1.65, 3.9, 4.7, 16)

    slide = base_slide(prs, "Completed Groq agent designs", "Generative AI")
    for title, subtitle, x, color in [
        ("A · Solo", "One evidence-bounded explanation", 0.65, CYAN),
        ("B · Team", "Numbers, news and skeptic roles; majority vote", 4.45, AMBER),
        ("C · Debate", "Two rounds plus a chair synthesis", 8.25, VIOLET),
    ]:
        rect(slide, x, 1.55, 3.45, 3.5, PANEL, color)
        add_text(slide, title, x + 0.25, 1.95, 2.95, 0.45, 21, color, True)
        add_text(slide, subtitle, x + 0.25, 2.65, 2.95, 1.2, 16, WHITE)
        add_text(slide, "Structured JSON\ncause · confidence\ndirection · explanation",
                 x + 0.25, 4.0, 2.95, 0.8, 13, MUTED, font="Aptos Mono")
    add_text(slide, "Safeguards: real case JSON only · historical news only when date-matched · cached responses · invalid JSON retry · no handwritten fallback",
             0.9, 5.65, 11.5, 0.75, 14, GREEN, True, align=PP_ALIGN.CENTER)

    slide = base_slide(prs, "Example saved AI investigation", "Generative AI")
    parsed = TITAN["parsed"]
    kpi(slide, 0.75, 1.45, "TITAN.NS", "case stock", CYAN)
    kpi(slide, 3.8, 1.45, "10 Aug 2026", "event date", CYAN)
    kpi(slide, 6.85, 1.45, parsed["cause"], "agent cause", AMBER)
    kpi(slide, 9.9, 1.45, f"{parsed['confidence']}%", "agent confidence", GREEN)
    rect(slide, 0.9, 3.15, 11.55, 2.55, PANEL, VIOLET)
    add_text(slide, "Saved solo explanation", 1.2, 3.48, 10.9, 0.35, 16, VIOLET, True)
    add_text(slide, parsed["explanation"], 1.2, 4.02, 10.9, 1.05, 19, WHITE)
    add_text(slide, "This is a model-generated case note based on supplied evidence; it is not a verified corporate cause.",
             1.2, 5.25, 10.9, 0.3, 12, RED, True)

    slide = base_slide(prs, "Agent direction check", "Evaluation")
    add_picture(slide, bt, 0.75, 1.35, w=6.6)
    rect(slide, 7.65, 1.55, 4.75, 4.7, PANEL, RED)
    add_text(slide, "Result", 7.95, 1.9, 4.1, 0.4, 20, RED, True)
    add_bullets(slide, [
        "A · Solo: 3/14 matched (21%)",
        "B · Team vote: 1/5 matched (20%)",
        "C · Debate: 3/13 matched (23%)",
        "Intervals are wide because samples are small.",
        "No 90-day score was available for these recent cases.",
    ], 7.95, 2.55, 4.05, 2.9, 16)
    add_text(slide, "Debate did not materially improve later direction matching.",
             7.95, 5.55, 4.05, 0.45, 15, AMBER, True)

    slide = base_slide(prs, "Final Streamlit terminal", "Product")
    add_bullets(slide, [
        "Home: verified KPIs and project flow",
        "Market Overview: candlestick, volume, Nifty comparison and case markers",
        "Case Explorer and Detail: filters, event-day metrics and local window",
        "Insights: case frequency, labels, move distributions and corrected Figure 7",
        "Model Lab: accuracy, confusion matrix, precision/recall and importance",
        "Agents, Debate and Backtest: saved outputs only; friendly locked state if missing",
    ], 0.75, 1.5, 7.15, 4.7, 17)
    rect(slide, 8.4, 1.55, 4.1, 4.6, PANEL, CYAN)
    add_text(slide, "Reliability rules", 8.75, 1.9, 3.4, 0.4, 20, CYAN, True)
    add_bullets(slide, [
        "Real files only",
        "Graceful missing-file messages",
        "Cached data loading",
        "Shared dark Plotly theme",
        "Desktop and mobile layout",
        "Disclaimer on every page",
    ], 8.75, 2.55, 3.4, 3.0, 16)

    slide = base_slide(prs, "Limitations and responsible interpretation", "Discussion")
    add_bullets(slide, [
        "Daily bars cannot reveal the exact intraday sequence or causal announcement.",
        "The four labels are transparent heuristic categories, not verified event causes.",
        "Historical headline coverage is intentionally sparse when no date-matched item exists.",
        "Groq output can be incomplete or wrong and is constrained by rate limits.",
        "Only 14 recent solo cases were available for the 30-day direction check.",
        "The system is an educational investigation tool—not a buy/sell signal or portfolio.",
    ], 0.8, 1.45, 11.6, 4.8, 19)
    add_text(slide, "The negative or weak result is still a valid finding.",
             0.8, 6.35, 11.6, 0.4, 17, GREEN, True, align=PP_ALIGN.CENTER)

    slide = base_slide(prs, "Final completion status", "Delivery")
    rows = [
        ("Real market data and cleaning", "Completed"),
        ("Case detection and EDA", "Completed"),
        ("Feature engineering and Random Forest", "Completed"),
        ("Explainability and corrected Figure 7", "Completed"),
        ("Groq solo, team and debate agents", "Completed"),
        ("Direction evaluation and report", "Completed"),
        ("Streamlit terminal and documentation", "Completed"),
    ]
    for i, (name, status) in enumerate(rows):
        y = 1.3 + i * 0.72
        rect(slide, 1.1, y, 10.9, 0.55, PANEL_2, GREEN)
        add_text(slide, name, 1.35, y + 0.12, 7.7, 0.25, 14, WHITE)
        add_text(slide, status, 9.6, y + 0.12, 1.95, 0.25, 14, GREEN, True, align=PP_ALIGN.RIGHT)
    add_text(slide, "Demo command: streamlit run app.py", 1.1, 6.55, 10.9, 0.35, 15, CYAN, True, font="Aptos Mono")

    slide = base_slide(prs, "Conclusion", "Summary")
    rect(slide, 0.75, 1.45, 11.85, 3.95, PANEL, CYAN)
    add_text(slide, "MarketForensics now completes the full investigation path:",
             1.15, 1.9, 11.0, 0.45, 21, CYAN, True, align=PP_ALIGN.CENTER)
    add_text(slide, "real prices → unusual-day detection → transparent labels → time-split model → evidence-bounded AI agents → honest direction evaluation",
             1.15, 2.75, 11.0, 1.1, 24, WHITE, True, font="Aptos Mono", align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    add_text(slide, "The strongest result is not a trading claim. It is a reproducible workflow that shows what the data supports—and clearly states what it does not prove.",
             1.3, 4.25, 10.7, 0.8, 17, AMBER, align=PP_ALIGN.CENTER)
    add_text(slide, "Questions", 0.75, 6.25, 11.85, 0.55, 25, GREEN, True, align=PP_ALIGN.CENTER)

    slide = base_slide(prs, "References", "Sources")
    add_bullets(slide, [
        "Yahoo Finance and yfinance — historical OHLCV data",
        "NSE India and Nifty Indices — market and index context",
        "Breiman (2001) — Random Forests",
        "MacKinlay (1997) — Event studies in economics and finance",
        "Scikit-learn — RandomForestClassifier and permutation importance",
        "Groq API documentation — structured AI completions",
        "Streamlit and Plotly documentation — interactive application and charts",
    ], 0.9, 1.4, 11.5, 4.8, 18)
    add_text(slide, "Source files and computed outputs are retained inside the MarketForensics project.",
             0.9, 6.35, 11.5, 0.35, 14, MUTED)

    out = OUT / "FINAL Term Presentation CAPSTONE.pptx"
    prs.save(out)
    print(out)


if __name__ == "__main__":
    build()
