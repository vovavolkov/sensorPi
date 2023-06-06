import sqlite3
import random

conn = sqlite3.connect('readings.db')
curs = conn.cursor()

curs.execute("CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, co2 INTEGER, temp REAL, hum REAL, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

co2 = random.randint(0, 1000)
temp = round(random.uniform(0, 50), 2)
hum = round(random.uniform(0, 100), 2)

curs.execute("INSERT INTO readings (co2, temp, hum) VALUES (?, ?, ?)", (co2, temp, hum))

conn.commit()
conn.close()
