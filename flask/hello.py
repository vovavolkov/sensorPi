import base64
import sqlite3
from io import BytesIO

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
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    data = base64.b64encode(buffer.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        global date
        date = request.form['date']
        return redirect('/')
    else:
        conn = sqlite3.connect("db/tests.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT time, co2, temperature, humidity from {table}")
        values = cursor.fetchall()

        times = [v[0] for v in values]
        co2 = [v[1] for v in values]
        temperature = [v[2] for v in values]
        humidity = [v[3] for v in values]

        times = pd.to_datetime(times)

        current_co2 = co2[-1]
        co2_str = plot(times, co2, "date", "co2", "CO2 over time")
        temp_str = plot(times, temperature, "date", "temperature", "Temperature over time")
        hum_str = plot(times, humidity, "date", "humidity", "Humidity over time")
        graphs = [co2_str, temp_str, hum_str]
        return render_template(
            'index.html', co2=current_co2, graphs=graphs, selected_date=date
        )
