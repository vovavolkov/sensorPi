import argparse
import datetime
import random
import sqlite3

# Define available command line arguments and fetch them
parser = argparse.ArgumentParser()
parser.add_argument(
    "table", default="readings",
    nargs="?", help="table for readings")
args = parser.parse_args()
print(args)

# Connect to the database 'readings.db'
connector = sqlite3.connect("db/readings.db")
cursor = connector.cursor()
# Create a table specified in command arguments, if it doesn't exist
cursor.execute(
    f"CREATE TABLE IF NOT EXISTS {args.table}"
    "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "co2 INTEGER, temperature REAL, humidity REAL,"
    "time DATETIME DEFAULT CURRENT_TIMESTAMP)")

# Ask the user for amount of test entries
print("how many entries?")
n = int(input())

# Get current timestamp
date = datetime.datetime.now()

# Generate n readings
for i in range(n):
    # Create pseudo readings, use normal distribution
    co2 = int(random.gauss(1000, 100))
    humidity = round(random.gauss(50, 13), 2)
    temperature = round(random.gauss(15, 10), 2)

    # Add 5 seconds to the timestamp to emulate real frequency of data collection
    date = date + datetime.timedelta(seconds=5)
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")

    # Insert the new values into the table
    cursor.execute(
        f"INSERT INTO {args.table}"
        "(co2, temperature, humidity, time)"
        f"VALUES ({co2}, {temperature}, {humidity}, '{date_str}')"
    )

connector.commit()
connector.close()
