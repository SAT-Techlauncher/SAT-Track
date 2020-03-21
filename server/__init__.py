from flask import Flask
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_cors import CORS
from config import LOG_PATH

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug

    # cross-origin resource sharing
    # CORS(OpticalCharacterRecognition)
    CORS(app, supports_credentials=True,
         expose_headers="content-disposition, filename")

    # routine blueprint
    from server.views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    # server log
    # log size: maxBytes=1024000, remain logs number: backupCount
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1024000, backupCount=100, encoding='utf-8')
    app.logger.setLevel(logging.INFO)  # control the logger level
    logging_format = logging.Formatter(
        '[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')
    file_handler.setFormatter(logging_format)
    app.logger.addHandler(file_handler)

    return app

app = create_app(debug=False)