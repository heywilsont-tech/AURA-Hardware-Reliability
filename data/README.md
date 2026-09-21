[README.md](https://github.com/user-attachments/files/32473897/README.md)
The repository does not include generated telemetry by default.

Run:

```bash
python edge/collector.py --simulate --samples 300
python edge/anomaly_detector.py --train
```

This creates local telemetry and anomaly-result files that are ignored by Git.
