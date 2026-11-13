"""Stage 05 — Fetch recent Google News RSS headlines for a company name."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.config import DEFAULT_TICKER, NEWS, ensure_data_dirs

TICKER = DEFAULT_TICKER
QUERY = "Reliance Industries NSE"


def main() -> None:
    ensure_data_dirs()
    q = urllib.parse.quote_plus(QUERY)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            xml = resp.read()
        root = ET.fromstring(xml)
        items = []
        for item in root.findall(".//item")[:20]:
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            pub = item.findtext("pubDate") or ""
            items.append({"title": title, "link": link, "published": pub})
    except Exception as exc:
        items = [{"title": f"(offline placeholder) news for {TICKER}", "link": "", "published": "", "error": str(exc)}]

    out = NEWS / f"{TICKER}_headlines.json"
    out.write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"Saved {len(items)} headlines -> {out}")


if __name__ == "__main__":
    main()
