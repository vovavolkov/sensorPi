import base64
import statistics
from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from matplotlib.figure import Figure

from sensorPi.auth import login_required, change_password, create_user
from sensorPi.db import get_db

bp = Blueprint('graphs', __name__)


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


@bp.route('/')
def index():
    # get the database and the current day
    current_day = datetime.now()
    current_day = current_day.strftime("%Y-%m-%d")
    print(current_day)

    # return the index page with the graphs and standard deviations passed as arguments
    return render_template('graphs/index.html', current_day=current_day)


@bp.route('/graph/<date>')
def graph_day(date):
    # get the database and the current day from the url
    db = get_db()
    current_day = date
    # convert the date to a datetime object
    # try catch block to handle invalid date
    try:
        current_day = datetime.strptime(current_day, '%Y-%m-%d')
    except ValueError:
        flash("Invalid date")
        return render_template('graphs/graph.html')
    # get the next day – to limit the readings to today
    next_day = current_day + timedelta(days=1)
    prev_day = current_day - timedelta(days=1)
    prev_day = prev_day.strftime("%Y-%m-%d")
    current_day_str = current_day.strftime("%-d %B %Y")
    next_day = next_day.strftime("%Y-%m-%d")
    print(prev_day, current_day, next_day)

    # get the readings from the database
    values = db.execute(
        'SELECT time, co2, temperature, humidity'
        ' FROM readings'
        ' WHERE time >= ? and time < ?', (current_day, next_day,)
    ).fetchall()
    # if there are no readings, return the empty index page
    if len(values) == 0:
        flash("No readings for this day")
        return render_template('graphs/graph.html', prev_day=prev_day, current_day=current_day_str, next_day=next_day)
    # split the values 2d array into separate lists
    times = [v[0].split(" ")[1] for v in values]
    co2 = [v[1] for v in values]
    temperature = [v[2] for v in values]
    humidity = [v[3] for v in values]

    # for each reading, create a plot and add it to the list of graphs
    co2_str = plot(times, co2, "date", "co2", "CO2 over time")
    temp_str = plot(times, temperature, "date", "temperature", "Temperature over time")
    hum_str = plot(times, humidity, "date", "humidity", "Humidity over time")
    graphs = [co2_str, temp_str, hum_str]

    # for each reading, calculate the standard deviation
    co2_stdev = round(statistics.stdev(co2), 4)
    temperature_stdev = round(statistics.stdev(temperature), 4)
    humidity_stdev = round(statistics.stdev(humidity), 4)

    # return the index page with the graphs and standard deviations passed as arguments
    return render_template('graphs/graph.html', graphs=graphs, co2_stdev=co2_stdev,
                           temperature_stdev=temperature_stdev, humidity_stdev=humidity_stdev,
                           prev_day=prev_day, current_day=current_day_str, next_day=next_day)


# admin page – register new users and change the password
@bp.route('/admin', methods=('GET', 'POST'))
# only users which are logged in can access the admin page
@login_required
def admin():
    # check each of two possible forms
    if request.method == 'POST':
        # if the register form is submitted, create a new user, using the create_user from auth.py
        if 'Register' in request.form:
            username = request.form['username']
            password = request.form['password']
            error = create_user(username, password)
            flash(error)
            # if the change form is submitted, change the password, using the change_password from auth.py
        if 'Change' in request.form:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            error = change_password(current_password, new_password)
            if error is None:
                return redirect(url_for('auth.login'))
            flash(error)
    # get the database and the list of all users
    db = get_db()
    admins = db.execute(
        'SELECT username FROM user'
    ).fetchall()
    # TODO: add ability to download sql database from instance folder
    return render_template('graphs/admin.html', admins=admins)
