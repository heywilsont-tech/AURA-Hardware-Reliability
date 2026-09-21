import argparse
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

from hardware.sensors import RealSensors, SimulatedSensors

CONFIG = "config/config.json"

def load_config():
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)

def init_db(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            timestamp TEXT,
            temperature_c REAL,
            humidity_pct REAL,
            pressure_hpa REAL,
            vibration_g REAL,
            voltage_v REAL,
            current_a REAL,
            power_w REAL
        )
    ''')
    conn.commit()
    return conn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--samples", type=int, default=0, help="0 = run continuously")
    args = parser.parse_args()

    cfg = load_config()
    conn = init_db(cfg["database"])
    sensors = SimulatedSensors() if args.simulate else RealSensors(cfg["i2c_bus"])

    try:
        count = 0
        while args.samples == 0 or count < args.samples:
            x = sensors.read()
            ts = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT INTO telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, x["temperature_c"], x["humidity_pct"], x["pressure_hpa"],
                 x["vibration_g"], x["voltage_v"], x["current_a"], x["power_w"])
            )
            conn.commit()
            print(ts, x)
            count += 1
            time.sleep(cfg["sampling_interval_seconds"])
    except KeyboardInterrupt:
        print("\nCollector stopped.")
    finally:
        if hasattr(sensors, "close"):
            sensors.close()
        conn.close()

if __name__ == "__main__":
    main()
