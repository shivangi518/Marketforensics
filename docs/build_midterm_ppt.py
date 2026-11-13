"""College mid-term seminar slides, filled from this project's saved results."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(r"C:\Users\shivangi\Projects\marketforensics")
OUT = ROOT / "docs" / "MarketForensics_Midterm_Presentation.pptx"
FIG = ROOT / "docs" / "ppt_figures"
CASES = ROOT / "data" / "cases" / "all_cases.csv"

W, H = 13.333, 7.5
BLUE = RGBColor(0x1F, 0x4E, 0x79)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY = RGBColor(0x59, 0x59, 0x59)
LINE = RGBColor(0x1F, 0x4E, 0x79)
PALE = RGBColor(0xD6, 0xE3, 0xF0)
ROW = RGBColor(0xF2, 0xF2, 0xF2)
DATE = "10-10-2026"


def font(run, size, bold=False, color=BLACK, name="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    for tag in ("latin", "ea", "cs"):
        el = rpr.find(qn(f"a:{tag}"))
        if el is None:
            el = rpr.makeelement(qn(f"a:{tag}"), {})
            rpr.append(el)
        el.set("typeface", name)


def box(slide, l, t, w, h, text, size=18, bold=False, color=BLACK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    shape = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = 0
    tf.margin_bottom = 0
    anchor_map = {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}
    tf._txBody.bodyPr.set("anchor", anchor_map[anchor])
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        run = p.add_run()
        run.text = line
        font(run, size, bold, color)
    return shape


def bullets(slide, l, t, w, h, items, size=18, space=6):
    shape = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.level = 0
        p.space_after = Pt(space)
        p.space_before = Pt(0)
        run = p.add_run()
        run.text = "•  " + item
        font(run, size, False, BLACK)
    return shape


def rect(slide, l, t, w, h, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    sp = shape._element.spPr
    effect = sp.find(qn("a:effectLst"))
    if effect is not None:
        sp.remove(effect)
    return shape


def hline(slide, y):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(y), Inches(12.53), Inches(0.015))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BLUE
    shape.line.fill.background()
    return shape


def header(slide, number, title):
    rect(slide, 0, 0, W, H, WHITE)
    box(slide, 0.4, 0.12, 8.2, 0.32, "Computer Science and Engineering Dept.", 14, True, BLUE)
    box(slide, 8.6, 0.12, 4.3, 0.32, f"{DATE}          {number}", 14, False, BLUE, PP_ALIGN.RIGHT)
    hline(slide, 0.48)
    box(slide, 0.4, 0.58, 12.5, 0.48, title, 28, True, BLUE)


def cell(table, r, c, text, size, bold, fill, color, align=PP_ALIGN.LEFT):
    item = table.cell(r, c)
    item.text = ""
    item.vertical_anchor = MSO_ANCHOR.MIDDLE
    item.margin_left = Inches(0.06)
    item.margin_right = Inches(0.05)
    item.margin_top = Inches(0.04)
    item.margin_bottom = Inches(0.03)
    item.fill.solid()
    item.fill.fore_color.rgb = fill
    p = item.text_frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    font(run, size, bold, color)
    # Keep the grid visible.
    tc = item._tc
    tcPr = tc.get_or_add_tcPr()
    for edge in ("lnL", "lnR", "lnT", "lnB"):
        ln = tcPr.find(qn(f"a:{edge}"))
        if ln is None:
            ln = tcPr.makeelement(qn(f"a:{edge}"), {"w": str(Pt(0.75))})
            tcPr.append(ln)
        ln.set("w", str(int(Pt(0.75))))
        sf = ln.find(qn("a:solidFill"))
        if sf is None:
            sf = ln.makeelement(qn("a:solidFill"), {})
            ln.append(sf)
        srgb = sf.find(qn("a:srgbClr"))
        if srgb is None:
            srgb = sf.makeelement(qn("a:srgbClr"), {"val": "7F7F7F"})
            sf.append(srgb)
        else:
            srgb.set("val", "7F7F7F")


def make_figures():
    FIG.mkdir(parents=True, exist_ok=True)
    cases = pd.read_csv(CASES, parse_dates=["date"])
    month = cases.assign(month=cases["date"].dt.to_period("M").astype(str)).groupby("month").size()
    fig, ax = plt.subplots(figsize=(6.4, 3.15))
    ax.plot(range(len(month)), month.values, color="#1f4e79", linewidth=1.6)
    ax.set_xticks(range(0, len(month), 6))
    ax.set_xticklabels(list(month.index[::6]), fontsize=8)
    ax.set_ylabel("Cases", fontsize=9)
    ax.set_title("Unusual days by month", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    month_path = FIG / "cases_by_month.png"
    fig.savefig(month_path, dpi=140)
    plt.close(fig)

    labels = ["Stock-specific", "Market-wide", "Unknown", "Volume shock"]
    values = [755, 351, 190, 26]
    fig, ax = plt.subplots(figsize=(5.6, 3.15))
    ax.barh(labels[::-1], values[::-1], color="#1f4e79")
    ax.set_xlabel("Cases", fontsize=9)
    ax.set_title("Labelled cases (1,322)", fontsize=11)
    for i, v in enumerate(values[::-1]):
        ax.text(v + 8, i, str(v), va="center", fontsize=8)
    fig.tight_layout()
    label_path = FIG / "label_counts.png"
    fig.savefig(label_path, dpi=140)
    plt.close(fig)
    return month_path, label_path


def flow_box(slide, x, y, w, h, text):
    rect(slide, x, y, w, h, PALE, BLUE)
    box(slide, x + 0.04, y + 0.08, w - 0.08, h - 0.1, text, 12, True, BLUE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


PLOTS = ROOT / "data" / "plots" / "eda"


def chart_with_note(slide, x, y, w, img, img_h, title, note):
    box(slide, x, y, w, 0.32, title, 16, True, BLACK)
    slide.shapes.add_picture(str(img), Inches(x), Inches(y + 0.36), Inches(w), Inches(img_h))
    box(slide, x, y + img_h + 0.42, w, 1.35, note, 14, False, BLACK)


def build():
    _month_path, label_path = make_figures()
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    prs.core_properties.title = "MarketForensics — Mid Term Seminar"
    prs.core_properties.subject = "Mid Term Seminar (IP101)"
    blank = prs.slide_layouts[6]

    # ----- 1 Title -----
    s = prs.slides.add_slide(blank)
    rect(s, 0, 0, W, H, WHITE)
    rect(s, 0, 0, W, 0.95, BLUE)
    box(s, 0.4, 0.28, 12.5, 0.45, "Mid Term Seminar (IP101)", 26, True, WHITE, PP_ALIGN.CENTER)
    box(s, 0.4, 1.25, 12.5, 0.35, "Computer Science and Engineering Department", 18, True, BLUE, PP_ALIGN.CENTER)
    box(s, 0.6, 2.05, 12.1, 0.35, "PROJECT TITLE", 16, True, GRAY, PP_ALIGN.CENTER)
    box(s, 0.5, 2.4, 12.3, 1.15, "MarketForensics:\nExplaining Unusual Daily Price Jumps in NSE Stocks", 28, True, BLUE, PP_ALIGN.CENTER)

    box(s, 0.7, 3.85, 5.5, 0.35, "Presented by", 18, True, BLACK)
    box(s, 7.1, 3.85, 5.5, 0.35, "Project Faculty Mentor", 18, True, BLACK)
    left_fields = ["Name", "Enroll. no.", "Date"]
    right_fields = ["Name", "Designation", "Dept."]
    for i, label in enumerate(left_fields):
        y = 4.4 + i * 0.55
        box(s, 0.7, y, 1.7, 0.32, label + "  :", 16, False, BLACK)
        rect(s, 2.45, y + 0.28, 3.3, 0.015, RGBColor(0x7F, 0x7F, 0x7F))
    box(s, 2.5, 5.42, 3.2, 0.3, DATE, 16, False, BLACK)
    for i, label in enumerate(right_fields):
        y = 4.4 + i * 0.55
        box(s, 7.1, y, 1.8, 0.32, label + "  :", 16, False, BLACK)
        rect(s, 8.95, y + 0.28, 3.4, 0.015, RGBColor(0x7F, 0x7F, 0x7F))
    box(s, 9.0, 5.42, 3.5, 0.3, "Computer Science and Engineering", 14, False, BLACK)

    # ----- 2 Introduction / background -----
    s = prs.slides.add_slide(blank)
    header(s, 2, "Introduction")
    box(s, 0.45, 1.2, 12, 0.35, "Background", 20, True, BLACK)
    bullets(
        s,
        0.45,
        1.6,
        12.3,
        2.3,
        [
            "Domain: finance, on daily prices of large stocks listed on the NSE.",
            "A stock sometimes moves much more in one day than it has moved recently.",
            "Most student projects try to guess the next day's price. This project looks at a day that has already happened and asks what kind of move it was.",
            "Prices are downloaded from Yahoo Finance. They are not typed in by hand.",
        ],
        size=18,
        space=8,
    )
    box(s, 0.45, 4.15, 12, 0.35, "Why this topic, and why it matters", 20, True, BLACK)
    bullets(
        s,
        0.45,
        4.55,
        12.3,
        2.3,
        [
            "A rule such as “any day over 3%” is common for a jumpy stock and rare for a calm stock. The cutoff should depend on that stock.",
            "A large move can be the whole market, that one stock, or a burst of trading. Those are different cases.",
            "The result is a sorting of past days. It is not a buy or sell instruction.",
        ],
        size=18,
        space=8,
    )

    # ----- 3 Problem and objectives -----
    s = prs.slides.add_slide(blank)
    header(s, 3, "Introduction")
    box(s, 0.45, 1.2, 12, 0.35, "Problem statement", 20, True, BLACK)
    bullets(
        s,
        0.45,
        1.65,
        12.3,
        1.5,
        [
            "When an NSE stock has an unusually large daily move, can price and volume clues say whether that day looks market-wide, stock-specific, a volume spike, or unclear?",
        ],
        size=18,
        space=4,
    )
    box(s, 0.45, 3.15, 12, 0.35, "Project objectives", 20, True, BLACK)
    bullets(
        s,
        0.45,
        3.55,
        12.3,
        2.45,
        [
            "Collect daily NSE prices from 1 January 2022 and clean them onto the Nifty trading calendar.",
            "Mark a day as unusual only when the absolute return is at least 2.5 times that stock’s own previous 20-day volatility.",
            "Build clues from prices on or before that day. Do not use the days after the jump.",
            "Label each case with a written rule, then test a Random Forest on later dates only.",
            "Show one case in a small Streamlit page.",
        ],
        size=18,
        space=6,
    )
    box(s, 0.45, 6.15, 12, 0.3, "Expected outcome", 20, True, BLACK)
    bullets(
        s,
        0.45,
        6.5,
        12.3,
        0.7,
        [
            "A working pipeline on real NSE prices, and a test score that is reported as the model learning the rule, not as a trading result.",
        ],
        size=18,
        space=2,
    )

    # ----- 4 Literature -----
    s = prs.slides.add_slide(blank)
    header(s, 4, "Literature Survey")
    box(
        s,
        0.4,
        1.15,
        12.5,
        0.4,
        "Similar work, and what it does not do for this project.",
        16,
        False,
        BLACK,
    )
    rows = [
        ["S.no.", "Title / system", "Author / source", "Year", "What it does", "Limitation"],
        ["1", "Price adjustment to new information", "Fama, Fisher, Jensen and Roll", "1969", "Treats a large price change as an event to be studied", "Starts from a known event. This project starts from the jump."],
        ["2", "Event studies in economics and finance", "MacKinlay", "1997", "Sets out the standard event-study method", "Made for a research event, not a four-way label."],
        ["3", "LIME: explaining a classifier", "Ribeiro, Singh and Guestrin", "2016", "Shows which inputs pushed a model’s answer", "Explains the model. It does not prove the real-world cause."],
        ["4", "SHAP", "Lundberg and Lee", "2017", "Splits a prediction across the input features", "Not used for the mid-term score. Same limit as LIME."],
        ["5", "Multi-agent debate", "Du, Li, Torralba, Tenenbaum and Mordatch", "2023", "Several model roles argue, then one answer is written", "Needs an API. Not finished on every case yet."],
    ]
    table = s.shapes.add_table(6, 6, Inches(0.35), Inches(1.65), Inches(12.65), Inches(5.15)).table
    widths = [0.6, 2.35, 2.45, 0.7, 3.35, 3.2]
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(w)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell(
                table,
                r,
                c,
                val,
                12 if r else 12,
                r == 0,
                BLUE if r == 0 else (ROW if r % 2 == 0 else WHITE),
                WHITE if r == 0 else BLACK,
                PP_ALIGN.CENTER if c in (0, 3) else PP_ALIGN.LEFT,
            )

    # ----- 5 Methodology -----
    s = prs.slides.add_slide(blank)
    header(s, 5, "Methodology")
    box(s, 0.45, 1.15, 12.4, 0.32, "Proposed solution", 20, True, BLACK)
    bullets(
        s,
        0.45,
        1.5,
        12.4,
        1.15,
        [
            "Download real daily prices, find days that are large for that stock, turn each day into a few numbers, and sort it into one of four buckets.",
        ],
        size=17,
        space=2,
    )
    steps = ["1  Download", "2  Clean", "3  Find cases", "4  Charts", "5  Clues", "6  Forest", "7  App"]
    for i, name in enumerate(steps):
        x = 0.4 + i * 1.84
        flow_box(s, x, 2.75, 1.62, 0.7, name)
        if i < len(steps) - 1:
            box(s, x + 1.55, 2.88, 0.32, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 0.45, 3.65, 6.1, 0.32, "The case rule", 18, True, BLACK)
    bullets(
        s,
        0.4,
        4.05,
        6.2,
        2.6,
        [
            "A day is a case if |return| ≥ 2.5 × the standard deviation of the previous 20 daily returns.",
            "That window is shifted back by one day, so today is not inside its own “normal” range.",
            "Missing prices are dropped. They are not copied from the previous day.",
        ],
        size=15,
        space=6,
    )
    box(s, 6.85, 3.65, 6.0, 0.32, "Tools and data", 18, True, BLACK)
    bullets(
        s,
        6.8,
        4.05,
        6.1,
        2.6,
        [
            "Python, pandas, NumPy, yfinance, Matplotlib, Plotly.",
            "scikit-learn Random Forest (200 trees), saved with joblib.",
            "Streamlit for the case page.",
            "Yahoo Finance daily bars, 31 NSE stocks plus Nifty, from 1 Jan 2022.",
        ],
        size=15,
        space=6,
    )

    # ----- 6 System design -----
    s = prs.slides.add_slide(blank)
    header(s, 6, "System Design")
    box(s, 0.45, 1.15, 12.4, 0.32, "Data flow", 20, True, BLACK)
    row1 = [("Yahoo Finance", 0.4), ("data/raw CSV", 3.55), ("Cleaned prices", 6.7), ("all_cases.csv", 9.85)]
    for name, x in row1:
        flow_box(s, x, 1.6, 2.85, 0.72, name)
    box(s, 3.2, 1.75, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 6.35, 1.75, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 9.5, 1.75, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    row2 = [("case_features.csv", 0.4), ("Rule labels", 3.55), ("Random Forest", 6.7), ("Streamlit app", 9.85)]
    for name, x in row2:
        flow_box(s, x, 2.55, 2.85, 0.72, name)
    box(s, 3.2, 2.7, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 6.35, 2.7, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 9.5, 2.7, 0.35, 0.4, ">", 16, True, BLUE, PP_ALIGN.CENTER)
    box(s, 0.45, 3.5, 12.4, 0.32, "Design logic", 20, True, BLACK)
    bullets(
        s,
        0.45,
        3.9,
        12.4,
        2.9,
        [
            "Cleaning keeps only dates that exist on the Nifty calendar. A missing close is removed, not filled.",
            "Labels, in order: market-wide if |Nifty| ≥ 1.5%; else stock-specific if the gap versus Nifty is at least 2.0 points; else volume shock if volume ≥ 2 × its 20-day average; else unknown.",
            "The forest is trained on cases up to 9 May 2025 (938 cases) and tested on cases from 12 May 2025 (384 cases). Same-day cases are not split across the two sets.",
            "The user runs the pipeline, then opens the app and reads one case: the move, the clues, and the bucket. A class diagram is not used. The system is this pipeline.",
        ],
        size=16,
        space=6,
    )

    # ----- 7 Implementation: price charts -----
    s = prs.slides.add_slide(blank)
    header(s, 7, "Implementation and Results")
    box(
        s,
        0.4,
        1.08,
        12.5,
        0.3,
        "Done so far: 31 stocks plus Nifty cleaned, 1,332 unusual days found, features built, Random Forest trained, Streamlit page opened.",
        14,
        False,
        BLACK,
    )
    chart_with_note(
        s,
        0.4,
        1.48,
        6.2,
        PLOTS / "RELIANCE.NS_price_volume.png",
        3.55,
        "Reliance close and volume",
        "Cleaned daily close (line) and volume (bars), Jan 2022 to Oct 2026. The same kind of file is saved for the other 30 stocks. Tata Motors had no Yahoo quote and was skipped.",
    )
    chart_with_note(
        s,
        6.8,
        1.48,
        6.15,
        PLOTS / "RELIANCE.NS_vs_nifty_growth100.png",
        3.55,
        "Reliance against Nifty",
        "Both lines start at 100. When the blue line leaves the orange line, Reliance is not just following the market. That gap is the clue called vs_nifty.",
    )

    # ----- 8 Implementation: case charts -----
    s = prs.slides.add_slide(blank)
    header(s, 8, "Implementation and Results")
    chart_with_note(
        s,
        0.4,
        1.15,
        6.2,
        PLOTS / "RELIANCE.NS_return_hist.png",
        3.7,
        "Most days are small",
        "For Reliance, most daily moves sit between about −2% and +2%. A fixed “over 3%” rule would miss a calm stock and flag a jumpy stock too often. The far bars are the unusual days.",
    )
    chart_with_note(
        s,
        6.8,
        1.15,
        6.15,
        PLOTS / "big_moves_by_month.png",
        3.7,
        "When the cases happened",
        "1,332 cases from 2022 to 2026, not one crash month. The busiest month is January 2025, with 47 cases. Quieter months still have about 10.",
    )

    # ----- 9 Model result -----
    s = prs.slides.add_slide(blank)
    header(s, 9, "Implementation and Results")
    box(s, 0.4, 1.1, 12.5, 0.3, "Cases per stock", 16, True, BLACK)
    s.shapes.add_picture(str(PLOTS / "big_moves_per_stock.png"), Inches(0.4), Inches(1.42), Inches(12.5), Inches(2.35))
    box(
        s,
        0.4,
        3.8,
        12.5,
        0.55,
        "Titan has the most cases (51). NTPC has the fewest on this chart, still above 30. Every stock is judged by its own recent volatility, so a calm stock is not dropped.",
        14,
        False,
        BLACK,
    )
    box(s, 0.4, 4.4, 5.8, 0.28, "How the 1,322 labels split", 15, True, BLACK)
    s.shapes.add_picture(str(label_path), Inches(0.4), Inches(4.72), Inches(5.7), Inches(2.15))
    box(s, 6.4, 4.4, 6.5, 0.28, "Test result, dates after 12 May 2025", 15, True, BLACK)
    result_rows = [
        ["Bucket", "Precision", "Recall", "Test cases"],
        ["Market-wide", "0.82", "0.72", "68"],
        ["Stock-specific", "0.94", "0.97", "238"],
        ["Unknown", "0.90", "0.93", "71"],
        ["Volume shock", "1.00", "0.71", "7"],
    ]
    result = s.shapes.add_table(5, 4, Inches(6.4), Inches(4.75), Inches(6.5), Inches(1.7)).table
    for i, w in enumerate([2.05, 1.4, 1.3, 1.75]):
        result.columns[i].width = Inches(w)
    for r, row in enumerate(result_rows):
        for c, val in enumerate(row):
            cell(
                result,
                r,
                c,
                val,
                12,
                r == 0,
                BLUE if r == 0 else (ROW if r % 2 == 0 else WHITE),
                WHITE if r == 0 else BLACK,
                PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER,
            )
    box(
        s,
        6.4,
        6.52,
        6.5,
        0.75,
        "Accuracy: 91.7% on 384 later cases. The forest learned the labelling rule. It does not mean a news report confirmed the cause. Median move 3.67%. Largest rise +10.63% (Bajaj Finance). Largest fall −15.45% (NTPC).",
        12,
        False,
        BLACK,
    )

    # ----- 10 Timeline -----
    s = prs.slides.add_slide(blank)
    header(s, 10, "Project Completion Timeline / Status")
    status_rows = [
        ["S.no.", "Module", "Planned work", "Status"],
        ["1", "Problem definition", "Question, scope, and what will not be claimed", "Completed"],
        ["2", "Data collection and cleaning", "Yahoo Finance download, Nifty calendar, no filled prices", "Completed"],
        ["3", "Case detection and charts", "2.5× volatility rule, EDA charts, universe profile", "Completed"],
        ["4", "Features and labels", "Clues up to the case day; four written buckets", "Completed"],
        ["5", "Random Forest", "Train on older cases, test on later cases, save the model", "Completed"],
        ["6", "Case viewer", "Streamlit page for one case, its clues, and its bucket", "Completed"],
        ["7", "Written explanations", "Groq: one analyst, a team vote, and a short debate", "In progress"],
        ["8", "Direction check and report", "Did the stated direction match the next 30 and 90 days", "In progress"],
    ]
    status = s.shapes.add_table(9, 4, Inches(0.4), Inches(1.25), Inches(12.55), Inches(5.55)).table
    for i, w in enumerate([0.7, 2.7, 6.35, 2.8]):
        status.columns[i].width = Inches(w)
    for r, row in enumerate(status_rows):
        for c, val in enumerate(row):
            cell(
                status,
                r,
                c,
                val,
                14 if r == 0 else 13,
                r == 0 or c == 3,
                BLUE if r == 0 else (ROW if r % 2 == 0 else WHITE),
                WHITE if r == 0 else BLACK,
                PP_ALIGN.CENTER if c in (0, 3) else PP_ALIGN.LEFT,
            )

    # ----- 9 References -----
    s = prs.slides.add_slide(blank)
    header(s, 11, "References")
    refs = [
        '[1]  E. F. Fama, L. Fisher, M. C. Jensen, and R. Roll, "The adjustment of stock prices to new information," Int. Econ. Rev., vol. 10, no. 1, pp. 1–21, Feb. 1969.',
        '[2]  A. C. MacKinlay, "Event studies in economics and finance," J. Econ. Lit., vol. 35, no. 1, pp. 13–39, Mar. 1997.',
        '[3]  M. T. Ribeiro, S. Singh, and C. Guestrin, "Why should I trust you?: Explaining the predictions of any classifier," in Proc. 22nd ACM SIGKDD, 2016, pp. 1135–1144.',
        '[4]  S. M. Lundberg and S. Lee, "A unified approach to interpreting model predictions," in Proc. Adv. Neural Inf. Process. Syst., 2017, pp. 4765–4774.',
        '[5]  Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch, "Improving factuality and reasoning in language models through multiagent debate," arXiv:2305.14325, 2023.',
        '[6]  F. Pedregosa et al., "Scikit-learn: Machine learning in Python," J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.',
        '[7]  R. Aroussi, "yfinance: Yahoo! Finance market data downloader," GitHub, 2024. [Online]. Available: https://github.com/ranaroussi/yfinance',
    ]
    y = 1.25
    for ref in refs:
        box(s, 0.45, y, 12.4, 0.7, ref, 15, False, BLACK)
        y += 0.75

    prs.save(str(OUT))
    print(OUT)


if __name__ == "__main__":
    build()
