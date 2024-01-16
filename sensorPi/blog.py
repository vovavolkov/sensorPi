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

bp = Blueprint('blog', __name__)


def plot(x_axis, y_axis, x_label, y_label, title):
    fig = Figure()
    ax = fig.subplots()
    ax.plot(x_axis, y_axis)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    ax.set_xticks(ax.get_xticks()[::(len(x_axis) // 5)])
    # save the figure to a buffer, then convert to base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    b64image = base64.b64encode(buffer.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{b64image}"


@bp.route('/')
def index():
    db = get_db()
    current_day = datetime.now().strftime("%Y-%m-%d")
    next_day = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    values = db.execute(
        'SELECT time, co2, temperature, humidity'
        ' FROM readings'
        ' WHERE time >= ? and time < ?', (current_day, next_day,)
    ).fetchall()
    times = [v[0].split(" ")[1] for v in values]
    co2 = [v[1] for v in values]
    temperature = [v[2] for v in values]
    humidity = [v[3] for v in values]

    co2_str = plot(times, co2, "date", "co2", "CO2 over time")
    temp_str = plot(times, temperature, "date", "temperature", "Temperature over time")
    hum_str = plot(times, humidity, "date", "humidity", "Humidity over time")
    graphs = [co2_str, temp_str, hum_str]

    co2_stdev = round(statistics.stdev(co2), 4)
    temperature_stdev = round(statistics.stdev(temperature), 4)
    humidity_stdev = round(statistics.stdev(humidity), 4)

    return render_template('blog/index.html', graphs=graphs, co2_stdev=co2_stdev,
                           temperature_stdev=temperature_stdev, humidity_stdev=humidity_stdev)


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
def admin():
    # TODO: create new users?
    # check each of two possible forms
    if request.method == 'POST':
        if 'Register' in request.form:
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    db.execute(
                        "INSERT INTO user (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password, method='pbkdf2:sha3_512', salt_length=8))
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("auth.login"))

            flash(error)
        elif 'Change' in request.form:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            error = change_password(current_password, new_password)
            if error is None:
                return redirect(url_for('auth.login'))
            flash(error)

    return render_template('blog/admin.html')
