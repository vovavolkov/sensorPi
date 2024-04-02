import os
import threading
import json

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # replace for production
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'readings.db'),
    )

    if test_config is None:
        # ensure the config.py exists
        # load the instance config, if it exists, when not testing
        if os.path.exists(os.path.join(app.instance_path, 'config.json')):
            app.config.from_file('config.json', load=json.load, silent=True)
        else:
            SECRET_KEY = os.urandom(16).hex()
            config = {
                'SECRET_KEY': SECRET_KEY,
                'DATABASE': os.path.join(app.instance_path, 'readings.db')
            }
            print(config)

            with open(os.path.join(app.instance_path, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import auth, db, graphs

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(graphs.bp)
    app.add_url_rule('/', endpoint='index')

    if not app.config['DEBUG']:
        from . import hardware
        hardware.init_app(app)

        # threading – background function
        def background():
            # wrap the hardware module with app context, allowing it to use the db
            with app.app_context():
                my_database = db.get_db()
                hardware.start_measuring(my_database)

        # start a background thread with hardware interaction module
        b = threading.Thread(name='background', target=background)
        b.daemon = True
        b.start()

    return app
