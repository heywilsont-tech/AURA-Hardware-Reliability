[Uploading testing.md…]()
# Validation Plan

AURA should be validated using controlled test conditions.

## Test 1 — Normal operation
Collect a baseline dataset under stable temperature, vibration and electrical conditions.

## Test 2 — Thermal change
Safely increase ambient temperature and verify the telemetry trend changes.

## Test 3 — Vibration
Introduce controlled vibration without exceeding sensor or hardware limits.

## Test 4 — Electrical change
Use an appropriate safe test setup to change the monitored load/voltage.

## Test 5 — Sensor disconnect
Disconnect one sensor and verify the software reports the communication/data failure instead of silently treating it as normal.

## Test 6 — Anomaly model
Train Isolation Forest on baseline data and evaluate whether deliberately unusual samples are flagged.

Do not perform unsafe electrical experiments. Use current-limited supplies and stay within the ratings of every component.
