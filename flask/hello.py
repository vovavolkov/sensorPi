import base64
from flask import Flask, render_template
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("tests.db")
cursor = conn.cursor()
cursor.execute("SELECT time, co2, temperature, humidity from readings")

values = cursor.fetchall()

times = [v[0] for v in values]
co2 = [v[1] for v in values]
temperature = [v[2] for v in values]
humidity = [v[3] for v in values]

times = pd.to_datetime(times)

first_date = times[0].strftime("%Y-%m-%d")
last_date = times[-1].strftime("%Y-%m-%d")


def plot(x_axis,y_axis,x_label,y_label,title):
    fig = Figure()

    ax = fig.subplots()
    ax.plot(x_axis, y_axis)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

@app.route('/')

def hello():
    print("bob")
    current_co2 = co2[-1]
    co2_str= plot(times, co2, "date", "co2", "CO2 over time")
    temp_str=plot(times, temperature, "date", "temperature", "Temperature over time")
    hum_str=plot(times, humidity, "date", "humidity", "Humidity over time")
    images_list = [co2_str, temp_str, hum_str]
    return render_template('hello.html', co2=current_co2, images=images_list)
