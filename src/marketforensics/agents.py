"""Step 7: case files plus agents A, B, and C. No stand-in answers.

The free path is Gemini. Groq stays available only when LLM_PROVIDER=groq.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from marketforensics.config import (
    AGENT_CACHE,
    CASES,
    CASES_JSON,
    FEATURES,
    GEMINI_MODEL_DEFAULT,
    GROQ_MODEL_DEFAULT,
    RESULTS_A,
    RESULTS_B,
    RESULTS_C,
    ROOT,
    PipelineError,
    ensure_data_dirs,
)
from marketforensics.mystery import explained_and_mystery
from marketforensics.news import fetch_headlines

load_dotenv(ROOT / ".env")

CAUSES = {"market_wide", "stock_specific", "volume_shock", "unknown"}
DIRECTIONS = {"up", "down", "unclear"}

PERSONAS = {
    "numbers": (
        "You are the numbers analyst. Use only the numeric clues in the case JSON. "
        "Do not invent news, filings, or prices that are not in the JSON."
    ),
    "news": (
        "You are the news analyst. Use only the headlines array in the case JSON. "
        "If it is empty, say the file has no matched headline and do not invent one."
    ),
    "skeptic": (
        "You are the risk skeptic. Challenge the other story. "
        "Use only the case JSON. Say what the clues do not prove."
    ),
}


def _provider() -> str:
    name = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if name == "groq":
        return "groq"
    return "gemini"


def provider_label() -> str:
    return "Groq" if _provider() == "groq" else "Gemini"


def _model_name() -> str:
    if _provider() == "groq":
        return os.getenv("GROQ_MODEL", GROQ_MODEL_DEFAULT).strip() or GROQ_MODEL_DEFAULT
    return os.getenv("GEMINI_MODEL", GEMINI_MODEL_DEFAULT).strip() or GEMINI_MODEL_DEFAULT


def _require_key() -> str:
    if _provider() == "groq":
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            raise PipelineError(
                "GROQ_API_KEY is empty.\n"
                "The default free provider is Gemini. Set LLM_PROVIDER=gemini in .env,\n"
                "or paste a Groq key if you still want Groq."
            )
        return key
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise PipelineError(
            "GEMINI_API_KEY is empty. Groq's free daily limit is no longer the agent path.\n"
            "Get a free key at https://aistudio.google.com/apikey\n"
            "Then put these lines in .env:\n"
            "  LLM_PROVIDER=gemini\n"
            "  GEMINI_API_KEY=your_key\n"
            "  GEMINI_MODEL=gemini-2.5-flash\n"
            "Retry one case from the Agents page. Saved replies still open without a key."
        )
    return key


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cache_file(version: str, persona: str, ticker: str, date: str, prompt_hash: str) -> Path:
    safe_ticker = ticker.replace("^", "")
    return AGENT_CACHE / f"{version}_{persona}_{safe_ticker}_{date}_{prompt_hash[:16]}.json"


def _parse_agent(text: str) -> dict:
    raw = text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise PipelineError("Model reply was not JSON.")
        data = json.loads(raw[start : end + 1])
    if not isinstance(data, dict):
        raise PipelineError("Model JSON was not an object.")
    cause = str(data.get("cause", "")).strip()
    direction = str(data.get("direction", "")).strip()
    if cause not in CAUSES or direction not in DIRECTIONS:
        raise PipelineError(f"Model JSON used cause={cause!r} direction={direction!r}.")
    try:
        confidence = int(round(float(data["confidence"])))
    except (KeyError, TypeError, ValueError) as exc:
        raise PipelineError("Model JSON missing numeric confidence.") from exc
    explanation = str(data.get("explanation", "")).strip()
    if not explanation:
        raise PipelineError("Model JSON missing explanation.")
    data["cause"] = cause
    data["direction"] = direction
    data["confidence"] = max(0, min(100, confidence))
    data["explanation"] = explanation
    return data


def _rate_limit_wait(exc: Exception) -> int | None:
    text = str(exc)
    lowered = text.lower()
    if "429" not in text and "rate_limit" not in lowered and "resource_exhausted" not in lowered and "quota" not in lowered:
        return None
    match = re.search(r"try again in (\d+)m(\d+(?:\.\d+)?)s", text, re.I)
    if match:
        return int(int(match.group(1)) * 60 + float(match.group(2))) + 2
    match = re.search(r"try again in (\d+(?:\.\d+)?)s", text, re.I)
    if match:
        return int(float(match.group(1))) + 2
    return 30


def _gemini_text(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        raise PipelineError("Gemini returned no candidates.")
    parts = ((candidates[0].get("content") or {}).get("parts")) or []
    return "".join(str(part.get("text") or "") for part in parts).strip()


def _gemini_call(system: str, user: str) -> str:
    import requests

    key = _require_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{_model_name()}:generateContent"
    last_error: Exception | None = None
    for attempt in range(3):
        for json_mode in (True, False):
            body = {
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"temperature": 0.2},
            }
            if json_mode:
                body["generationConfig"]["responseMimeType"] = "application/json"
            try:
                resp = requests.post(
                    url,
                    headers={"x-goog-api-key": key},
                    json=body,
                    timeout=90,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(f"{resp.status_code} {resp.text[:400]}")
                content = _gemini_text(resp.json())
                if not content:
                    raise PipelineError("Gemini returned an empty reply.")
                return content
            except PipelineError:
                raise
            except Exception as exc:
                last_error = exc
                if json_mode and "429" not in str(exc) and "quota" not in str(exc).lower():
                    continue
                break
        wait = _rate_limit_wait(last_error or Exception("gemini"))
        if wait is not None and wait > 45:
            raise PipelineError(
                "Gemini's free quota is used up for now.\n"
                "Saved notes on the Agents page still open. Wait for the free quota to reset, then retry one case."
            )
        time.sleep(wait if wait is not None else 2 ** attempt)
    raise PipelineError(
        "Gemini refused the call after retries.\n"
        "Open Agents and pick a saved investigation. Do not invent a reply.\n"
        f"Last error: {last_error}"
    )


def _groq_only(system: str, user: str) -> str:
    try:
        from groq import Groq
    except ImportError as exc:
        raise PipelineError(
            "Package groq is not installed.\nInstall with:\n  python -m pip install groq"
        ) from exc
    client = Groq(api_key=_require_key())
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            try:
                resp = client.chat.completions.create(
                    model=_model_name(),
                    messages=messages,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
            except Exception as exc:
                if "429" in str(exc) or "rate" in str(exc).lower():
                    raise
                resp = client.chat.completions.create(
                    model=_model_name(),
                    messages=messages,
                    temperature=0.2,
                )
            content = resp.choices[0].message.content or ""
            return content
        except Exception as exc:
            last_error = exc
            wait = _rate_limit_wait(exc)
            if wait is None:
                wait = 2 ** attempt
            elif wait > 360:
                raise PipelineError(
                    "Groq's daily token limit is used up.\n"
                    "Saved notes on the Agents page still open. Wait until Groq resets "
                    "(the error says when), then retry one case:\n"
                    "  python run_pipeline.py --steps 7 --ticker TITAN.NS --date 2026-08-10"
                )
            print(f"  Groq error ({exc}); sleeping {wait}s")
            time.sleep(wait)
    raise PipelineError(
        "Groq refused new calls after retries (often a 429 daily token cap).\n"
        "Open Agents and pick a saved investigation. Do not invent a reply.\n"
        f"Last error: {last_error}"
    )


def _groq_call(system: str, user: str) -> str:
    """Route to the free Gemini tier unless .env sets LLM_PROVIDER=groq."""
    if _provider() == "groq":
        return _groq_only(system, user)
    return _gemini_call(system, user)


def complete_json(
    version: str,
    persona: str,
    ticker: str,
    date: str,
    system: str,
    user: str,
    log=None,
) -> dict:
    prompt = system + "\n" + user
    digest = _hash(prompt)
    cache = _cache_file(version, persona, ticker, date, digest)
    ensure_data_dirs()
    if cache.exists():
        cached = json.loads(cache.read_text(encoding="utf-8"))
        if log:
            log(f"cache hit {version}/{persona} {ticker} {date}")
        return {
            "parsed": _parse_agent(cached["response"]),
            "raw": cached["response"],
            "cache": "hit",
            "latency_s": 0.0,
            "model": cached.get("model", _model_name()),
        }
    started = time.perf_counter()
    text = _groq_call(system, user)
    latency = time.perf_counter() - started
    parsed = _parse_json_with_repair(version, persona, ticker, date, system, user, text)
    cache.write_text(
        json.dumps({"response": parsed["raw"], "model": _model_name()}, indent=2),
        encoding="utf-8",
    )
    if log:
        log(f"cache miss {version}/{persona} {ticker} {date} ({latency:.1f}s)")
    parsed["cache"] = "miss"
    parsed["latency_s"] = round(latency, 3)
    parsed["model"] = _model_name()
    return parsed


def _parse_json_with_repair(version, persona, ticker, date, system, user, text: str) -> dict:
    """Retry the call when the body is not the required JSON. Never fill a fake answer."""
    try:
        parsed = _parse_agent(text)
        return {"parsed": parsed, "raw": text}
    except PipelineError:
        repaired_user = user + "\n\nYour previous reply was invalid. Reply with one JSON object only."
        text2 = _groq_call(system + " Reply with JSON keys explanation, cause, confidence, direction.", repaired_user)
        parsed = _parse_agent(text2)
        return {"parsed": parsed, "raw": text2}


def _instruction() -> str:
    return (
        "Reply with one JSON object and no markdown. Keys: "
        "explanation (string), cause (market_wide|stock_specific|volume_shock|unknown), "
        "confidence (integer 0-100), direction (up|down|unclear)."
    )


def load_feature_table() -> pd.DataFrame:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise PipelineError(
            f"Missing {path}\nCreate it with:\n  python run_pipeline.py --steps 5"
        )
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise PipelineError(
            "case_features.csv has no label column.\n"
            "Create it with:\n  python run_pipeline.py --steps 6"
        )
    return df


def _top_clues(ticker: str, date: str) -> list[str]:
    path = CASES / "sample_explanations.json"
    if not path.exists():
        raise PipelineError(
            f"Missing {path}\nCreate it with:\n  python run_pipeline.py --steps 6"
        )
    blob = json.loads(path.read_text(encoding="utf-8"))
    clues = blob.get(f"{ticker}|{date}")
    if not isinstance(clues, list):
        raise PipelineError(f"No top-3 clues for {ticker} {date}. Re-run step 6.")
    return [str(x) for x in clues]


def case_record(row: pd.Series, headlines: list[dict] | None = None) -> dict:
    ticker = str(row["ticker"])
    date = str(row["date"])[:10]
    explained, mystery = explained_and_mystery(
        float(row["return_pct"]),
        float(row["nifty_return_pct"]) if pd.notna(row.get("nifty_return_pct")) else float("nan"),
        float(row["volume_vs_avg20"]) if pd.notna(row.get("volume_vs_avg20")) else float("nan"),
    )
    features = {}
    for key, value in row.items():
        if key in {"ticker", "date"}:
            continue
        features[str(key)] = None if pd.isna(value) else value
    if headlines is None:
        try:
            headlines = fetch_headlines(ticker, date)
        except PipelineError as exc:
            print(f"  headlines skipped for {ticker} {date}: {exc}")
            headlines = []
    return {
        "ticker": ticker,
        "date": date,
        "return_pct": float(row["return_pct"]),
        "features": features,
        "ml_cause_guess": str(row.get("label")),
        "top_clues": _top_clues(ticker, date),
        "headlines": headlines,
        "explained_pct": explained,
        "mystery_score": mystery,
    }


def write_case_json(record: dict) -> Path:
    ensure_data_dirs()
    path = CASES_JSON / f"{record['ticker']}_{record['date']}.json"
    path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    return path


def _user_prompt(record: dict, extra: str = "") -> str:
    body = json.dumps(
        {
            "ticker": record["ticker"],
            "date": record["date"],
            "return_pct": record["return_pct"],
            "features": record["features"],
            "ml_cause_guess": record["ml_cause_guess"],
            "top_clues": record["top_clues"],
            "headlines": record["headlines"],
            "mystery_score": record["mystery_score"],
        },
        default=str,
    )
    return body + ("\n" + extra if extra else "") + "\n" + _instruction()


def _majority(values: list[str]) -> str:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "unclear" if ranked[0][0] in DIRECTIONS else "unknown"
    return ranked[0][0]


def run_investigation(ticker: str, date: str, log=None) -> dict:
    """Run versions A, B, and C for one real case. Raises if inputs or Groq fail."""
    _require_key()
    table = load_feature_table()
    day = str(date)[:10]
    match = table[(table["ticker"].astype(str) == ticker) & (table["date"].astype(str).str.slice(0, 10) == day)]
    if match.empty:
        raise PipelineError(
            f"No feature row for {ticker} {day}.\n"
            "Build cases first:\n  python run_pipeline.py --steps 1-6"
        )
    record = case_record(match.iloc[0])
    write_case_json(record)
    user = _user_prompt(record)
    solo_system = "You explain one already-observed NSE price jump from the case JSON only. " + _instruction()
    solo = complete_json("A", "solo", ticker, day, solo_system, user, log=log)

    opinions = {}
    for name, system in PERSONAS.items():
        opinions[name] = complete_json("B", name, ticker, day, system + " " + _instruction(), user, log=log)
    vote_cause = _majority([item["parsed"]["cause"] for item in opinions.values()])
    vote_direction = _majority([item["parsed"]["direction"] for item in opinions.values()])
    if vote_cause == "unclear":
        vote_cause = "unknown"
    version_b = {
        "version": "B",
        "ticker": ticker,
        "date": day,
        "vote_cause": vote_cause,
        "vote_direction": vote_direction,
        "personas": opinions,
    }

    round1 = {}
    for name, system in PERSONAS.items():
        round1[name] = complete_json("C", f"{name}_r1", ticker, day, system + " " + _instruction(), user, log=log)
    visible = json.dumps({name: item["parsed"] for name, item in round1.items()}, indent=2)
    round2 = {}
    for name, system in PERSONAS.items():
        rebuttal = _user_prompt(record, extra="Other round-1 answers:\n" + visible + "\nWrite your rebuttal JSON.")
        round2[name] = complete_json(
            "C",
            f"{name}_r2",
            ticker,
            day,
            system + " Rebut the others using only the case and their answers. " + _instruction(),
            rebuttal,
            log=log,
        )
    chair_user = _user_prompt(
        record,
        extra="Round 1:\n"
        + json.dumps({k: v["parsed"] for k, v in round1.items()})
        + "\nRound 2:\n"
        + json.dumps({k: v["parsed"] for k, v in round2.items()}),
    )
    chair = complete_json(
        "C",
        "chair",
        ticker,
        day,
        "You are the chair. Synthesize the debate. Do not add facts that are not in the case or the debate. "
        + _instruction(),
        chair_user,
        log=log,
    )
    version_c = {
        "version": "C",
        "ticker": ticker,
        "date": day,
        "round1": round1,
        "round2": round2,
        "chair": chair,
    }
    version_a = {"version": "A", "ticker": ticker, "date": day, **solo}
    ensure_data_dirs()
    path_a = RESULTS_A / f"{ticker}_{day}.json"
    path_b = RESULTS_B / f"{ticker}_{day}.json"
    path_c = RESULTS_C / f"{ticker}_{day}.json"
    path_a.write_text(json.dumps(version_a, indent=2), encoding="utf-8")
    path_b.write_text(json.dumps(version_b, indent=2), encoding="utf-8")
    path_c.write_text(json.dumps(version_c, indent=2), encoding="utf-8")
    return {"A": version_a, "B": version_b, "C": version_c, "files": [str(path_a), str(path_b), str(path_c)]}


def run_step(n: int = 50, ticker: str | None = None, date: str | None = None) -> dict:
    if ticker and date:
        result = run_investigation(ticker, date, log=print)
        print(f"STEP 7 summary: rows in=1, rows out=1 case investigated")
        return {"rows_in": 1, "rows_out": 1, "files": result["files"], "notes": f"{ticker} {date}"}
    table = load_feature_table()
    table = table.sort_values("date")
    chosen = table.tail(int(n))
    if chosen.empty:
        raise PipelineError("No feature rows to investigate. Run steps 1-6.")
    files: list[str] = []
    failures = []
    for _, row in chosen.iterrows():
        try:
            result = run_investigation(str(row["ticker"]), str(row["date"])[:10], log=print)
            files.extend(result["files"])
        except PipelineError as exc:
            failures.append({"ticker": str(row["ticker"]), "date": str(row["date"])[:10], "error": str(exc)})
            print(f"  FAILED {row['ticker']} {row['date']}: {exc}")
    if len(files) == 0:
        raise PipelineError("Every agent case failed. See messages above. No substitute answers were written.")
    print(f"STEP 7 summary: rows in={len(chosen)}, rows out={len(files) // 3} cases, failures={len(failures)}")
    return {
        "rows_in": int(len(chosen)),
        "rows_out": len(files) // 3,
        "files": files,
        "notes": f"failures={len(failures)}",
    }
