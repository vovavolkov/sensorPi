# sensorPi

A self-hosted indoor air-quality monitor for the Raspberry Pi, built as my OCR A-Level Computer Science project.

It reads CO2, temperature and humidity from a Sensirion SCD4x sensor over I2C, shows the latest values on a small OLED display, logs every reading to SQLite, and serves a Flask web dashboard with daily graphs.

## Features

- **Hardware:** SCD4x CO2/temperature/humidity sensor and a 128x32 SSD1305 OLED display, both on the Pi's I2C bus (Adafruit CircuitPython libraries).
- **Background logging:** a background thread polls the sensor every second, validates each reading (CO2 400-2000 ppm, humidity 0-100%) and stores valid readings with a timestamp in SQLite, discarding invalid ones.
- **Web dashboard:** Flask app with a graph page per day (CO2, temperature and humidity plotted with matplotlib), standard deviation for each measurement, and previous/next day navigation.
- **Admin area:** login with hashed passwords, adding users, changing passwords and downloading all readings as CSV.

## Running it

On a Raspberry Pi with I2C enabled and the sensor and display connected:

```sh
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
flask --app sensorPi init-db   # creates the database and an admin:admin user (change the password on first login)
flask --app sensorPi run --host 0.0.0.0
```

The hardware thread only starts when Flask is not in debug mode, so the web app can be developed on a machine without the sensor.

## Project structure

- `sensorPi/hardware.py`: sensor and display handling, measurement loop
- `sensorPi/db.py`: SQLite connection, schema setup and inserts
- `sensorPi/graphs.py`: dashboard, graphs, admin page and CSV export
- `sensorPi/auth.py`: login, users and passwords
- `sensorPi/schema.sql`: database schema
