from smbus2 import SMBus

BUS = 1

with SMBus(BUS) as bus:
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.write_quick(addr)
            found.append(hex(addr))
        except OSError:
            pass

print("Detected I2C addresses:", found)
print("Expected for the recommended setup: 0x40, 0x68, 0x76")
