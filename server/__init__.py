from flask import Flask, Blueprint
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_cors import CORS
from config import LOG_PATH

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug

    app.config['SECRET_KEY'] = 'dev'

    # cross-origin resource sharing
    # CORS(OpticalCharacterRecognition)
    CORS(app, supports_credentials=True,
         expose_headers="content-disposition, filename")

    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    # server log
    # log size: maxBytes=1024000, remain logs number: backupCount
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1024000, backupCount=100, encoding='utf-8')
    app.logger.setLevel(logging.INFO)  # control the logger level
    logging_format = logging.Formatter(
        '[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')
    file_handler.setFormatter(logging_format)
    app.logger.addHandler(file_handler)

    from server.views import bp
    app.register_blueprint(bp)

    return app

app = create_app(debug=False)


