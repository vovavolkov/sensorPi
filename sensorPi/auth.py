import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from sensorPi.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = 'Invalid credentials.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


def create_user(username, password):
    db = get_db()
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
    return error


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def change_password(current_password, new_password):
    db = get_db()
    uid = session.get('user_id')
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (uid,)
    ).fetchone()

    if not check_password_hash(user['password'], current_password):
        error = 'Current password is invalid.'

    if error is None:
        db.execute(
            "UPDATE user SET password = ? WHERE id = ?",
            (generate_password_hash(new_password, method='pbkdf2:sha3_512', salt_length=8), uid)
        )
        db.commit()

    return error

