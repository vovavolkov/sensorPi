import sqlite3
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('table', default="readings", nargs ='?', help='table for readings')
args = parser.parse_args()

print(args)

conn = sqlite3.connect('tests.db')
cursor = conn.cursor()

cursor.execute(f"CREATE TABLE IF NOT EXISTS {args.table} (id INTEGER PRIMARY KEY AUTOINCREMENT, co2 INTEGER, temperature REAL, humidity REAL, time DATETIME DEFAULT CURRENT_TIMESTAMP)")

co2 = int(random.gauss(1000,100))
humidity = round(random.gauss(50, 13),2)
temperature = round(random.gauss(15, 10),2)

cursor.execute(f"INSERT INTO {args.table} (co2, temperature, humidity) VALUES ({co2}, {temperature}, {humidity})")
conn.commit()
conn.close()
