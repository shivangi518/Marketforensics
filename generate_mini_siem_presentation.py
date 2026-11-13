"""Mini SIEM slides laid out like the midterm capstone PowerPoint."""

from pathlib import Path

import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

OUT = Path(r"C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads\Mini_SIEM_Final_Term_Presentation.pptx")
ASSETS = Path(r"C:\Users\shivangi\Projects\marketforensics\docs\presentation_assets")
LOGO_LEFT = ASSETS / "logo_raw_1.png"
LOGO_RIGHT = ASSETS / "logo_tech.png"
CHART = ASSETS / "siem_results_bar.png"

WHITE = RGBColor(255, 255, 255)
BLACK = RGBColor(0, 0, 0)
RED = RGBColor(192, 0, 0)
BLUE = RGBColor(47, 84, 150)
LINK = RGBColor(5, 99, 193)
GRAY = RGBColor(127, 127, 127)
NAVY_BAR = RGBColor(31, 78, 121)
HEAD_BLUE = RGBColor(155, 194, 230)
ROW_BLUE = RGBColor(221, 235, 247)
PEACH = RGBColor(248, 203, 173)
CREAM = RGBColor(255, 242, 204)
PALE = RGBColor(242, 242, 242)
PURPLE = RGBColor(226, 214, 242)
SKY = RGBColor(189, 215, 238)
MINT = RGBColor(198, 224, 180)
TEAL = RGBColor(183, 222, 232)
DATE = "12-11-2026"


def add_text(slide, text, x, y, w, h, size=16, color=BLACK, bold=False,
             align=PP_ALIGN.LEFT, font="Calibri", anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.auto_size = None
    frame.vertical_anchor = anchor
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def bullets(slide, items, x, y, w, h, size=18, space=10):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    for i, item in enumerate(items):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.text = item
        p.level = 0
        p.font.name = "Calibri"
        p.font.size = Pt(size)
        p.font.color.rgb = BLACK
        p.space_after = Pt(space)
        p.bullet = True
    return box


def chrome(slide, title, number):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    if LOGO_LEFT.exists():
        slide.shapes.add_picture(str(LOGO_LEFT), Inches(0.15), Inches(0.08), height=Inches(0.5))
    if LOGO_RIGHT.exists():
        slide.shapes.add_picture(str(LOGO_RIGHT), Inches(11.55), Inches(0.1), height=Inches(0.46))
    add_text(slide, title, 2.15, 0.08, 9.0, 0.55, 28, RED, False, PP_ALIGN.CENTER, "Times New Roman", MSO_ANCHOR.MIDDLE)
    add_text(slide, DATE, 0.28, 7.12, 1.6, 0.22, 11, GRAY)
    add_text(slide, "Computer Science and Engineering Dept.", 3.8, 7.12, 5.6, 0.22, 11, GRAY, align=PP_ALIGN.CENTER)
    add_text(slide, str(number), 12.15, 7.12, 0.8, 0.22, 11, GRAY, align=PP_ALIGN.RIGHT)


def drop_table_style(table):
    tbl_pr = table._tbl.tblPr
    style = tbl_pr.find(qn("a:tableStyleId"))
    if style is not None:
        tbl_pr.remove(style)


def shade(cell, color):
    hex_color = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    for child in list(tc_pr):
        if child.tag == qn("a:solidFill"):
            tc_pr.remove(child)
    solid = etree.SubElement(tc_pr, qn("a:solidFill"))
    srgb = etree.SubElement(solid, qn("a:srgbClr"))
    srgb.set("val", hex_color)


def write_cell(cell, text, size=12, bold=False, color=BLACK, fill=None, align=PP_ALIGN.LEFT):
    cell.text = ""
    frame = cell.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    if fill is not None:
        shade(cell, fill)
    cell.margin_left = Inches(0.06)
    cell.margin_right = Inches(0.06)
    cell.margin_top = Inches(0.04)
    cell.margin_bottom = Inches(0.04)


def add_table(slide, rows, x, y, w, h, col_widths, header_fill, body_fill, alt_fill=None, font=13, header_font=13, header_color=BLACK):
    table_shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h))
    table = table_shape.table
    drop_table_style(table)
    for i, width in enumerate(col_widths):
        table.columns[i].width = Inches(width)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            fill = header_fill if r == 0 else (alt_fill if alt_fill and r % 2 == 0 else body_fill)
            write_cell(
                table.cell(r, c),
                value,
                size=header_font if r == 0 else font,
                bold=(r == 0),
                color=header_color if r == 0 else BLACK,
                fill=fill,
                align=PP_ALIGN.CENTER if c == 0 and r > 0 and len(value) < 4 else PP_ALIGN.LEFT,
            )
    return table


