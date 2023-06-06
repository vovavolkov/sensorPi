#!/usr/bin/python

import time
import random
import subprocess
import signal
from board import SCL, SDA, D4
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1305
import adafruit_scd4x

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(D4)
                                                                    
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
 
# Create the SSD1305 OLED class.
disp = adafruit_ssd1305.SSD1305_I2C(128, 32, i2c, reset=oled_reset) 

# try to initialise the sensor, catching errors
try:
    i2c = board.I2C()
    sensor = adafruit_scd4x.SCD4X(i2c)
    sensorOK = True

except Exception:
    sensorOK=False
    print("Sensor not initialised")

# Clear display
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the canvas for draw method.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
# font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('Minecraftia-Regular.ttf', 8)

def drawString(offset, text):
    draw.text((0, top+offset), text, font=font, fill=255)

def cleanup(signal, frame):
    # clear switch off display before exiting.
    disp.fill(0)
    disp.show()
    print("Display turned off.")
    exit(0)

# Register the cleanup function to run when the script is terminated.
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

sensor_status = (lambda x: "Sensor OK" if x else "NO SENSOR, values random")(sensorOK)

while True:
    # clear the canvas
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    drawString(0, sensor_status)

    co2 = int(random.gauss(1000,100))
    drawString(8, "CO2: " + str(co2) + " ppm")

    humidity = round(random.gauss(50, 13),2)
    drawString(16, "Humidity: " + str(humidity) + " %")

    temperature = round(random.gauss(15, 10),2)
    drawString(25, "Temp: " + str(temperature) + " *C")
    
    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(2)

#while True:
#    # Draw a black filled box to clear the image.
#    draw.rectangle((0, 0, width, height), outline=0, fill=0)
#
#    cmd = "iwgetid -r"
#    try:
#        SSID = subprocess.check_output(cmd, shell=True, timeout=5).decode("utf-8").strip()
#    except subprocess.CalledProcessError:
#        SSID = "Not connected"
#    except subprocess.TimeoutExpired:
#        SSID = "Timeout"
#
#    # Shell scripts for system monitoring from here:
#    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
#
#    # cmd = "hostname -I | cut -d' ' -f1"
#    # IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
#
#    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
#    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
#
#    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
#    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
#
#    # cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
#    # Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
#
#    current_time = time.strftime("%H:%M:%S")
#
#    # Write four lines of text.
#
#    draw.text((x, top + 0), "SSID: " + SSID, font=font, fill=255)
#    draw.text((x, top + 8), "Time: " + current_time, font=font, fill=255)
#    # draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
#    draw.text((x, top + 16), CPU, font=font, fill=255)
#    draw.text((x, top + 25), MemUsage, font=font, fill=255)
#    # draw.text((x, top + 25), Disk, font=font, fill=255)
#
#    # Display image.
#    disp.image(image)
#    disp.show()
#    time.sleep(0.1)
