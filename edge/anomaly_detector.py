import argparse
import json
import os
import sqlite3

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

CONFIG = "config/config.json"
MODEL = "models/isolation_forest.joblib"
SCALER = "models/scaler.joblib"

FEATURES = [
    "temperature_c",
    "humidity_pct",
    "vibration_g",
    "voltage_v",
    "current_a",
    "power_w"
]

def train(db_path, rows):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT ?", conn, params=(rows,))
    conn.close()
    df = df.dropna(subset=FEATURES)
    if len(df) < 20:
        raise RuntimeError("Collect at least 20 valid samples before training.")

    X = df[FEATURES].astype(float)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )
    model.fit(Xs)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL)
    joblib.dump(scaler, SCALER)

    df["anomaly"] = model.predict(Xs)
    df["anomaly_score"] = model.decision_function(Xs)
    df.to_csv("data/anomaly_results.csv", index=False)

    print(f"Model trained on {len(df)} samples.")
    print(f"Results saved to data/anomaly_results.csv")

def score(db_path):
    if not os.path.exists(MODEL):
        raise RuntimeError("Train the model first: python edge/anomaly_detector.py --train")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 1000", conn)
    conn.close()
    df = df.dropna(subset=FEATURES)

    model = joblib.load(MODEL)
    scaler = joblib.load(SCALER)
    Xs = scaler.transform(df[FEATURES].astype(float))

    df["anomaly"] = model.predict(Xs)
    df["anomaly_score"] = model.decision_function(Xs)
    df["status"] = df["anomaly"].map({1: "NORMAL", -1: "ANOMALY"})
    df.to_csv("data/anomaly_results.csv", index=False)

    print(df[["timestamp", "status", "anomaly_score"]].head(20).to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true")
    args = parser.parse_args()

    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if args.train:
        train(cfg["database"], cfg["anomaly"]["training_rows"])
    else:
        score(cfg["database"])
