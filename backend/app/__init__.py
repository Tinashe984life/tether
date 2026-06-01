import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, jwt, migrate, bcrypt, cors, ma
from .config import DevelopmentConfig

def create_app(config_name='development'):
    load_dotenv()  # load environment from .env if present
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(DevelopmentConfig)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['JWT_SECRET_KEY'])
    app.config['ENCRYPTION_KEY'] = os.environ.get('ENCRYPTION_KEY', app.config.get('ENCRYPTION_KEY'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)

    # Register API blueprints
    try:
        from .api import auth_bp, notes_bp, search_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(notes_bp, url_prefix='/api/notes')
        app.register_blueprint(search_bp, url_prefix='/api/search')
    except Exception:
        # blueprints may not exist yet during early development
        pass

    return app
