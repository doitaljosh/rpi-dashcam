import math
import datetime
import threading
from gps import *
from params import *

# Create the GPS polling thread

class GpsPoller(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      global gpsd
      gpsd = gps(mode=1)
      self.current_value = None
      self.running = True

   def run(self):
      global gpsd
      if self.running:
         logger.info('GPS thread initialized')
      if not self.running:
         logger.error('GPS thread failed to start')
      while self.running:
         gpsd.next() # Continuously update the buffer

def make_time(gps_datetime_str):
    """Makes datetime object from string object"""
    if not 'n/a' == gps_datetime_str:
        datetime_string = gps_datetime_str
        datetime_object = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
        return datetime_object

def elapsed_time_from(start_time, now_time):
    """calculate time delta from latched time and current time"""
    time_then = make_time(start_time)
    time_now = make_time(now_time)
    if time_then is None:
        return
    delta_t = time_now - time_then
    return delta_t

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def readLoc():
    global initialLatitude
    global initialLongitude
    global initialStartupTime

    if (isGpsEnabled and gpsd.fix.latitude != "n/a" and initialLatitude == 0):
       initialLatitude = gpsd.fix.latitude

    if (isGpsEnabled and gpsd.fix.longitude != "n/a" and initialLongitude == 0):
       initialLongitude = gpsd.fix.longitude

    if (isGpsEnabled and gpsd.utc != "n/a" and initialStartupTime == "" and '-' in gpsd.utc):
       initialStartupTime = gpsd.utc.split('.')[0]

    if (isGpsEnabled and gpsd.utc != "n/a" and '-' in initialStartupTime and '-' in gpsd.utc):
       timeActive = elapsed_time_from(initialStartupTime, gpsd.utc.split('.')[0])
