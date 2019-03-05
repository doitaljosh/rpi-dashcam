# -*- coding: utf-8 -*-
import picamera
import time
import datetime
import numpy as np
import string
import random
import os
import sys
import io
from params import *
from initSensors import *
from gps import *
from gpsreceiver import *
import subprocess
import threading
from PIL import Image, ImageDraw, ImageFont

# global gpsp

# Create empty canvas layers to store text overlays
txtCanvas = Image.new("RGB", (dispWidth, canvasHeight))
drawTxt = txtCanvas.load()

# Use the Gotham Medium font
font = ImageFont.truetype("/home/pi/dashcam/fonts/GothamMedium.ttf", fontSize)

# Load kernel module for SPI LCD
if isTftEnabled:
   fbtftModPath = "/sys/module/fbtft_device"
   if not os.path.isdir(fbtftModPath):
      os.system('modprobe fbtft_device')
      logger.info('Loaded fbtft module')

if disableOutput:
   sys.stdout = os.devnull
   sys.stderr = os.devnull

# os.system('clear')

# Create the GPS polling thread
GpsPoller()

# Initialize camera
with picamera.PiCamera() as camera:
   camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
   logger.info('Opening video instance with dimensions: ' + str(VIDEO_WIDTH) + "x" + str(VIDEO_HEIGHT) + "p-" + str(VIDEO_FPS))
   camera.framerate = VIDEO_FPS
   camera.led = cfg.getboolean('Camera', 'EnableLED')
   if not cfg.getboolean('Camera', 'EnableLED'):
      logger.info('Camera LED disabled')

   logger.info('Opening preview instance')
   camera.start_preview()

   time.sleep(0.5)

   if isGpsEnabled:
      gpsp = GpsPoller()

   # Start recording
   if isRecordEnabled:
      camera.start_recording(recPath + '/VID_' + dtfilestamp + '.h264', bitrate=VIDEO_BITRATE)
      isCameraRecording = True
      logger.info('Started recording')

   # Enable the light sensor
   if isAlsEnabled:
      als.enableLightSensor()
      logger.info('Light sensor initialized')

   # Set up constraints for text overlays on canvases
   topTxtBg = txtCanvas.copy()
   btmTxtBg = txtCanvas.copy()

   # Attach overlays
   topOverlay = camera.add_overlay(topTxtBg.tobytes(), format='rgb', size=(dispWidth,canvasHeight), layer=5, alpha=canvasOpacity, fullscreen=False, window=(0,0,dispWidth,canvasHeight))
   btmOverlay = camera.add_overlay(btmTxtBg.tobytes(), format='rgb', size=(dispWidth,canvasHeight), layer=4, alpha=canvasOpacity, fullscreen=False, window=(0,posRelBtm,dispWidth,canvasHeight))

   try:
      if isGpsEnabled:
         gpsp.start() # start receiving data from GPS radio
         logger.info('Started monitoring GPS')

      while True:
          if isCameraRecording == False:
            timeActive = "Off"

          if isBme280Enabled:
             bme280.sample(i2cbus, bme280Addr, bme280Cal)
             if isCustomary:
                temp = bme280Read.temperature * (9/5) + 32
                tempUnit = "*F"
             else:
                temp = bme280Read.temperature
             hum = bme280Read.humidity
             prs = bme280Read.pressure

          if isAccelEnabled:
             accelData = accelDev.get_accel_data()
             xVal = accelData['x']
             yVal = accelData['y']
             zVal = accelData['z']

          if isGpsEnabled:
             readLoc()
             gpsd = gps(mode=1)
             distanceTraveled = distance((initialLatitude, initialLongitude), (gpsd.fix.latitude, gpsd.fix.longitude))
             lat = gpsd.fix.latitude
             lon = gpsd.fix.longitude
             sats = len(gpsd.satellites)
             if isCustomary:
                spd = gpsd.fix.speed / 1.609
                alt = gpsd.fix.altitude * 3.281
                traveled = distanceTraveled * 3.281
                spdUnit = "MPH"
                distUnit = "ft"
             else:
                spd = gpsd.fix.speed
                alt = gpsd.fix.altitude
                traveled = distanceTraveled
                spdUnit = "KPH"
                distUnit = "m"

          # Draw canvas layers
          topTxtBg = txtCanvas.copy()
          btmTxtBg = txtCanvas.copy()

          time.sleep(0.2)

          # Draw text onto canvas layers
          topText = "{0:.0f} {9}  Sats: {1} T: {3:.1f} {10} H: {7:.1f} % P: {8:.1f} mbar  Acc: X:{3:.2f},Y:{4:.2f},Z:{5:.2f} ALS: {6:.1f} lux".format(spd, sats, temp, xVal, yVal, zVal, alsval, hum, prs, spdUnit, tempUnit)
          drawTopOverlay = ImageDraw.Draw(topTxtBg)
          drawTopOverlay.text((fontSpcX, fontSpcY), topText, font=font, fill=(255, 255, 255), align="center")
          topOverlay.update(topTxtBg.tobytes())

          btmText = "Altitude: {0:.2f} {6}   Lat: {1:.5f}    Lon: {2:.5f}    Home: {3:.2f} {6}     Rec: {4}    {5}".format(alt, lat, lon, traveled, timeActive, str(time.strftime('%m/%d/%Y %H:%M:%S')), distUnit)
          drawBtmOverlay = ImageDraw.Draw(btmTxtBg)
          drawBtmOverlay.text((fontSpcX, fontSpcY), btmText, font=font, fill=(255, 255, 255))
          btmOverlay.update(btmTxtBg.tobytes())

          secondsRecorded = secondsRecorded + 1

          if isCameraRecording == True:
            camera.wait_recording(refreshInterval)

            if secondsRecorded > VIDEO_INTERVAL:
              camera.stop_recording()
              isCameraRecording = False

          else:
            time.sleep(refreshInterval)

   except KeyboardInterrupt:
      if isGpsEnabled:
         gpsp.running = False
         logger.info('Stopping GPS thread')
         gpsp.join()
      camera.remove_overlay(topOverlay)
      camera.remove_overlay(btmOverlay)
      if isCameraRecording:
        camera.stop_recording()
        logger.info('Stopped recording')
      logger.info('Exit')

   finally:
      if isGpsEnabled:
         gpsp.running = False
         logger.info('Stopping GPS thread')
         gpsp.join()
      camera.remove_overlay(topOverlay)
      camera.remove_overlay(btmOverlay)
      if isCameraRecording:
        camera.stop_recording()
        logger.info('Stopped recording')
      logger.info('Exit')
