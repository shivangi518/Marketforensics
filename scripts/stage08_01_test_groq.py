"""Stage 08 — Test Groq (or dummy mode) with one prompt."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketforensics.llm import chat


def main() -> None:
    print(chat("You are a helpful test bot.", "Reply with: MarketForensics Groq test OK"))


if __name__ == "__main__":
    main()
