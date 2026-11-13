"""Make `src/` importable when scripts are run from the repo root."""

from __future__ import annotations

import sys
from pathlib import Path


def add_src_to_path(stage_file: str) -> Path:
    """Insert src/ onto sys.path. Pass __file__ from a stage script."""
    stage_path = Path(stage_file).resolve()
    # scripts/script.py -> repo root is parent
    root = stage_path.parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return root
