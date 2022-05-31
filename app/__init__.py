from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flaskext.markdown import Markdown
from pymysql import install_as_MySQLdb

import config


install_as_MySQLdb()

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    from app import models

    # Blueprints
    from app.views import main_views, question_views, answer_views, auth_views, comment_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(comment_views.bp)

    # Filters
    from app.filter import datetime_format
    app.jinja_env.filters['datetime'] = datetime_format

    # Markdown
    Markdown(app, extensions=['nl2br', 'fenced_code'])

    # Mail
    mail.init_app(app)

    return app