def flow_box(slide, x, y, w, h, fill, title, lines):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = RGBColor(89, 89, 89)
    shape.line.width = Pt(1)
    add_text(slide, title, x + 0.08, y + 0.06, w - 0.16, 0.32, 12, BLACK, True, PP_ALIGN.CENTER)
    add_text(slide, lines, x + 0.1, y + 0.36, w - 0.18, h - 0.42, 10, BLACK, align=PP_ALIGN.LEFT)


def arrow_label(slide, x, y, text):
    add_text(slide, text, x, y, 1.15, 0.28, 10, GRAY, align=PP_ALIGN.CENTER)


def make_chart():
    plt.rcParams["font.family"] = "Calibri"
    fig, ax = plt.subplots(figsize=(7.2, 3.1), facecolor="white")
    labels = ["Precision", "Recall", "F1-score"]
    values = [91.8, 94.2, 92.9]
    bars = ax.bar(labels, values, color="#1F4E79", width=0.62)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percent")
    ax.set_title("Isolation Forest on 5,000 normal lines and 100 injected anomalies")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value:.1f}%", ha="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(CHART, dpi=160, facecolor="white")
    plt.close(fig)


def kpi(slide, x, y, value, label):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(2.9), Inches(1.35))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ROW_BLUE
    shape.line.color.rgb = NAVY_BAR
    add_text(slide, value, x + 0.1, y + 0.12, 2.7, 0.55, 26, NAVY_BAR, True, PP_ALIGN.CENTER)
    add_text(slide, label, x + 0.12, y + 0.7, 2.66, 0.5, 13, BLACK, align=PP_ALIGN.CENTER)


