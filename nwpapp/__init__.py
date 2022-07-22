import logging
from logging.handlers import WatchedFileHandler
import os

from flask import Flask, send_from_directory
from nwpapp import config
from nwpapp.extensions import mail
def create_app(config=config.base_config):
# create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # DATABASE_FILE = os.path.join(app.instance_path, "nwpapp.sqlite")

    app.config.from_object(config)

    app.config.from_pyfile("G:/Python/مشروع الاخ تركي/project/nwpapp/config.py", silent=True)

    mail.init_app(app)

    #setup logging
    handler = WatchedFileHandler(app.config["LOGFILE"])
    handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '))
    root = logging.getLogger()
    root.setLevel(app.config["LOGLEVEL"])
    root.addHandler(handler)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)

    except OSError:
        pass

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static/favicon"),
            "favicon_ico.png",
            mimetype="image/vnd.microsoft.icon",
        )

    # init flask_sqlalchemy
    from nwpapp.model.auth_model import db

    db.init_app(app)

    # init command line interface
    from nwpapp.view import cli

    cli.init_app(app)

    from nwpapp.view import auth

    app.register_blueprint(auth.bp)
    from nwpapp.view import parameters

    app.register_blueprint(parameters.bp)
    app.add_url_rule("/", endpoint="index")
    from nwpapp.view import api

    app.register_blueprint(api.bp)

    from flask_migrate import Migrate
    MIGRATE_DIR = os.path.join(os.path.dirname(__file__),"model","migrations")
    migrate = Migrate(app, db, directory=MIGRATE_DIR)

    from flask_admin import Admin
    from nwpapp.view.auth import AdminView
    from nwpapp.model.auth_model import db, User, Group, NSector

    admin = Admin(app, name="NWP Admin", template_mode="bootstrap3")
    admin.add_view(AdminView(User, db.session))
    admin.add_view(AdminView(Group, db.session))
    admin.add_view(AdminView(NSector, db.session))

    return app

