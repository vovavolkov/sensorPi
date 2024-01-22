import time
import threading

import adafruit_scd4x
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_ssd1305 import SSD1305_I2C
from board import SCL, SDA, D4
from busio import I2C
from digitalio import DigitalInOut

from sensorPi.db import insert_readings

table = "readings"
dark = False

global display, image, draw, font


# initialise the display
def init_display():
    global display, image, draw, font
    # Define the Reset Pin for the display
    oled_reset = DigitalInOut(D4)
    # Create the I2C interface for the display
    disp_i2c = I2C(SCL, SDA)
    # Create the SSD1305 display class.
    display = SSD1305_I2C(128, 32, disp_i2c, reset=oled_reset)

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
    font = ImageFont.truetype('sensorPi/static/Minecraftia-Regular.ttf', 8)


def init_sensor():
    try:
        sensor_i2c = board.I2C()
        scd4x = adafruit_scd4x.SCD4X(sensor_i2c)
        print("Sensor connected\nSerial number:", [hex(i) for i in scd4x.serial_number])
        return scd4x
    except Exception():
        print("Sensor not found")
        return None


# Function switches value of args.dark, i.e. switches the display on/off
# def toggle_display(signal, frame):
#     global dark
#     dark = not dark
#
#     print("Display is now:", "OFF" if dark else "ON")
#     display.fill(0)
#     display.show()


# Display toggle is triggered by kill -USR1 signal.
# signal(SIGUSR1, toggle_display)


# Cleanup function - fills display with black, i.e. switches it off

def cleanup():
    display.fill(0)
    display.show()
    print("\nDisplay turned off, changes committed.")
    exit(0)


# # Register the cleanup function to run when the script is terminated
# signal(SIGINT, cleanup)
# signal(SIGTERM, cleanup)

# Load a .ttf font


# Define a function to print out a string with a pixel offset from top left
def display_strings(strings):
    # Draw a black filled box to clear the canvas for draw method
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
    for i, string in enumerate(strings):
        draw.text((0, -2 + 8 * i), string, font=font, fill=255)
    display.image(image)
    display.show()


def start_measuring(db):
    init_display()
    sensor = init_sensor()
    if sensor is None:
        display_strings(["Sensor not found"])
        return None

    # Launch the sensor's periodic measurement
    sensor.start_periodic_measurement()

    while True:
        if sensor.data_ready:
            # Fetch the readings from the sensor
            co2 = sensor.CO2
            temperature = round(sensor.temperature, 4)
            humidity = round(sensor.relative_humidity, 2)

            # Insert the new values into the table
            insert_readings(co2, temperature, humidity, db)

            # Skip the display if the -d(ark) flag is set
            if not dark:
                display_strings([
                        "Sensor OK",
                        f"CO2: {co2} ppm",
                        f"Temp: {temperature} *C",
                        f"Hum: {humidity} %"
                    ]
                )
        # Wait for 1 second before repeating
        time.sleep(1)


def init_app(app):
    app.teardown_appcontext(cleanup)
