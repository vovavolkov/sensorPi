import base64
import sqlite3
from io import BytesIO
import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect
from matplotlib.figure import Figure

app = Flask(__name__)
table = "readings"


# create a plot for readings
def plot(x_axis, y_axis, x_label, y_label, title):
    # create a figure object and add axes
    fig = Figure()
    ax = fig.subplots()
    # plot the data onto the axes (x-axis is time, y-axis is the value)
    ax.plot(x_axis, y_axis)
    # label the axes and add a title
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    # every (len / 5)th tick is shown, to avoid clutter
    ax.set_xticks(ax.get_xticks()[::(len(x_axis) // 5)])
    # save the figure to a buffer, then convert to base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    b64image = base64.b64encode(buffer.getbuffer()).decode("ascii")
    # return the base64 string to be used in the html
    return f"data:image/png;base64,{b64image}"


@app.route('/', methods=['GET', 'POST'])
def index():
    # get the dates from the database
    conn = sqlite3.connect("db/readings.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT time from {table}")
    # convert the timestamps to datetime objects
    times = [t[0] for t in cursor.fetchall()]
    times = pd.to_datetime(times)
    # get the min and max dates for the date picker
    min_date = times[0].strftime("%Y-%m-%d")
    max_date = times[-1].strftime("%Y-%m-%d")
    # set the default date to the max date, i.e. today
    date = max_date
    if request.method == 'POST':
        date = request.form['date']

    # get the values from the database for the selected date
    cursor.execute(f"SELECT time, co2, temperature, humidity from {table} where time like '{date}%'")

    try:
        values = cursor.fetchall()
        # select time but not date
        times = [v[0].split(" ")[1] for v in values]
        co2 = [v[1] for v in values]
        temperature = [v[2] for v in values]
        humidity = [v[3] for v in values]
        current_co2 = co2[-1]

    # if there are no values for the selected date, set everything to None to avoid errors
    except IndexError:
        current_co2 = None
        times = []
        co2 = []
        temperature = []
        humidity = []

    # create the plots
    co2_str = plot(times, co2, "date", "co2", "CO2 over time")
    temp_str = plot(times, temperature, "date", "temperature", "Temperature over time")
    hum_str = plot(times, humidity, "date", "humidity", "Humidity over time")
    graphs = [co2_str, temp_str, hum_str]
    # return the html template with the plots and the selected date
    return render_template(
        'index.html', co2=current_co2, graphs=graphs, selected_date=date,
        min_date=min_date, max_date=max_date
    )


# testing the login
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect('/')
    return render_template('auth/login.html')