"""Step 6: rule labels, time-split random forest, global and per-case importance."""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from marketforensics.config import (
    CASES,
    FEATURES,
    LABEL_MARKET_ABS,
    LABEL_STOCK_VS,
    LABEL_VOLUME_RATIO,
    MODELS,
    RESULTS,
    PipelineError,
    ensure_data_dirs,
)

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


def assign_label(row: pd.Series) -> str:
    """First match wins. Thresholds live in config.py.

    1. market_wide if |Nifty return| >= LABEL_MARKET_ABS
    2. stock_specific if |stock − Nifty| >= LABEL_STOCK_VS
    3. volume_shock if volume / 20-day average >= LABEL_VOLUME_RATIO
    4. unknown otherwise
    """
    nifty = row.get("nifty_return_pct")
    vs = row.get("vs_nifty")
    ratio = row.get("volume_vs_avg20")
    if pd.notna(nifty) and abs(float(nifty)) >= LABEL_MARKET_ABS:
        return "market_wide"
    if pd.notna(vs) and abs(float(vs)) >= LABEL_STOCK_VS:
        return "stock_specific"
    if pd.notna(ratio) and float(ratio) >= LABEL_VOLUME_RATIO:
        return "volume_shock"
    return "unknown"


def _frame(values: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame([values], columns=FEATURE_COLS)


def _local_top3(model, row: np.ndarray, medians: np.ndarray, class_index: int) -> list[str]:
    base = model.predict_proba(_frame(row))[0][class_index]
    drops = []
    for j, name in enumerate(FEATURE_COLS):
        tweaked = row.copy()
        tweaked[j] = medians[j]
        score = model.predict_proba(_frame(tweaked))[0][class_index]
        drops.append((base - score, name, float(row[j])))
    drops.sort(key=lambda item: item[0], reverse=True)
    return [f"{name}={value:.3f} (proba drop {drop:.3f})" for drop, name, value in drops[:3]]


def run_ml() -> dict:
    ensure_data_dirs()
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise PipelineError(
            f"Missing {path}\nCreate it with:\n  python run_pipeline.py --steps 5"
        )
    df = pd.read_csv(path)
    rows_in = len(df)
    df["label"] = df.apply(assign_label, axis=1)
    df.to_csv(path, index=False)
    usable = df.dropna(subset=FEATURE_COLS + ["label"]).sort_values(["date", "ticker"])
    if len(usable) < 20:
        raise PipelineError(
            f"Only {len(usable)} complete feature rows. Need at least 20 for a time split.\n"
            "Download more stocks:\n  python run_pipeline.py --steps 1-5"
        )
    counts = usable["label"].value_counts().to_dict()
    dates = sorted(usable["date"].unique())
    cut_date = dates[max(1, int(len(dates) * 0.7))]
    train = usable[usable["date"] < cut_date]
    test = usable[usable["date"] >= cut_date]
    if train["label"].nunique() < 2 or len(test) < 5:
        raise PipelineError(
            "Time split does not have two classes in train and 5 test rows.\n"
            "Collect more cases and re-run:\n  python run_pipeline.py --steps 3-6"
        )
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=1,
    )
    model.fit(train[FEATURE_COLS], train["label"])
    pred = model.predict(test[FEATURE_COLS])
    labels = sorted(usable["label"].unique())
    acc = float(accuracy_score(test["label"], pred))
    perm = permutation_importance(
        model,
        test[FEATURE_COLS],
        test["label"],
        n_repeats=5,
        random_state=42,
        n_jobs=1,
    )
    medians = train[FEATURE_COLS].median().to_numpy()
    explanations: dict[str, list[str]] = {}
    for _, row in usable.iterrows():
        values = row[FEATURE_COLS].to_numpy(dtype=float)
        guess = model.predict(_frame(values))[0]
        class_index = list(model.classes_).index(guess)
        key = f"{row['ticker']}|{row['date']}"
        explanations[key] = _local_top3(model, values, medians, class_index)

    honest = []
    for label, count in counts.items():
        if int(count) < 5:
            honest.append(f"Class {label} has only {int(count)} rows. Accuracy for that class is not reliable.")
    honest.append(
        "The label is a rule on the Nifty return, the gap versus Nifty, and the volume ratio, "
        "and those same numbers are features. A high accuracy means the forest reproduced that rule "
        "on later dates. It does not mean a person confirmed the cause."
    )

    RESULTS.mkdir(parents=True, exist_ok=True)
    model_path = MODELS / "rf_cause_v1.joblib"
    joblib.dump(
        {"model": model, "features": FEATURE_COLS, "train_medians": medians, "classes": list(model.classes_)},
        model_path,
    )
    metrics = {
        "accuracy": acc,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "train_last_date": str(train["date"].iloc[-1]),
        "test_first_date": str(test["date"].iloc[0]),
        "class_counts": {str(k): int(v) for k, v in counts.items()},
        "label_thresholds": {
            "market_wide_abs_nifty": LABEL_MARKET_ABS,
            "stock_specific_abs_vs_nifty": LABEL_STOCK_VS,
            "volume_shock_ratio": LABEL_VOLUME_RATIO,
            "order": "market_wide, then stock_specific, then volume_shock, else unknown",
        },
        "confusion_matrix_labels": labels,
        "confusion_matrix": confusion_matrix(test["label"], pred, labels=labels).tolist(),
        "classification_report": classification_report(test["label"], pred, zero_division=0),
        "feature_importance": {
            name: float(value) for name, value in zip(FEATURE_COLS, model.feature_importances_)
        },
        "permutation_importance_mean": {
            name: float(value) for name, value in zip(FEATURE_COLS, perm.importances_mean)
        },
        "honest_notes": honest,
    }
    metrics_path = RESULTS / "ml_baseline_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    expl_path = CASES / "sample_explanations.json"
    expl_path.write_text(json.dumps(explanations, indent=2), encoding="utf-8")
    print(f"STEP 6 summary: rows in={rows_in}, rows out={len(usable)} labeled, test accuracy={acc:.3f}")
    for note in honest:
        print(f"  note: {note}")
    print(metrics["classification_report"])
    return {
        "rows_in": rows_in,
        "rows_out": int(len(usable)),
        "files": [str(model_path), str(metrics_path), str(expl_path), str(path)],
        "notes": f"accuracy={acc:.3f}",
    }
