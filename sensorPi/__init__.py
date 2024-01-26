import os
import threading

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'readings.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth
    from . import blog
    from . import hardware

    hardware.init_app(app)
    
    # threading – background function
    def background():
        # wrap the hardware module with app context, allowing it to use the db
        with app.app_context():
            my_database = db.get_db()
            hardware.start_measuring(my_database)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # start a background thread with hardware interaction module
    b = threading.Thread(name='background', target=background)
    b.start()

    return app
