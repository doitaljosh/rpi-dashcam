# Raspberry Pi Dashcam Proof of Concept

### This is a very initial proof of concept with many bugs that need to be worked out and optimized.

## Features:
- Camera streaming from Rapsberry Pi camera
- HUD with live sensor and GPS data (temp, humidity, pressure, accelerometer, etc.)
- Speedometer and trip counter
- Configurable measuring units, HUD, and camera settings

## To do:
- Add accelerometer motion detection trigger for recording
- Implement GPS auto-updating of time
- Include overlay in recorded video
- Auto convert raw H264 to mp4
- Implement a HAL for compatibility with more sensors
- Reverse camera function with lane markers
- CAN bus monitoring support
- Touch GUI for interaction
- Much more

## Install Dependencies:
```
sudo apt install python python-pil python-pip gpsd gpsd-clients

pip install mpu6050-raspberrypi python-apds9960 bme280 gps numpy picamera configparser
```

## Make sure the following are configured in raspi-config:
- camera
- i2c
- spi
- serial with no terminal access
- At least 200MB of VMEM

## Note on sensors and GPS:
### Sensors are disabled by default. Currently supported sensors are:
- BME280 (i2c Temp, Humidity and Pressure)
- APDS9960 (i2c RGBW light, gesture, proximity sensor)
- MPU6050 (i2c 6-axis gyroscope, accelerometer)

Additional sensors can be added by adapting to the new libraries and their calling methods.
To enable sensors, change the ```False``` values in ```config.ini``` under ```Sensors/Peripherals``` to ```True```.

##### Any UART GPS receiver should work, preferably UBlox devices.

### Copy the ```gpsd``` file to ```/etc/default/``` to configure gpsd.

## Run:
```python main.py```
