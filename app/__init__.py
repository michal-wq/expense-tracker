import os

from flask import Flask

from app.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL")
    app.register_blueprint(bp)
    return app
