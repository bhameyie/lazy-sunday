import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)

    app_setting = 'appsettings.py'
    app.config.from_pyfile(app_setting)

    if test_config is not None:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/health')
    def hello():
        return 'All good!'

    from moviefriday import auth, watch, db, upload
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(watch.bp)
    app.register_blueprint(upload.bp)

    app.add_url_rule('/', endpoint='index')

    return app
