"""Create the concise, polished final deck without agents or backtest."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


DOWNLOADS = Path(r"C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads")
BASE = Path(__file__).resolve().parent
SOURCE = DOWNLOADS / "FINAL Term Presentation CAPSTONE Full Same Theme.pptx"
OUTPUT = DOWNLOADS / "FINAL Term Presentation CAPSTONE Polished.pptx"
NOTES = DOWNLOADS / "FINAL Term Presentation Polished Speaking Notes.md"
SCREENSHOT = BASE / "docs/presentation_assets/marketforensics_dashboard_home.png"

BLACK = RGBColor(20, 20, 20)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(192, 0, 0)
BLUE = RGBColor(47, 84, 150)
GREEN = RGBColor(112, 173, 71)
ORANGE = RGBColor(237, 125, 49)
LIGHT_BLUE = RGBColor(221, 235, 247)
LIGHT_GREEN = RGBColor(226, 240, 217)
LIGHT_ORANGE = RGBColor(252, 228, 214)
GRAY = RGBColor(100, 100, 100)


SPEAKER_NOTES = [
    "Good morning. My project is MarketForensics. It investigates unusually large NSE stock movements using real prices, transparent rules, machine learning, and an interactive dashboard. It is educational and does not give trading advice.",
    "At the midterm I had completed the market-data pipeline, anomaly detection, feature engineering, Random Forest, and an early dashboard. After the midterm I corrected the visual analysis, improved the model evaluation, rebuilt the dashboard, added robust missing-file handling, and completed the final report and documentation.",
    "The project asks whether same-day price and volume evidence can describe a large move as market-wide, stock-specific, volume-driven, or unclear. The purpose is transparent investigation, not predicting tomorrow's price.",
    "The completed core pipeline has eight stages: download, clean, detect, analyse, build features, train the model, display results, and test the application. Every stage writes a real file that the next stage reads.",
    "The current final rerun contains 31 stocks plus Nifty, 1,179 trading days, and 1,334 detected cases through 12 October 2026. Titan has the most cases, January 2025 is the busiest month, and the median absolute event move is 3.67 percent.",
    "A day becomes a case when its absolute return is at least 2.5 times the previous 20-day volatility. The volatility baseline is shifted by one day so the event is not inside its own threshold. Features use data only through the event-day close.",
    "The model uses returns, volatility, relative volume, moving-average position, momentum, the gap versus Nifty, and weekday. Labels follow a documented order: market-wide, stock-specific, volume shock, then unknown.",
    "The EDA shows that unusual movements appear throughout the sample. They are not limited to one crash month. Titan has the highest number of cases, and January 2025 has the largest monthly count.",
    "The Random Forest has 200 trees. The latest time split uses 953 older training cases and 381 later test cases. Accuracy is 92.1 percent. Volume shock has only seven test examples, so its result must be interpreted carefully.",
    "The gap versus Nifty is the dominant permutation-importance feature. The accuracy mainly shows that the model learned the written label rules because those labels were derived from related variables. It does not verify a real-world news cause.",
    "Figure 7 was blank in the earlier version because zero volume caused infinite percentage changes. The corrected figure uses log-volume change after removing non-positive values. Most correlations are close to zero.",
    "This is the final Streamlit dashboard. The home page shows current file-based KPIs. Other pages provide candlesticks, case filters, event details, insights, model evaluation, and project documentation. Missing files show a clear repair instruction instead of fake data.",
    "Testing covered file availability, date parsing, no-leakage checks, chart generation, model loading, and mobile-friendly page structure. The application caches repeated reads and uses a shared visual theme.",
    "The limitations are important. Daily bars cannot prove an exact corporate cause. Labels are heuristics. The volume-shock class is small. Yahoo data can have ticker failures. These limits are shown openly in the app and report.",
    "All core modules are complete: data collection, preprocessing, anomaly detection, EDA, feature engineering, Random Forest, explainability, dashboard, testing, and documentation. The live demo starts with streamlit run app.py.",
    "In conclusion, MarketForensics is a reproducible educational workflow for investigating unusual NSE movements. Its main strength is transparent rules, time-aware testing, clear visual evidence, and honest limitations. Thank you; I am ready for questions.",
]


def delete_slide(prs, number: int) -> None:
    slide = prs.slides[number - 1]
    slide_id = slide.slide_id
    prs.part.drop_rel(prs.slides._sldIdLst[number - 1].rId)
    for item in list(prs.slides._sldIdLst):
        if item.id == slide_id:
            prs.slides._sldIdLst.remove(item)
            break


def remove_shape(shape) -> None:
    element = shape._element
    element.getparent().remove(element)


def add_text(slide, text, x, y, w, h, size=17, color=BLACK, bold=False,
             align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def card(slide, x, y, w, h, fill, line=BLUE):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(0.9)
    return shape


def clear_content(slide, keep_title=True) -> None:
    for shape in list(slide.shapes):
        y = shape.top / Inches(1)
        x = shape.left / Inches(1)
        text = shape.text.strip() if getattr(shape, "has_text_frame", False) else ""
        is_logo = y < 0.35 and x < 2.5
        is_title = keep_title and y < 1.15 and len(text) > 2
        is_footer = y > 6.95
        if not (is_logo or is_title or is_footer):
            remove_shape(shape)


def replace_text(prs, mapping: dict[str, str]) -> None:
    for slide in prs.slides:
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    for old, new in mapping.items():
                        if old in run.text:
                            run.text = run.text.replace(old, new)


def set_notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def main() -> None:
    prs = Presentation(SOURCE)

    # Remove A/B/C agent design, example case, and direction backtest slides.
    for number in (14, 13, 12):
        delete_slide(prs, number)

    replace_text(
        prs,
        {
            "1,332": "1,334",
            "1,172": "1,179",
            "91.7%": "92.1%",
            "938": "953",
            "384": "381",
            "9 May 2025": "10 June 2025",
            "12 May 2025": "11 June 2025",
            "Groq integration is complete: solo, team-vote and debate designs write structured JSON.":
                "The Streamlit dashboard is complete with market, case, insight and model views.",
            "Agent responses are cached; invalid JSON is retried; API rate limits stop honestly.":
                "The final application handles missing files safely and never substitutes fake results.",
            "A 30-day direction check evaluates the saved agent calls without calling it a trading strategy.":
                "Model evaluation, explainability and the final documentation are complete.",
            "The Streamlit terminal now includes market, case, insight, model, agent, debate and backtest views.":
                "The redesigned terminal includes market overview, case explorer, insights and model lab.",
            "transparent labels → time-split model → evidence-bounded AI agents → honest direction evaluation":
                "transparent labels → time-split model → explainability → interactive dashboard",
            "Groq solo, team and debate agents": "Application testing and reliability",
            "Direction evaluation and report": "Final analysis and report",
            "Groq output can be incomplete or wrong and is constrained by rate limits.":
                "Data-provider failures can temporarily omit an individual ticker.",
            "Only 14 recent solo cases were available for the 30-day direction check.":
                "The volume-shock class has only 26 total cases and seven test cases.",
            "Agents, Debate and Backtest: saved outputs only; friendly locked state if missing":
                "All views read saved outputs and show friendly repair instructions if files are missing",
            "Groq API documentation — structured AI completions":
                "Matplotlib documentation — static analytical figures",
        },
    )

    # Slide 2: make the post-midterm work concise and visual.
    slide = prs.slides[1]
    clear_content(slide)
    items = [
        ("Dashboard", "Redesigned terminal with seven core views", LIGHT_BLUE, BLUE),
        ("Evaluation", "Updated time split and 92.1% test accuracy", LIGHT_GREEN, GREEN),
        ("Visual quality", "Corrected Figure 7 and consistent charts", LIGHT_ORANGE, ORANGE),
        ("Reliability", "Missing-file handling, caching and documentation", LIGHT_BLUE, BLUE),
    ]
    for i, (title, text, fill, line) in enumerate(items):
        x = 0.85 + (i % 2) * 6.0
        y = 1.55 + (i // 2) * 2.2
        card(slide, x, y, 5.3, 1.65, fill, line)
        add_text(slide, title, x + 0.25, y + 0.25, 4.8, 0.35, 18, line, True)
        add_text(slide, text, x + 0.25, y + 0.8, 4.8, 0.5, 15)
    add_text(slide, "Midterm prototype → complete, tested and documented final product",
             1.0, 6.15, 11.3, 0.4, 17, RED, True, PP_ALIGN.CENTER)

    # Slide 4: remove the agent lane and replace it with product/testing.
    architecture = prs.slides[3]
    for shape in list(architecture.shapes):
        y = shape.top / Inches(1)
        if 3.4 <= y <= 5.6:
            remove_shape(shape)
    card(architecture, 2.5, 4.05, 3.25, 1.25, LIGHT_GREEN, GREEN)
    add_text(architecture, "7  Streamlit dashboard", 2.75, 4.46, 2.75, 0.35, 16, GREEN, True)
    card(architecture, 7.55, 4.05, 3.25, 1.25, LIGHT_ORANGE, ORANGE)
    add_text(architecture, "8  Testing + report", 7.8, 4.46, 2.75, 0.35, 16, ORANGE, True)

    # Slide 12 after deletion: full dashboard screenshot with concise callouts.
    dashboard = prs.slides[11]
    clear_content(dashboard)
    if SCREENSHOT.exists():
        dashboard.shapes.add_picture(str(SCREENSHOT), Inches(0.55), Inches(1.25), width=Inches(8.1))
    for i, (title, body, fill, line) in enumerate([
        ("Explore", "Filter real cases by stock, label and move size.", LIGHT_BLUE, BLUE),
        ("Explain", "Inspect event windows, clues and Nifty comparison.", LIGHT_GREEN, GREEN),
        ("Evaluate", "Review confusion matrix and feature importance.", LIGHT_ORANGE, ORANGE),
    ]):
        y = 1.35 + i * 1.72
        card(dashboard, 9.0, y, 3.55, 1.35, fill, line)
        add_text(dashboard, title, 9.25, y + 0.2, 3.0, 0.3, 17, line, True)
        add_text(dashboard, body, 9.25, y + 0.65, 2.95, 0.48, 13)

    # Slide 13: limitations plus mitigation, rather than a wall of bullets.
    limits = prs.slides[12]
    clear_content(limits)
    card(limits, 0.8, 1.4, 5.7, 4.8, LIGHT_ORANGE, ORANGE)
    add_text(limits, "Current limitations", 1.15, 1.75, 5.0, 0.4, 20, RED, True)
    add_text(limits,
             "• Daily bars cannot prove exact causes.\n\n"
             "• Labels are transparent heuristics.\n\n"
             "• Volume-shock examples are limited.\n\n"
             "• Yahoo can temporarily fail for a ticker.",
             1.15, 2.4, 4.9, 2.9, 17)
    card(limits, 6.85, 1.4, 5.7, 4.8, LIGHT_GREEN, GREEN)
    add_text(limits, "How the project responds", 7.2, 1.75, 5.0, 0.4, 20, GREEN, True)
    add_text(limits,
             "• Uses careful language: “looks like,” not “caused by.”\n\n"
             "• Publishes every threshold and label rule.\n\n"
             "• Reports class support and honest caveats.\n\n"
             "• Skips failed downloads without inventing data.",
             7.2, 2.4, 4.9, 2.9, 17)

    # Completion slide: core project only.
    status = prs.slides[13]
    replace_text(
        PresentationWrapper(status),
        {
            "Model testing and validation": "Model evaluation and explainability",
            "Final analysis and report": "Dashboard, testing and final report",
        },
    )

    # Conclusion: remove remaining AI wording if it was split across runs.
    conclusion = prs.slides[14]
    for shape in conclusion.shapes:
        if getattr(shape, "has_text_frame", False):
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = run.text.replace("AI agents", "interactive dashboard")

    # Apply speaker notes.
    for slide, note in zip(prs.slides, SPEAKER_NOTES):
        set_notes(slide, note)

    prs.save(OUTPUT)
    lines = ["# MarketForensics polished final presentation notes", ""]
    for index, note in enumerate(SPEAKER_NOTES, start=1):
        lines.extend([f"## Slide {index}", note, ""])
    NOTES.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)
    print(NOTES)
    print(f"slides={len(prs.slides)}")


class PresentationWrapper:
    """Small adapter so replace_text can be reused for one slide."""

    def __init__(self, slide):
        self.slides = [slide]


if __name__ == "__main__":
    main()
