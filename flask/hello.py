import base64
import sqlite3
from io import BytesIO
import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect
from matplotlib.figure import Figure

app = Flask(__name__)
table = "readings"


def plot(x_axis, y_axis, x_label, y_label, title):
    fig = Figure()
    ax = fig.subplots()
    ax.plot(x_axis, y_axis)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    ax.set_xticks(ax.get_xticks()[::(len(x_axis) // 5)])
    # save the figure to a buffer, then convert to base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    data = base64.b64encode(buffer.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect("db/readings.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT time from {table}")
    times = [t[0] for t in cursor.fetchall()]
    times = pd.to_datetime(times)
    min_date = times[0].strftime("%Y-%m-%d")
    max_date = times[-1].strftime("%Y-%m-%d")
    date = max_date
    if request.method == 'POST':
        date = request.form['date']

    cursor.execute(f"SELECT time, co2, temperature, humidity from {table} where time like '{date}%'")

    try:
        values = cursor.fetchall()
        # select time but not date
        times = [v[0].split(" ")[1] for v in values]
        co2 = [v[1] for v in values]
        temperature = [v[2] for v in values]
        humidity = [v[3] for v in values]
        current_co2 = co2[-1]
    except IndexError:
        current_co2 = None
        times = []
        co2 = []
        temperature = []
        humidity = []

    co2_str = plot(times, co2, "date", "co2", "CO2 over time")
    temp_str = plot(times, temperature, "date", "temperature", "Temperature over time")
    hum_str = plot(times, humidity, "date", "humidity", "Humidity over time")
    graphs = [co2_str, temp_str, hum_str]
    return render_template(
        'index.html', co2=current_co2, graphs=graphs, selected_date=date,
        min_date=min_date, max_date=max_date
    )
