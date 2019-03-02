from __main__ import *
import io
import os
import logging
import sys
import ConfigParser
import time
import dispres
from PIL import Image, ImageFont


# Open configuration file
with open("/home/pi/dashcam/config.ini") as f:
   cfgfile = f.read()
cfg = ConfigParser.RawConfigParser(allow_no_value=False)
cfg.readfp(io.BytesIO(cfgfile))

# Open log file and set up logging
logger = logging.getLogger('dashcam')

# Clean up old log files if they exist
try:
   os.remove(str(cfg.get('Debugging', 'Logfile')))
except OSError:
   pass

# Begin logger
logfile = logging.FileHandler(str(cfg.get('Debugging', 'Logfile')))
logfmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logfile.setFormatter(logfmt)
logger.addHandler(logfile)
logger.setLevel(logging.INFO)

# Parse the configuration file
# Camera settings
VIDEO_HEIGHT = int(cfg.get('Camera', 'Height'))
VIDEO_WIDTH = int(cfg.get('Camera', 'Width'))
VIDEO_FPS = int(cfg.get('Camera', 'Framerate'))
VIDEO_BITRATE = int(cfg.get('Camera', 'Bitrate'))
VIDEO_INTERVAL = int(cfg.get('Camera', 'Interval'))
recPath = str(cfg.get('Camera', 'Path'))

# Display settings
canvasHeight = int(cfg.get('HUD', 'CanvasHeight'))
canvasOpacity = int(cfg.get('HUD', 'Opacity'))
dispHeight = dispres.yres # Get vertical resolution from HDMI fb
dispWidth = dispres.xres # Get horizontal resolution from HDMI fb
fontSpcY = int(cfg.get('Font', 'FontSpacing'))
fontSpcX = int(cfg.get('Font', 'FontStartingPos'))
posRelBtm = dispHeight - canvasHeight
dtfilestamp = time.strftime('%Y%m%d-%H%M')

# Other parameters
fontSize = int(cfg.get('Font', 'FontSize'))
refreshInterval = float(cfg.get('HUD', 'RefreshInterval')) # Seconds
baseDir = str(cfg.get('Camera', 'Path')) # directory where the video will be recorded
isCustomary = cfg.getboolean('HUD', 'Customary')
disableOutput = cfg.getboolean('Debugging', 'DisableOutput')

# Boolean values for enabling/disabling sensors and GPS devices
isAccelEnabled = cfg.getboolean('Sensors/Peripherals', 'mpu6050Enabled')
isAlsEnabled = cfg.getboolean('Sensors/Peripherals', 'apds9960Enabled')
isBme280Enabled = cfg.getboolean('Sensors/Peripherals', 'bme280Enabled')
isGpsEnabled = cfg.getboolean('Sensors/Peripherals', 'gpsEnabled')
isTftEnabled = cfg.getboolean('Sensors/Peripherals', 'SPITFT')

# Set initial variables for GPS receiver and sensors
gpsd = None
initialLatitude = initialLongitude = 0
initialStartupTime = ""
timeActive = distanceTraveled = 0
spd = alt = traveled = 0.0
alsval = temp = hum = prs = 0
xVal = yVal = zVal = 0
tempUnit = "*C"
distUnit = "m"
spdUnit = "KPH"

# Set initial variables for recording counter
secondsRecorded = 0
isCameraRecording = False
