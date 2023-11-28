#!/usr/bin/python

import argparse
import signal
import sqlite3
import time

import adafruit_scd4x
import adafruit_ssd1305
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA, D4

# Define available command line arguments and fetch them
parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--dark',
    action='store_true', help="no display")
parser.add_argument(
    "table", default="readings",
    nargs="?", help="table for readings")
args = parser.parse_args()
print(args)

# Connect to the database 'readings.db'
connector = sqlite3.connect('db/readings.db')
cursor = connector.cursor()
# Create a table specified in command arguments, if it doesn't exist
cursor.execute(
    f"CREATE TABLE IF NOT EXISTS {args.table}"
    "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "co2 INTEGER, temperature REAL, humidity REAL,"
    "time DATETIME DEFAULT CURRENT_TIMESTAMP)")

# Define the Reset Pin for the display
oled_reset = digitalio.DigitalInOut(D4)

# Create the I2C interface for the display
disp_i2c = busio.I2C(SCL, SDA)

# Create the SSD1305 display class.
display = adafruit_ssd1305.SSD1305_I2C(128, 32, disp_i2c, reset=oled_reset)

# Clear display
display.fill(0)
display.show()

# Create blank image for drawing
# Create image with mode '1' for 1-bit color
width = display.width
height = display.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)


# Draw a black filled box to clear the canvas for draw method
def clear_canvas():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)


# Load a .ttf font
font = ImageFont.truetype('assets/Minecraftia-Regular.ttf', 8)


# Define a function to print out a string with a pixel offset from top
def draw_string(offset, text):
    draw.text((0, -2 + offset), text, font=font, fill=255)


# try to initialise the sensor, catching errors
try:
    sensor_i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(sensor_i2c)
    sensorOK = True
    print("Sensor connected\nSerial number:", [hex(i) for i in scd4x.serial_number])

except Exception:
    sensorOK = False
    print("Sensor not found")
    if not args.dark:
        clear_canvas()
        draw_string(0, "Sensor not found")
        display.image(image)
        display.show()
    exit(1)


# Cleanup function - fills display with black, i.e. switches it off
def cleanup(signal, frame):
    connector.close()
    display.fill(0)
    display.show()
    print("\nDisplay turned off, changes committed.")
    exit(0)


# Register the cleanup function to run when the script is terminated
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


# Function switches value of args.dark, i.e. switches the display on/off
def toggle_display(signal, frame):
    args.dark = not args.dark
    print("Display is now:", "OFF" if args.dark else "ON")
    display.fill(0)
    display.show()


# Display toggle is triggered by kill -USR1 signal.
signal.signal(signal.SIGUSR1, toggle_display)

scd4x.start_periodic_measurement()

while True:
    if scd4x.data_ready:
        # Fetch the readings from the sensor
        co2 = scd4x.CO2
        temperature = round(scd4x.temperature, 4)
        humidity = round(scd4x.relative_humidity, 2)

        # Insert the new values into the table
        try:
            cursor.execute(
                f"INSERT INTO {args.table}"
                "(co2, temperature, humidity)"
                f"VALUES ({co2}, {temperature}, {humidity})")
        except Exception as e:
            print(e)

        # Skip the display if the -d(ark) flag is set
        if args.dark:
            continue
            
        clear_canvas()
        # Add text strings to the canvas
        draw_string(0, "Sensor OK")
        draw_string(8, f"CO2: {co2} ppm")
        draw_string(16, f"Temp: {temperature} *C")
        draw_string(25, f"Hum: {humidity} %")

        # Push the canvas onto the display
        display.image(image)
        display.show()

    # Wait for 1 second before repeating
    time.sleep(1)
