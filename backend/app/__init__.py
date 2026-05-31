from flask import Flask
from .extensions import db, jwt, migrate
from .config import DevelopmentConfig

def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    return app
