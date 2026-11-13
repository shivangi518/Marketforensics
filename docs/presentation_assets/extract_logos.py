import pymupdf
from pathlib import Path

src = Path(r"c:\Users\shivangi\Dropbox\My PC (LAPTOP-Q3DGSR28)\Downloads\MID term Presentation CAPSTONE.pdf")
out = Path(r"C:\Users\shivangi\Projects\marketforensics\docs\presentation_assets")
doc = pymupdf.open(src)
page = doc[0]
for i, img in enumerate(page.get_images(full=True)):
    info = doc.extract_image(img[0])
    p = out / f"logo_raw_{i}.{info['ext']}"
    p.write_bytes(info["image"])
    print(i, info["ext"], info["width"], info["height"], info["colorspace"], p)
for b in page.get_image_info():
    print(b["xref"], b["bbox"], b["width"], b["height"])
