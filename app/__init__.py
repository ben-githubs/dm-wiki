"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import config
from . import jinja_filters as filters

db = SQLAlchemy()
mg = Migrate()
lm = LoginManager()

def init_app():
    """Create Flask app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config.DevConfig)

    db.init_app(app)
    mg.init_app(app, db)
    lm.init_app(app)

    with app.app_context():
        # Import parts of the application
        from .main import routes as main

        # Register blueprints
        app.register_blueprint(main.main_bp)

        # Register template filters
        app.jinja_env.filters['markdown'] = filters.markdown

        return app