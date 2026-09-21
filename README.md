[AURA_README.md](https://github.com/user-attachments/files/32474060/AURA_README.md)
# AURA — Autonomous Unified Reliability Architecture

> Edge-AI predictive hardware health monitoring and anomaly detection platform built around a Raspberry Pi 3 Model B+.

## Overview

**AURA (Autonomous Unified Reliability Architecture)** is an edge-computing prototype designed to monitor hardware health using multiple physical signals and identify abnormal operating conditions.

The system combines environmental, vibration, and electrical telemetry to create a unified view of device health. Telemetry is collected locally at the edge, stored for analysis, and processed using an unsupervised anomaly-detection model.

The project was developed as a hardware reliability and predictive-maintenance concept for the **Cisco NextGen System League**.

---

## Problem Statement

Hardware failures are often preceded by changes in measurable operating conditions such as:

- Increasing temperature
- Unusual vibration
- Voltage instability
- Abnormal current consumption
- Changes in environmental conditions

Traditional threshold-only monitoring can miss relationships between multiple signals.

AURA addresses this by combining several hardware-health signals and applying anomaly detection to identify operating conditions that differ from the learned baseline.

---

## System Architecture

```text
                 ┌─────────────────────┐
                 │   Physical System   │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        ┌────▼────┐   ┌─────▼────┐   ┌─────▼────┐
        │ BME280  │   │ MPU6050  │   │  INA219  │
        │Temp/Hum │   │Vibration │   │V/I/Power │
        └────┬────┘   └─────┬────┘   └─────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │ I²C
                     ┌──────▼──────┐
                     │ Raspberry Pi│
                     │   3 Model B+│
                     └──────┬──────┘
                            │
                  ┌─────────▼─────────┐
                  │ Telemetry Collector│
                  └─────────┬─────────┘
                            │
                     ┌──────▼──────┐
                     │    SQLite   │
                     └──────┬──────┘
                            │
                ┌───────────▼───────────┐
                │ Isolation Forest      │
                │ Anomaly Detection     │
                └───────────┬───────────┘
                            │
                     ┌──────▼──────┐
                     │  Dashboard   │
                     │ Streamlit    │
                     └──────────────┘
```

---

## Hardware

| Component | Purpose |
|---|---|
| Raspberry Pi 3 Model B+ | Edge computing and telemetry processing |
| BME280 | Temperature and humidity monitoring |
| MPU6050 | Acceleration and vibration monitoring |
| INA219 | Voltage, current and power monitoring |

### Why these sensors?

The three sensors provide complementary hardware-health signals:

- **BME280** → thermal/environmental conditions
- **MPU6050** → mechanical vibration and movement
- **INA219** → electrical operating conditions

Combining these signals makes the project more useful for hardware-health analysis than monitoring a single parameter.

---

## Software Stack

- **Python 3**
- **Raspberry Pi OS / Linux**
- **I²C**
- **SQLite**
- **NumPy**
- **Pandas**
- **scikit-learn**
- **Isolation Forest**
- **Streamlit**
- **Plotly**
- **smbus2**

---

## Key Features

### 1. Multi-Sensor Telemetry

The Raspberry Pi collects:

- Temperature
- Humidity
- Vibration
- Voltage
- Current
- Power

Telemetry is timestamped and stored locally.

### 2. Edge Data Processing

Instead of depending on a remote server for initial analysis, telemetry can be collected and processed directly on the Raspberry Pi.

### 3. Anomaly Detection

AURA uses **Isolation Forest**, an unsupervised machine-learning algorithm, to identify observations that differ from the normal operating baseline.

The model produces:

- Normal operating observations
- Potential anomalies
- Anomaly scores

### 4. Diagnostic Data Storage

Telemetry is stored in an SQLite database, making it possible to inspect historical operating conditions and analyze changes over time.

### 5. Hardware Health Dashboard

A Streamlit dashboard provides visualizations for:

- Temperature
- Humidity
- Vibration
- Voltage
- Current
- Power

---

## Repository Structure

```text
AURA-Hardware-Reliability/
│
├── config/
│   └── config.json
│
├── dashboard/
│   └── app.py
│
├── data/
│   └── README.md
│
├── docs/
│   ├── testing.md
│   └── wiring.md
│
├── edge/
│   ├── anomaly_detector.py
│   └── collector.py
│
├── hardware/
│   └── sensors.py
│
├── scripts/
│   └── check_i2c.py
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/heywilson-tech/AURA-Hardware-Reliability.git
cd AURA-Hardware-Reliability
```

Replace the repository URL above with your actual GitHub URL if your username/repository differs.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Enable I²C on Raspberry Pi

Run:

```bash
sudo raspi-config
```

Then:

```text
Interface Options
    → I2C
        → Enable
```

Restart if required.

Check the connected devices:

```bash
python scripts/check_i2c.py
```

Expected addresses for the recommended configuration:

```text
0x40 → INA219
0x68 → MPU6050
0x76 → BME280
```

Actual addresses can vary depending on the breakout-board configuration.

---

## Wiring

The recommended sensors communicate using I²C.

| Raspberry Pi | Function |
|---|---|
| Pin 1 | 3.3V |
| Pin 3 | SDA / GPIO2 |
| Pin 5 | SCL / GPIO3 |
| Pin 6 | GND |

See [`docs/wiring.md`](docs/wiring.md) for the wiring reference.

> Always verify the voltage requirements of the specific sensor breakout boards before connecting them to the Raspberry Pi.

---

## Running the Telemetry Collector

### Hardware mode

With the sensors connected:

```bash
python edge/collector.py
```

The collector continuously reads sensor values and stores telemetry in:

```text
data/telemetry.db
```

### Simulation mode

The repository also includes simulation mode for development without physical hardware:

```bash
python edge/collector.py --simulate --samples 300
```

This generates sample telemetry for testing the software pipeline.

---

## Training the Anomaly Detection Model

After collecting sufficient telemetry:

```bash
python edge/anomaly_detector.py --train
```

The Isolation Forest model is trained on the collected baseline data.

Generated model files are intentionally excluded from Git using `.gitignore`.

---

## Running Anomaly Detection

After training:

```bash
python edge/anomaly_detector.py
```

The program evaluates recent telemetry and reports:

```text
NORMAL
ANOMALY
```

along with an anomaly score.

---

## Running the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard displays recent hardware telemetry and helps visualize changes in operating conditions.

---

## Validation Strategy

AURA can be validated using controlled test scenarios.

### Normal baseline

Collect telemetry while the hardware operates under stable conditions.

### Thermal variation

Safely change the surrounding temperature and observe the temperature telemetry.

### Vibration variation

Introduce controlled vibration within the sensor and hardware operating limits.

### Electrical variation

Use an appropriate current-limited test setup to observe changes in voltage/current/power.

### Sensor failure

Disconnect or disable a sensor and verify that the software handles missing or invalid readings appropriately.

### Anomaly detection

Train the model using baseline data and evaluate whether intentionally unusual operating conditions are identified as anomalies.

Detailed validation guidance is available in [`docs/testing.md`](docs/testing.md).

---

## Engineering Concepts Demonstrated

This project demonstrates practical experience in:

- Embedded hardware monitoring
- Raspberry Pi edge computing
- I²C communication
- Sensor interfacing
- Real-time telemetry collection
- Diagnostic data logging
- Hardware health monitoring
- Anomaly detection
- Time-series data analysis
- Hardware validation
- Fault investigation
- Predictive-maintenance concepts
- Hardware/software integration

---

## Relevance to Hardware Reliability Engineering

AURA follows a simplified hardware-reliability workflow:

```text
Hardware Health Signals
        ↓
Telemetry Collection
        ↓
Diagnostic Data
        ↓
Baseline Modeling
        ↓
Anomaly Detection
        ↓
Failure Pattern Investigation
        ↓
Validation / Corrective Action
```

This workflow is applicable to systems where engineers need to monitor hardware health, investigate abnormal behavior, and identify potential failure conditions.

---

## Limitations

AURA is a prototype and is not a production infrastructure-monitoring system.

The current repository focuses on:

- Local edge telemetry
- Sensor-level health monitoring
- SQLite-based storage
- Isolation Forest anomaly detection
- Visualization

It does **not** claim production deployment across cloud/server fleets or direct integration with Azure infrastructure.

---

## Future Improvements

Potential extensions include:

- LSTM-based time-series prediction
- TensorFlow Lite edge inference
- MQTT-based distributed telemetry
- Multiple Raspberry Pi monitoring nodes
- Centralized telemetry aggregation
- Automated fault classification
- Remaining-useful-life estimation
- Alert notifications
- Hardware fault-injection framework
- Secure device identity and communication
- Cloud-based fleet monitoring

---

## Project Context

**Project:** AURA — Autonomous Unified Reliability Architecture  
**Competition:** Cisco NextGen System League  
**Domain:** Edge AI / Hardware Reliability / Predictive Monitoring  
**Platform:** Raspberry Pi 3 Model B+

---

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE).
