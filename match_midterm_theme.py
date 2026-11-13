"""Restyle the Core ML final deck to match the supplied midterm PDF theme."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


BASE = Path(r"C:\Users\shivangi\Projects\marketforensics")
DOWNLOADS = Path(r"C:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads")
SOURCE = DOWNLOADS / "FINAL Term Presentation CAPSTONE Core ML.pptx"
OUTPUT = DOWNLOADS / "FINAL Term Presentation CAPSTONE Same Theme.pptx"
ASSETS = BASE / "docs" / "presentation_assets"
LOGO_A = ASSETS / "midterm_img_1_1.png"
LOGO_B = ASSETS / "midterm_img_1_2.png"

WHITE = RGBColor(255, 255, 255)
BLACK = RGBColor(20, 20, 20)
RED = RGBColor(192, 0, 0)
BLUE = RGBColor(47, 84, 150)
LIGHT_BLUE = RGBColor(221, 235, 247)
LIGHT_ORANGE = RGBColor(252, 228, 214)
LIGHT_GREEN = RGBColor(226, 240, 217)
LIGHT_GRAY = RGBColor(242, 242, 242)
GRAY = RGBColor(128, 128, 128)


def remove_shape(shape) -> None:
    element = shape._element
    element.getparent().remove(element)


def add_text(slide, text, x, y, w, h, size=18, color=BLACK, bold=False,
             align=PP_ALIGN.LEFT, font="Aptos"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def make_light_charts() -> tuple[Path, Path]:
    import json

    metrics = json.loads((BASE / "data/results/ml_baseline_metrics.json").read_text(encoding="utf-8"))
    labels = metrics["confusion_matrix_labels"]
    matrix = np.array(metrics["confusion_matrix"])

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="white")
    im = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(labels)), [x.replace("_", "\n") for x in labels])
    ax.set_yticks(range(len(labels)), [x.replace("_", "\n") for x in labels])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", color="black", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    confusion = ASSETS / "confusion_matrix_light.png"
    fig.savefig(confusion, dpi=170, facecolor="white")
    plt.close(fig)

    scores = metrics["permutation_importance_mean"]
    items = sorted(scores.items(), key=lambda item: item[1])
    fig, ax = plt.subplots(figsize=(7, 4.4), facecolor="white")
    ax.barh([k for k, _ in items], [v for _, v in items], color="#2F5597")
    ax.axvline(0, color="black", linewidth=0.7)
    ax.set_xlabel("Decrease in test accuracy after permutation")
    ax.set_title("Permutation importance")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    importance = ASSETS / "permutation_importance_light.png"
    fig.savefig(importance, dpi=170, facecolor="white")
    plt.close(fig)
    return confusion, importance


def add_logos_and_footer(slide, number: int) -> None:
    slide.shapes.add_picture(str(LOGO_A), Inches(0.18), Inches(0.1), width=Inches(0.78))
    slide.shapes.add_picture(str(LOGO_B), Inches(0.98), Inches(0.1), width=Inches(1.42))
    add_text(slide, "10-11-2026", 0.35, 7.15, 1.2, 0.18, 7, GRAY)
    add_text(slide, "Computer Science and Engineering Dept.", 5.1, 7.15, 3.2, 0.18, 7, GRAY, align=PP_ALIGN.CENTER)
    add_text(slide, str(number), 12.25, 7.15, 0.4, 0.18, 7, GRAY, align=PP_ALIGN.RIGHT)


def rebuild_title(slide) -> None:
    for shape in list(slide.shapes):
        remove_shape(shape)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    slide.shapes.add_picture(str(LOGO_A), Inches(0.3), Inches(0.18), width=Inches(1.2))
    slide.shapes.add_picture(str(LOGO_B), Inches(1.62), Inches(0.18), width=Inches(2.2))
    add_text(slide, "CAPSTONE PROJECT\nFINAL TERM PRESENTATION", 4.05, 0.32, 5.25, 0.85, 20, RED, False, align=PP_ALIGN.CENTER, font="Times New Roman")
    add_text(slide, "MARKETFORENSICS", 3.7, 1.55, 5.9, 0.55, 25, BLUE, False, align=PP_ALIGN.CENTER, font="Times New Roman")

    # Presenter information box
    box = slide.shapes.add_shape(1, Inches(2.45), Inches(2.48), Inches(8.35), Inches(2.55))
    box.fill.background()
    box.line.color.rgb = BLUE
    box.line.width = Pt(1.25)
    add_text(slide, "Presented by", 3.1, 2.75, 2.2, 0.28, 15, BLACK, False, align=PP_ALIGN.CENTER, font="Times New Roman")
    add_text(slide, "Name\nEnroll. no.\nDate", 3.0, 3.25, 1.45, 0.9, 14, BLACK, font="Times New Roman")
    add_text(slide, ": Shivangi Padhi\n: 24BCAHH010160\n: 10-11-2026", 4.35, 3.25, 2.7, 0.9, 14, BLACK, font="Times New Roman")
    add_text(slide, "Project Faculty Mentor", 7.6, 2.75, 2.5, 0.28, 15, BLACK, False, align=PP_ALIGN.CENTER, font="Times New Roman")
    add_text(slide, "Name\nDesignation\nDept.", 7.2, 3.25, 1.35, 0.9, 14, BLACK, font="Times New Roman")
    add_text(slide, ": Mr. P Senthil Raja\n: Assistant Professor\n: AI & DS", 8.55, 3.25, 2.0, 0.9, 14, BLACK, font="Times New Roman")
    add_text(slide, "Computer Science and Engineering Dept.", 5.0, 7.13, 3.35, 0.18, 7, GRAY, align=PP_ALIGN.CENTER)


def style_slide(slide, number: int) -> None:
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    # Remove old dark-theme section tags, footer and decorative left bar.
    for shape in list(slide.shapes):
        x = shape.left / Inches(1)
        y = shape.top / Inches(1)
        w = shape.width / Inches(1)
        text = shape.text.strip() if getattr(shape, "has_text_frame", False) else ""
        if (x < 0.2 and w < 0.2) or y > 6.95 or (y < 0.5 and text.isupper() and len(text) < 30):
            remove_shape(shape)

    # Recolour shapes and text.
    pastel_index = 0
    for shape in list(slide.shapes):
        if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            fills = (LIGHT_BLUE, LIGHT_ORANGE, LIGHT_GREEN, LIGHT_GRAY)
            shape.fill.solid()
            shape.fill.fore_color.rgb = fills[pastel_index % len(fills)]
            shape.line.color.rgb = BLUE
            shape.line.width = Pt(0.8)
            pastel_index += 1
        if getattr(shape, "has_text_frame", False):
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.name = "Aptos"
                    run.font.color.rgb = BLACK
                    if run.font.size and run.font.size.pt > 24:
                        run.font.size = Pt(22)

    # Identify the main title near the top.
    title_candidates = [
        shape for shape in slide.shapes
        if getattr(shape, "has_text_frame", False)
        and shape.text.strip()
        and shape.top / Inches(1) < 1.25
        and shape.width / Inches(1) > 4
    ]
    if title_candidates:
        title = max(title_candidates, key=lambda s: s.width)
        title.left = Inches(2.4)
        title.top = Inches(0.36)
        title.width = Inches(8.5)
        title.height = Inches(0.55)
        for paragraph in title.text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER
            for run in paragraph.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(22)
                run.font.bold = False
                run.font.color.rgb = RED

    add_logos_and_footer(slide, number)


def replace_chart(slide, image_path: Path) -> None:
    pictures = [shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
    # Logos are not present yet when this function is called; select the largest picture.
    if not pictures:
        return
    picture = max(pictures, key=lambda shape: shape.width * shape.height)
    left, top, width, height = picture.left, picture.top, picture.width, picture.height
    remove_shape(picture)
    slide.shapes.add_picture(str(image_path), left, top, width=width, height=height)


def main() -> None:
    confusion, importance = make_light_charts()
    prs = Presentation(SOURCE)
    rebuild_title(prs.slides[0])
    for number, slide in enumerate(list(prs.slides)[1:], start=2):
        # Replace dark result charts before adding logos.
        if number == 8:
            replace_chart(slide, confusion)
        elif number == 9:
            replace_chart(slide, importance)
        style_slide(slide, number)
    prs.save(OUTPUT)
    print(OUTPUT)
    print(f"slides={len(prs.slides)}")


if __name__ == "__main__":
    main()
