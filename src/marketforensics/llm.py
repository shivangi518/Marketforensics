"""Model helper kept for older stage scripts.

Those scripts must not invent an answer when the key is missing.
The free provider is Gemini. Use run_pipeline.py --steps 7 for investigations.
"""

from __future__ import annotations

from dotenv import load_dotenv

from marketforensics.config import ROOT, PipelineError

load_dotenv(ROOT / ".env")


def chat(system: str, user: str) -> str:
    from marketforensics.agents import _groq_call

    try:
        return _groq_call(system, user)
    except PipelineError as exc:
        raise SystemExit(str(exc)) from exc
