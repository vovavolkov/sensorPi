import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin", method='pbkdf2:sha3_512', salt_length=8))
        )
    db.commit()


def insert_readings(co2, temperature, humidity, db):
    try:
        db.execute(
            "INSERT INTO readings (co2, temperature, humidity) VALUES (?, ?, ?)",
            (co2, temperature, humidity)
        )
        db.commit()
    except Exception as e:
        print(e)


@click.command('init-db')
def init_db_command():
    # Clear the existing data and create new tables.
    init_db()

    click.echo('Initialized the database.\n'
               'A user admin:admin has been created.\n'
               'Please change the password on first login.')


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
