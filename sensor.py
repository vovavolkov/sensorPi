#!/usr/bin/python

import argparse
import time
import random
import sqlite3
import signal
import board
from board import SCL, SDA, D4
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1305
import adafruit_scd4x

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dark', action='store_true', help="no display")
parser.add_argument('table', default="readings", nargs ='?', help='table for readings')
args = parser.parse_args()

print(args)

conn = sqlite3.connect('readings.db')
cursor = conn.cursor()
cursor.execute(f"CREATE TABLE IF NOT EXISTS {args.table}"
               "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
               "co2 INTEGER, temperature REAL, humidity REAL,"
               "time DATETIME DEFAULT CURRENT_TIMESTAMP)")

# try to initialise the sensor, catching errors
#try:
sensor_i2c = board.I2C()
scd4x  = adafruit_scd4x.SCD4X(sensor_i2c)
sensorOK = True
print("Sensor connected\nSerial number:", [hex(i) for i in scd4x.serial_number])

#except Exception:
#    sensorOK=False
#    print("Sensor not initialised")


# Define the Reset Pin for the display
oled_reset = digitalio.DigitalInOut(D4)

# Create the I2C interface for the OLED display.
disp_i2c = busio.I2C(SCL, SDA)

# Create the SSD1305 OLED class.
disp = adafruit_ssd1305.SSD1305_I2C(128, 32, disp_i2c, reset=oled_reset) 

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
    conn.close()
    disp.fill(0)
    disp.show()
    print("\nDisplay turned off, changes commited.")
    exit(0)

# Register the cleanup function to run when the script is terminated.
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

sensor_status = (lambda x: "Sensor OK" if x else "NO SENSOR, values random")(sensorOK)

#while True:
#    # clear the canvas
#    draw.rectangle((0, 0, width, height), outline=0, fill=0)
#    drawString(0, sensor_status)
#
#    co2 = int(random.gauss(1000,100))
#    drawString(8, "CO2: " + str(co2) + " ppm")
#
#    humidity = round(random.gauss(50, 13),2)
#    drawString(16, "Humidity: " + str(humidity) + " %")
#
#    temperature = round(random.gauss(15, 10),2)
#    drawString(25, "Temp: " + str(temperature) + " *C")
#    
#    # Display image.
#    disp.image(image)
#    disp.show()
#    time.sleep(2)

scd4x.start_periodic_measurement()

while True:
    if scd4x.data_ready:

        # fetch the values from the sensor
        co2 = scd4x.CO2
        temperature = round(scd4x.temperature, 4)
        humidity = round(scd4x.relative_humidity, 2)

        # write the values to the database
        cursor.execute(f"INSERT INTO {args.table}"
                       f"(co2, temperature, humidity)"
                       f"VALUES ({co2}, {temperature}, {humidity})")
        conn.commit() 

        # skip the display if the -d(ark) flag is set
        if args.dark:
            continue

        # print the values on the display 
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        drawString(0, sensor_status)

        drawString(8, f"CO2: {co2} ppm")

        drawString(16, f"Temp: {temperature} *C")

        drawString(25, f"Hum: {humidity} %")

        disp.image(image)
        disp.show()

    time.sleep(1)
