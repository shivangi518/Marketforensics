"""Stage 03 — Random Forest on time-based split (older train, newer test)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from marketforensics.config import FEATURES, MODELS, RESULTS, ensure_data_dirs

FEATURE_COLS = [
    "return_pct",
    "return_5d",
    "vol_20",
    "volume_vs_avg20",
    "above_ma",
    "momentum_5d",
    "vs_nifty",
    "dow",
]


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Run feature + label scripts first.")
    df = pd.read_csv(path, parse_dates=["date"]).dropna(subset=FEATURE_COLS + ["label"])
    df = df.sort_values("date")
    if len(df) < 20:
        raise SystemExit("Need more labeled cases (download a bigger universe).")

    split = int(len(df) * 0.7)
    train, test = df.iloc[:split], df.iloc[split:]
    X_train, y_train = train[FEATURE_COLS], train["label"]
    X_test, y_test = test[FEATURE_COLS], test["label"]

    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, pred))

    ensure_data_dirs()
    RESULTS.mkdir(parents=True, exist_ok=True)
    model_path = MODELS / "rf_cause_v1.joblib"
    joblib.dump({"model": model, "features": FEATURE_COLS}, model_path)

    metrics = {
        "accuracy": acc,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "labels": sorted(df["label"].unique().tolist()),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "report": classification_report(y_test, pred, zero_division=0),
    }
    out = RESULTS / "ml_baseline_metrics.json"
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Accuracy: {acc:.3f}")
    print(metrics["report"])
    print(f"Saved model -> {model_path}")
    print(f"Saved metrics -> {out}")


if __name__ == "__main__":
    main()
