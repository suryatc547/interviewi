import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from controllers.interview_controller import interview_bp
from models.models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    CORS(app)
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(interview_bp, url_prefix='/api/interview')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
