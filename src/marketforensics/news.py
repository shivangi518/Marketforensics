"""Headlines for a case. Only items whose publish time is within one day of the case.

Current RSS is not attached to old dates. If nothing matches, the list stays empty.
"""

from __future__ import annotations

import json
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import pandas as pd
import requests

from marketforensics.config import NEWS, PipelineError, ensure_data_dirs


def _company_query(ticker: str) -> str:
    return ticker.replace(".NS", "").replace("&", " ")


def fetch_headlines(ticker: str, date: str) -> list[dict]:
    ensure_data_dirs()
    day = pd.Timestamp(date).tz_localize(None)
    if abs((pd.Timestamp.utcnow().tz_localize(None) - day).days) > 3:
        return []
    query = requests.utils.quote(_company_query(ticker) + " NSE")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as exc:
        raise PipelineError(
            f"Headline fetch failed for {ticker} {date}: {exc}\n"
            "The pipeline will not invent headlines. Retry when the network allows, "
            "or continue agents with an empty list by catching this in run_step."
        ) from exc
    kept = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub = item.findtext("pubDate") or ""
        try:
            published = pd.Timestamp(parsedate_to_datetime(pub)).tz_localize(None)
        except Exception:
            continue
        if abs((published - day).days) <= 1 and title:
            kept.append({"title": title, "link": link, "published": pub, "source": "Google News RSS"})
    out = NEWS / f"{ticker}_{day.strftime('%Y-%m-%d')}.json"
    out.write_text(json.dumps(kept, indent=2), encoding="utf-8")
    return kept
