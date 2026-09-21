import math
import random
import time
from smbus2 import SMBus

BME280_ADDR = 0x76
MPU6050_ADDR = 0x68
INA219_ADDR = 0x40

class SimulatedSensors:
    def __init__(self):
        self.t = 0

    def read(self):
        self.t += 1
        temp = 35 + 2 * math.sin(self.t / 20) + random.gauss(0, 0.25)
        humidity = 48 + 4 * math.sin(self.t / 30) + random.gauss(0, 0.7)
        vibration = 0.02 + abs(random.gauss(0, 0.012))
        voltage = 5.0 + random.gauss(0, 0.015)
        current = 0.35 + random.gauss(0, 0.025)
        return {
            "temperature_c": round(temp, 3),
            "humidity_pct": round(humidity, 3),
            "pressure_hpa": 1013.0 + random.gauss(0, 1.2),
            "vibration_g": round(vibration, 5),
            "voltage_v": round(voltage, 4),
            "current_a": round(current, 4),
            "power_w": round(voltage * current, 4)
        }

class RealSensors:
    # Register-level implementation for MPU6050 and INA219.
    # BME280 uses a compact calibration/data implementation below.
    def __init__(self, bus_no=1):
        self.bus = SMBus(bus_no)
        self._init_mpu()
        self._init_ina219()
        self._init_bme280()

    def _init_mpu(self):
        self.bus.write_byte_data(MPU6050_ADDR, 0x6B, 0x00)
        self.bus.write_byte_data(MPU6050_ADDR, 0x1C, 0x00)

    def _init_ina219(self):
        # 32V, 2A-ish configuration suitable for prototype monitoring.
        self.bus.write_i2c_block_data(INA219_ADDR, 0x00, [0x39, 0x9F])

    def _init_bme280(self):
        self.bus.write_byte_data(BME280_ADDR, 0xF2, 0x01)
        self.bus.write_byte_data(BME280_ADDR, 0xF4, 0x27)
        self.bus.write_byte_data(BME280_ADDR, 0xF5, 0xA0)

        self.dig_T1 = self.bus.read_word_data(BME280_ADDR, 0x88)
        self.dig_T2 = self._signed16(0x8A)
        self.dig_T3 = self._signed16(0x8C)
        self.dig_H1 = self.bus.read_byte_data(BME280_ADDR, 0xA1)
        self.dig_H2 = self._signed16(0xE1)
        self.dig_H3 = self.bus.read_byte_data(BME280_ADDR, 0xE3)
        e4 = self.bus.read_byte_data(BME280_ADDR, 0xE4)
        e5 = self.bus.read_byte_data(BME280_ADDR, 0xE5)
        e6 = self.bus.read_byte_data(BME280_ADDR, 0xE6)
        self.dig_H4 = (e4 << 4) | (e5 & 0x0F)
        if self.dig_H4 & 0x800:
            self.dig_H4 -= 4096
        self.dig_H5 = (e6 << 4) | (e5 >> 4)
        if self.dig_H5 & 0x800:
            self.dig_H5 -= 4096
        self.dig_H6 = self.bus.read_byte_data(BME280_ADDR, 0xE7)
        if self.dig_H6 & 0x80:
            self.dig_H6 -= 256

    def _signed16(self, reg):
        v = self.bus.read_word_data(BME280_ADDR, reg)
        v = ((v & 0xFF) << 8) | (v >> 8)
        return v - 65536 if v & 0x8000 else v

    def _bme_raw(self):
        d = self.bus.read_i2c_block_data(BME280_ADDR, 0xF7, 8)
        p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        h = (d[6] << 8) | d[7]
        return t, h

    def _temperature_humidity(self):
        adc_t, adc_h = self._bme_raw()
        var1 = (((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temp = (t_fine * 5 + 128) >> 8
        temp_c = temp / 100.0

        v_x1 = t_fine - 76800
        v_x1 = (((((adc_h << 14) - (self.dig_H4 << 20) -
                   (self.dig_H5 * v_x1)) + 16384) >> 15) *
                (((((((v_x1 * self.dig_H6) >> 10) *
                   (((v_x1 * self.dig_H3) >> 11) + 32768)) >> 10) +
                   2097152) * self.dig_H2 + 8192) >> 14))
        v_x1 -= (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * self.dig_H1) >> 4)
        v_x1 = max(0, min(v_x1, 419430400))
        humidity = v_x1 >> 12
        return temp_c, humidity / 1024.0

    def _mpu_accel(self):
        d = self.bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
        vals = []
        for i in range(0, 6, 2):
            raw = (d[i] << 8) | d[i+1]
            if raw & 0x8000:
                raw -= 65536
            vals.append(raw / 16384.0)
        ax, ay, az = vals
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        vibration = abs(magnitude - 1.0)
        return vibration

    def _ina219(self):
        # Bus voltage register: bits [15:3], 4mV/bit.
        bv = self.bus.read_i2c_block_data(INA219_ADDR, 0x02, 2)
        raw_v = ((bv[0] << 8) | bv[1]) >> 3
        voltage = raw_v * 0.004

        # Current register depends on calibration. This prototype uses
        # the configured calibration value and converts raw current to A.
        ci = self.bus.read_i2c_block_data(INA219_ADDR, 0x04, 2)
        raw_i = (ci[0] << 8) | ci[1]
        if raw_i & 0x8000:
            raw_i -= 65536
        current = raw_i * 0.001
        return voltage, current

    def read(self):
        temp, humidity = self._temperature_humidity()
        vibration = self._mpu_accel()
        voltage, current = self._ina219()
        return {
            "temperature_c": round(temp, 3),
            "humidity_pct": round(humidity, 3),
            "pressure_hpa": None,
            "vibration_g": round(vibration, 5),
            "voltage_v": round(voltage, 4),
            "current_a": round(current, 4),
            "power_w": round(voltage * current, 4)
        }

    def close(self):
        self.bus.close()
