
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from matplotlib.figure import Figure

from sensorPi.auth import login_required, change_password, create_user
from sensorPi.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    date = datetime.now().strftime("%Y-%m-%d")
    posts = db.execute(
        'SELECT time, co2, temperature, humidity'
        ' FROM readings'
        ' where time like ?', (date,)
    ).fetchall()

    return render_template('blog/index.html', )


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
