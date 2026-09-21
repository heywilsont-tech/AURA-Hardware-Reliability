[wiring.md](https://github.com/user-attachments/files/32473877/wiring.md)
# Recommended I2C Wiring

All three recommended sensors use I2C.

## Raspberry Pi 3B+

| Signal | Raspberry Pi |
|---|---|
| 3.3V | Pin 1 |
| GND | Pin 6 |
| SDA | GPIO2 / Pin 3 |
| SCL | GPIO3 / Pin 5 |

## Devices

- BME280: address `0x76`
- MPU6050: address `0x68`
- INA219: address `0x40`

Run:

```bash
python scripts/check_i2c.py
```

before starting the collector.

**Power note:** use sensor breakout boards compatible with Raspberry Pi 3.3V logic. Verify the breakout's voltage requirements before wiring.
