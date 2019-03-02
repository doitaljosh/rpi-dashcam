import re

# Open framebuffer modes for reading
# Ensures that PIL elements are drawn correctly to scale
f = open('/sys/class/graphics/fb0/modes', 'r')
rawdata = f.read()

# Parse fb size from mode data and pass it as integers
xres = int(rawdata.split('U:')[-1].split('x')[0])
yres = int(rawdata.split('x')[-1].split('p')[0])
