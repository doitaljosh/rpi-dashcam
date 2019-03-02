from __main__ import *
import smbus2
from apds9960 import APDS9960
from apds9960.const import *
from mpu6050 import mpu6050
import bme280

# Initialize smbus library for i2c-1 (Raspberry Pi I2C)
i2cbus = smbus2.SMBus(1)
# Define sensor device i2c addresses
bme280Addr = 0x77
mpu6050Addr = 0x68
# Load calibration data for bme280 sensor
bme280Cal = bme280.load_calibration_params(i2cbus, bme280Addr)
# Initialize sensor devices
bme280Read = bme280.sample(i2cbus, bme280Addr, bme280Cal)
als = APDS9960(i2cbus)
accelDev = mpu6050(mpu6050Addr)

