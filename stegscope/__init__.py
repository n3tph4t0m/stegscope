from flask import Flask

from .config import Config


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    from .views import bp

    app.register_blueprint(bp)
    return app
