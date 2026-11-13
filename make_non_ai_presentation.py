"""Create an editable final-term PPT without the Generative-AI agent section."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


SOURCE = Path(
    r"C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads"
    r"\FINAL Term Presentation CAPSTONE.pptx"
)
OUTPUT = SOURCE.with_name("FINAL Term Presentation CAPSTONE Core ML.pptx")

NAVY = RGBColor(6, 12, 22)
PANEL = RGBColor(14, 24, 40)
WHITE = RGBColor(235, 241, 249)
MUTED = RGBColor(159, 173, 194)
CYAN = RGBColor(0, 229, 255)
GREEN = RGBColor(0, 230, 118)
AMBER = RGBColor(255, 179, 0)


def delete_slide(prs, number: int) -> None:
    slide = prs.slides[number - 1]
    slide_id = slide.slide_id
    prs.part.drop_rel(prs.slides._sldIdLst[number - 1].rId)
    for item in list(prs.slides._sldIdLst):
        if item.id == slide_id:
            prs.slides._sldIdLst.remove(item)
            break


def replace_all(prs, replacements: dict[str, str]) -> None:
    for slide in prs.slides:
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    for old, new in replacements.items():
                        if old in run.text:
                            run.text = run.text.replace(old, new)


def remove_shape(shape) -> None:
    element = shape._element
    element.getparent().remove(element)


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT):
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


def add_card(slide, x, y, w, h, line=CYAN):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL
    shape.line.color.rgb = line
    shape.line.transparency = 35
    return shape


def main() -> None:
    prs = Presentation(SOURCE)

    # Remove the three completed Generative-AI slides and the "after midterm" AI summary.
    for number in (14, 13, 12, 2):
        delete_slide(prs, number)

    replace_all(
        prs,
        {
            "rules, machine learning and AI agents": "statistical rules and machine learning",
            "Generate evidence-bounded AI case notes.": "Build interactive evidence-based visualisations.",
            "Evaluate direction calls honestly.": "Evaluate model performance on later dates.",
            "Groq solo, team and debate agents": "Model testing and validation",
            "Direction evaluation and report": "Final analysis and report",
            "Agents, Debate and Backtest: saved outputs only; friendly locked state if missing":
                "Saved charts and model outputs only; friendly messages if files are missing",
            "Groq output can be incomplete or wrong and is constrained by rate limits.":
                "Daily market data cannot identify an exact corporate cause by itself.",
            "Only 14 recent solo cases were available for the 30-day direction check.":
                "The volume-shock class has only 26 cases, so that class is less certain.",
            "transparent labels → time-split model → evidence-bounded AI agents → honest direction evaluation":
                "transparent labels → time-split model → explainability → interactive dashboard",
            "Groq API documentation — structured AI completions":
                "Matplotlib documentation — static analytical figures",
        },
    )

    # Original architecture slide is now slide 3. Remove the lower AI-agent lane.
    architecture = prs.slides[2]
    for shape in list(architecture.shapes):
        top = shape.top / Inches(1)
        if 3.45 <= top <= 5.55:
            remove_shape(shape)
    add_card(architecture, 3.0, 4.05, 3.0, 1.3, GREEN)
    add_text(architecture, "7", 3.2, 4.22, 0.35, 0.3, 13, GREEN, True)
    add_text(architecture, "Streamlit dashboard", 3.2, 4.65, 2.55, 0.35, 15, WHITE, True)
    add_card(architecture, 7.35, 4.05, 3.0, 1.3, AMBER)
    add_text(architecture, "8", 7.55, 4.22, 0.35, 0.3, 13, AMBER, True)
    add_text(architecture, "Testing + report", 7.55, 4.65, 2.55, 0.35, 15, WHITE, True)

    # Remove any remaining text paragraphs that mention agents or Groq.
    for slide in prs.slides:
        for shape in list(slide.shapes):
            if not getattr(shape, "has_text_frame", False):
                continue
            text = shape.text.lower()
            if (
                "groq" in text
                or "solo, team" in text
                or "agent direction" in text
                or "debate" in text
            ):
                if shape.top / Inches(1) < 6.95:
                    remove_shape(shape)

    prs.save(OUTPUT)
    print(OUTPUT)
    print(f"slides={len(prs.slides)}")


if __name__ == "__main__":
    main()
