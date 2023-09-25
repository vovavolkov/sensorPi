import sqlite3
import argparse
import random
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('table', default="readings", nargs ='?', help='table for readings')
args = parser.parse_args()

print(args)

conn = sqlite3.connect('tests.db')
cursor = conn.cursor()

date = datetime.datetime.now()

cursor.execute(f"CREATE TABLE IF NOT EXISTS {args.table} (id INTEGER PRIMARY KEY AUTOINCREMENT, co2 INTEGER, temperature REAL, humidity REAL, time DATETIME DEFAULT CURRENT_TIMESTAMP)")

print("how many entries?")

n = int(input())

for i in range(n):
    co2 = int(random.gauss(1000,100))
    humidity = round(random.gauss(50, 13),2)
    temperature = round(random.gauss(15, 10),2)
    date = date +  datetime.timedelta(seconds=5)
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(f"INSERT INTO {args.table} (co2, temperature, humidity, time) VALUES ({co2}, {temperature}, {humidity}, '{date_str}')")

conn.commit()
conn.close()
