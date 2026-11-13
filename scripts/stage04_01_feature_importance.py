"""Stage 04 — Global feature importance from the saved Random Forest."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json

import joblib
import pandas as pd

from marketforensics.config import MODELS, RESULTS, ensure_data_dirs


def main() -> None:
    model_path = MODELS / "rf_cause_v1.joblib"
    if not model_path.exists():
        raise SystemExit("Train the Random Forest first (Stage 03).")
    bundle = joblib.load(model_path)
    model = bundle["model"]
    names = bundle["features"]
    imp = pd.Series(model.feature_importances_, index=names).sort_values(ascending=False)
    ensure_data_dirs()
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "feature_importance.json"
    out.write_text(json.dumps(imp.to_dict(), indent=2), encoding="utf-8")
    print(imp.to_string())
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
