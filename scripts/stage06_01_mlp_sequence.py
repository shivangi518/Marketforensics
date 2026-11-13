"""Stage 06 (optional) — Small sklearn MLP vs last-10-day return sequence.

Skip if RAM is tight. Compares fairly to a dummy majority baseline, not the RF.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import json

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

from marketforensics.config import FEATURES, NIFTY_INDEX, RESULTS, ensure_data_dirs
from marketforensics.io import returns_csv


def window_features(ticker: str, date: str, n: int = 10) -> list[float] | None:
    path = returns_csv(ticker)
    if not path.exists():
        return None
    s = pd.read_csv(path, parse_dates=["Date"], index_col="Date")["return_pct"]
    event = pd.Timestamp(date)
    if event not in s.index:
        return None
    loc = s.index.get_loc(event)
    if isinstance(loc, slice) or loc < n:
        return None
    return [float(x) for x in s.iloc[loc - n : loc].tolist()]


def main() -> None:
    path = FEATURES / "case_features.csv"
    if not path.exists():
        raise SystemExit("Need labeled case_features.csv")
    df = pd.read_csv(path).dropna(subset=["label"])
    X, y = [], []
    for _, row in df.iterrows():
        if row["ticker"] == NIFTY_INDEX:
            continue
        vec = window_features(str(row["ticker"]), str(row["date"]))
        if vec:
            X.append(vec)
            y.append(row["label"])
    if len(X) < 30:
        raise SystemExit("Not enough sequence windows yet.")

    X = np.array(X)
    y = np.array(y)
    split = int(len(X) * 0.7)
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X[:split])
    Xte = scaler.transform(X[split:])
    clf = MLPClassifier(hidden_layer_sizes=(16,), max_iter=400, random_state=42)
    clf.fit(Xtr, y[:split])
    pred = clf.predict(Xte)
    acc = float(accuracy_score(y[split:], pred))
    ensure_data_dirs()
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "mlp_sequence_metrics.json"
    out.write_text(json.dumps({"accuracy": acc, "n": int(len(X))}, indent=2), encoding="utf-8")
    print(f"MLP accuracy: {acc:.3f} on {len(X)} windows -> {out}")


if __name__ == "__main__":
    main()