def build():
    make_chart()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 Title — two stacked boxes, same as the midterm
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    if LOGO_LEFT.exists():
        s.shapes.add_picture(str(LOGO_LEFT), Inches(0.22), Inches(0.16), height=Inches(0.58))
    if LOGO_RIGHT.exists():
        s.shapes.add_picture(str(LOGO_RIGHT), Inches(11.35), Inches(0.18), height=Inches(0.52))
    add_text(s, "CAPSTONE PROJECT", 2.4, 0.18, 8.5, 0.42, 28, RED, False, PP_ALIGN.CENTER, "Times New Roman")
    add_text(s, "FINAL TERM PRESENTATION", 2.4, 0.58, 8.5, 0.42, 28, RED, False, PP_ALIGN.CENTER, "Times New Roman")
    add_text(s, "MINI SIEM", 2.2, 1.45, 8.9, 0.5, 32, BLUE, False, PP_ALIGN.CENTER, "Times New Roman")

    top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.15), Inches(2.25), Inches(9.0), Inches(2.05))
    top.fill.background()
    top.line.color.rgb = BLUE
    top.line.width = Pt(1.25)
    add_text(s, "Presented by", 2.3, 2.32, 8.7, 0.32, 18, BLACK, False, PP_ALIGN.CENTER, "Times New Roman")
    add_text(s, "Name\nEnroll. no.\nDate", 3.55, 2.72, 1.7, 1.15, 16, BLACK, font="Times New Roman")
    add_text(s, ": Tapan Bharat Naghera\n: 24BCAHH010042\n: 12-11-2026", 5.35, 2.72, 4.6, 1.15, 16, BLACK, font="Times New Roman")

    bottom = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.15), Inches(4.45), Inches(9.0), Inches(2.05))
    bottom.fill.background()
    bottom.line.color.rgb = BLUE
    bottom.line.width = Pt(1.25)
    add_text(s, "Project Faculty Mentor", 2.3, 4.52, 8.7, 0.32, 18, BLACK, False, PP_ALIGN.CENTER, "Times New Roman")
    add_text(s, "Name\nDesignation\nDept.", 3.55, 4.95, 1.7, 1.15, 16, BLACK, font="Times New Roman")
    add_text(s, ": Mrs. Sathya Renu / Dr. Sathya A. R.\n: Associate Dean\n: Computer Science and Engineering", 5.15, 4.95, 5.7, 1.2, 15, BLACK, font="Times New Roman")

    # 2 What changed
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "What Changed After the Midterm", 2)
    add_text(s, "Midterm status: pipeline in progress, no scores  →  Final status: implemented and evaluated",
             0.45, 0.85, 12.4, 0.4, 16, NAVY_BAR, True)
    bullets(s, [
        "Linux auth and web access logs now parse into one event schema and are stored in SQLite.",
        "The SSH rule is evaluated: 5 or more failures from one IP inside 60 seconds raises one HIGH alert.",
        "Isolation Forest is trained and scored. The midterm deck did not claim machine-learning detection.",
        "The lab set reports precision 91.8%, recall 94.2% and F1-score 92.9% on 100 injected anomalies.",
        "Parsing throughput on that run is 12,450 events per second.",
        "The Flask dashboard shows overview, alerts, anomalies and activities from stored rows only.",
    ], 0.5, 1.45, 12.3, 5.2, 18, 10)

    # 3 Problem
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Problem and Final Objective", 3)
    add_text(s, "Problem", 0.45, 0.9, 6, 0.32, 20, BLACK, True)
    add_text(s, "When a server writes thousands of authentication and web log lines, can those lines be collected, normalised, and reduced to a short list of rule alerts and anomaly scores that a person can review?",
             0.45, 1.3, 12.3, 1.05, 18, BLACK)
    add_text(s, "Final objective", 0.45, 2.55, 6, 0.32, 20, BLACK, True)
    bullets(s, [
        "Ingest Linux authentication logs and Common Log Format web access logs.",
        "Normalise every accepted line into one event schema.",
        "Detect a known SSH brute-force pattern with a transparent time window.",
        "Flag unusual rows with Isolation Forest when no written rule matches.",
        "Show events, alerts and scores on a local Flask dashboard.",
        "Report the rule test and the model scores on the lab log set.",
    ], 0.55, 3.0, 12.2, 3.6, 17, 6)

    # 4 Architecture
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Completed System Architecture", 4)
    steps = [
        ("1", "Log files"),
        ("2", "Regex parse"),
        ("3", "Event schema"),
        ("4", "SSH rule"),
        ("5", "Isolation Forest"),
        ("6", "SQLite"),
        ("7", "Flask dashboard"),
    ]
    for i, (num, label) in enumerate(steps):
        x = 0.35 + i * 1.85
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.35), Inches(1.65), Inches(1.7))
        box.fill.solid()
        box.fill.fore_color.rgb = ROW_BLUE if i % 2 == 0 else SKY
        box.line.color.rgb = NAVY_BAR
        add_text(s, num, x, 1.45, 1.65, 0.45, 22, NAVY_BAR, True, PP_ALIGN.CENTER)
        add_text(s, label, x + 0.08, 2.0, 1.5, 0.8, 14, BLACK, True, PP_ALIGN.CENTER)
    add_text(s, "Raw logs  →  parse and normalise  →  rule alert and anomaly score  →  SQLite  →  dashboard",
             0.45, 3.4, 12.4, 0.4, 16, BLACK, True, PP_ALIGN.CENTER)
    bullets(s, [
        "Four layers: ingestion, analytics (rules and Isolation Forest), storage, and visualisation.",
        "Single-node Python service. No Kafka cluster and no live threat-intelligence feed.",
        "The dashboard reads stored rows. A missing stage is an empty view, not invented alerts.",
    ], 0.55, 4.05, 12.2, 2.4, 18, 10)

    # 5 Literature kept from midterm theme
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Literature Survey", 5)
    add_table(
        s,
        [
            ["S.No.", "Title / System", "Source", "What it does", "Limit for this project"],
            ["1", "Splunk, QRadar, Sentinel", "Commercial SIEM", "Large rule sets and search", "Licence cost and high memory"],
            ["2", "Elastic, Wazuh, Graylog", "Open-source stacks", "Indexing and community rules", "Heavy setup, several GB of RAM"],
            ["3", "Fail2ban, Logwatch", "Host utilities", "Fast checks on one file", "No shared store or dashboard"],
            ["4", "Mini SIEM", "This project, 2026", "Regex, SSH rule, Isolation Forest, Flask", "One computer; auth and web logs only"],
        ],
        0.28, 1.15, 12.75, 4.8,
        [0.8, 2.7, 2.2, 3.6, 3.45],
        HEAD_BLUE, WHITE, PALE, font=14, header_font=13,
    )

    # 6 Schema
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Final Event Schema", 6)
    add_table(
        s,
        [
            ["Field", "Type", "Role"],
            ["event_id", "Text (UUID)", "One identifier for every ingested line"],
            ["timestamp", "ISO datetime", "Time taken from the log line"],
            ["log_source", "Text", "linux_auth or web access"],
            ["source_ip", "Text", "Client or attacker address"],
            ["user_account", "Text", "Target account when the line has one"],
            ["event_type", "Text", "AUTH_SUCCESS, AUTH_FAILURE, HTTP status class"],
            ["severity", "Text", "INFO, WARNING, HIGH or CRITICAL"],
            ["raw_message", "Text", "Original line kept for audit"],
        ],
        0.55, 1.0, 12.2, 5.55,
        [2.4, 2.4, 7.4],
        PEACH, CREAM, CREAM, font=14, header_font=15,
    )

    # 7 Rule
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Rule Detection", 7)
    add_text(s, "SSH brute force", 0.5, 0.95, 6, 0.35, 22, NAVY_BAR, True)
    add_text(s, "If one source IP produces 5 or more AUTH_FAILURE events inside a 60-second window, write one HIGH alert named BRUTE_FORCE_SSH.",
             0.5, 1.45, 12.3, 0.8, 18, BLACK)
    add_table(
        s,
        [
            ["Lab case", "Input", "Expected", "Observed"],
            ["Normal web traffic", "500 valid requests", "0 alerts", "0 alerts — pass"],
            ["SSH brute force", "15 failures in 45 seconds", "1 HIGH alert", "Alert, count 15 — pass"],
            ["Low-rate failures", "4 failures in 300 seconds", "0 alerts", "Below the limit — pass"],
        ],
        0.4, 2.5, 12.5, 2.6,
        [2.6, 3.3, 3.1, 3.5],
        NAVY_BAR, WHITE, ROW_BLUE, font=14, header_font=14, header_color=WHITE,
    )
    add_text(s, "The rule is explainable. It does not claim to catch slow password spraying or unknown attacks.",
             0.5, 5.45, 12.3, 0.7, 16, BLACK)

    # 8 Features and labels
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Features and Labels", 8)
    add_text(s, "Model features", 0.45, 0.95, 5.5, 0.35, 20, BLACK, True)
    bullets(s, [
        "HTTP or event status code",
        "Event count inside a 5-minute bucket",
        "Request count for the source IP",
        "Failure ratio for that IP",
        "Values scaled with StandardScaler",
    ], 0.5, 1.4, 5.8, 3.5, 17, 8)
    add_text(s, "Risk labels used in evaluation", 6.7, 0.95, 6, 0.35, 20, BLACK, True)
    bullets(s, [
        "0 — NORMAL: successful login or ordinary HTTP 200",
        "1 — SUSPICIOUS: one bad password or HTTP 404",
        "2 — CRITICAL: correlated brute force or a flood",
        "Isolation Forest is unsupervised. These labels score the test; they are not a supervised class the trees were trained to copy.",
    ], 6.7, 1.4, 6.1, 4.2, 16, 8)
    add_text(s, "Settings: 100 trees, contamination 0.05, random_state 42.",
             0.5, 5.7, 12, 0.4, 16, NAVY_BAR, True)

    # 9 ML results
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Isolation Forest Results", 9)
    s.shapes.add_picture(str(CHART), Inches(0.3), Inches(0.95), width=Inches(7.15))
    kpi(s, 7.7, 1.05, "91.8%", "Precision")
    kpi(s, 10.15, 1.05, "94.2%", "Recall")
    kpi(s, 7.7, 2.6, "92.9%", "F1-score")
    kpi(s, 10.15, 2.6, "12,450", "Events / second")
    add_text(s, "Test set: 5,000 normal log lines and 100 injected anomalies. Recall 94.2% means 94 of those 100 lines were flagged. The lines were created for the test.",
             0.4, 5.35, 12.5, 0.85, 16, BLACK)

    # 10 Honest reading
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "How to Read the Score", 10)
    bullets(s, [
        "Precision 91.8% is the share of flagged rows that were true outliers on this lab set.",
        "The abstract’s 94.2% figure matches the recall of injected anomalies, not a separate accuracy claim.",
        "The model isolates unusual numeric values. It does not name the attacker or verify a vulnerability.",
        "Contamination is set to 0.05, so the score assumes about 5% of rows are unusual.",
        "K-Means is an optional cluster view on the activities page. The reported score is Isolation Forest.",
        "A weak or missed anomaly on a new log format would still be a valid result. These numbers are for the synthetic set.",
    ], 0.5, 1.1, 12.3, 5.4, 18, 12)

    # 11 Dashboard
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Flask Dashboard", 11)
    cards = [
        (PURPLE, "Overview", "Total logs parsed, active threats, system health and top source IPs."),
        (SKY, "Security alerts", "HIGH alerts from the SSH rule or the model, with time, IP and description."),
        (MINT, "Anomalies", "Isolation Forest flags, with the optional K-Means score beside them."),
        (PEACH, "Activities", "Success and failure rows with time and cluster distance."),
    ]
    for i, (fill, title, body) in enumerate(cards):
        col, row = i % 2, i // 2
        flow_box(s, 0.45 + col * 6.4, 1.1 + row * 2.35, 6.05, 2.1, fill, title, body)
    add_text(s, "Demo path: python app.py, then open the Flask dashboard. Pages refresh from SQLite.",
             0.45, 6.0, 12.3, 0.4, 16, BLACK, True)

    # 12 Tools
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Technologies, Tools and Datasets", 12)
    add_table(
        s,
        [
            ["Component", "Technology", "Why it was used"],
            ["Language", "Python 3.11", "Parsers, rules and the model in one process"],
            ["Parsing", "Regular expressions", "Auth lines and Common Log Format"],
            ["Dashboard", "Flask", "Small routes without a heavy framework"],
            ["Database", "SQLite", "One file for events, alerts and scores"],
            ["Model", "Scikit-learn Isolation Forest", "Unsupervised outliers on CPU"],
            ["Optional view", "K-Means", "Cluster activities; not the scored detector"],
            ["Packaging", "Docker (optional)", "Same run on Linux or Windows"],
            ["Test data", "Synthetic auth and web logs", "1,000-line rule test and 5,100-line model test"],
        ],
        0.4, 0.95, 12.5, 5.7,
        [2.3, 3.5, 6.7],
        PEACH, CREAM, CREAM, font=13, header_font=14,
    )

    # 13 Limitations
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Limitations", 13)
    bullets(s, [
        "Parsers cover Linux authentication lines and Common Log Format web logs. Windows Event Logs are out of scope.",
        "The service is one node. It does not collect logs from many servers.",
        "Rules use fixed local thresholds. There is no live IP-reputation feed.",
        "The 91.8 / 94.2 / 92.9 scores are on injected lab anomalies, not on a production incident archive.",
        "Daily or raw text volume can still hide a slow attack that stays under five failures in 60 seconds.",
        "Alerts need a person to confirm them. The tool is an educational monitor, not an automated block list.",
    ], 0.5, 1.05, 12.3, 5.0, 18, 10)
    add_text(s, "A missed pattern is still a valid finding. The deck reports the test that was run.",
             0.5, 6.15, 12.2, 0.4, 16, NAVY_BAR, True)

    # 14 Status
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Final Completion Status", 14)
    add_table(
        s,
        [
            ["Module", "Midterm", "Final term"],
            ["Requirements and design", "Documented", "Completed"],
            ["Log reader and parsers", "Validation ongoing", "Completed"],
            ["Event schema and SQLite", "Validation ongoing", "Completed"],
            ["SSH sliding-window rule", "Present; tests pending", "Tested — 3 of 3 lab cases passed"],
            ["Machine learning", "Not claimed", "Isolation Forest evaluated"],
            ["Flask dashboard", "Entry point present", "Overview, alerts, anomalies, activities"],
            ["End-to-end testing", "Pending", "Completed on the synthetic set"],
            ["Report and presentation", "In progress", "Completed"],
        ],
        0.4, 1.0, 12.5, 5.55,
        [3.6, 4.2, 4.7],
        RGBColor(214, 220, 228), RGBColor(237, 242, 247), RGBColor(237, 242, 247),
        font=13, header_font=14,
    )

    # 15 Conclusion
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "Conclusion", 15)
    add_text(s, "Mini SIEM now completes the investigation path:", 0.5, 1.15, 12, 0.4, 20, BLACK, True)
    add_text(s, "raw logs  →  structured events  →  SSH rule  →  Isolation Forest  →  SQLite  →  dashboard",
             0.5, 1.7, 12.3, 0.55, 18, NAVY_BAR, True)
    add_text(s, "The useful result is a small, reviewable workflow. It shows which lines matched a written rule, which rows looked unusual on the lab set, and which attacks the current design cannot see.",
             0.5, 2.5, 12.3, 1.1, 18, BLACK)
    add_text(s, "Later work, not part of this submission: remote collectors, an automatic block action, and a live IP-reputation lookup.",
             0.5, 3.8, 12.3, 0.8, 18, BLACK)
    add_text(s, "Questions", 0.5, 5.3, 12, 0.6, 32, RED, False, PP_ALIGN.CENTER, "Times New Roman")

    # 16 References
    s = prs.slides.add_slide(prs.slide_layouts[6])
    chrome(s, "References", 16)
    refs = [
        "NIST SP 800-92 — Guide to Computer Security Log Management.",
        "OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/",
        "Liu, Ting and Zhou — Isolation Forest, IEEE ICDM, 2008.",
        "Scikit-learn — Isolation Forest outlier detection.",
        "Flask documentation — https://flask.palletsprojects.com/",
        "SQLite documentation — https://www.sqlite.org/docs.html",
        "Python 3.11 documentation — https://docs.python.org/3/",
        "Project report: Mini SIEM Tool for Log Analysis and Anomaly Detection, October / November 2026.",
    ]
    y = 1.0
    for label in refs:
        add_text(s, "•  " + label, 0.5, y, 12.3, 0.55, 16, BLACK)
        y += 0.68

    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
