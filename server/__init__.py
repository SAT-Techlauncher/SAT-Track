from flask import Flask
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_cors import CORS
from config import LOG_PATH

app = Flask(__name__)

app.debug = False

app.config['SECRET_KEY'] = 'dev'

# cross-origin resource sharing
# CORS(OpticalCharacterRecognition)
CORS(app, supports_credentials=True,
     expose_headers="content-disposition, filename")

# server log
#  log size: maxBytes=1024000, remain logs number: backupCount
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1024000, backupCount=100, encoding='utf-8')
app.logger.setLevel(logging.INFO)  # control the logger level
logging_format = logging.Formatter(
    '[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')
file_handler.setFormatter(logging_format)
app.logger.addHandler(file_handler)

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
csrf.init_app(app)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from server.models.model import User
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

from server.views.routes import routes_bp
from server.views.view import view_bp
from server.views.auth import auth_bp

app.register_blueprint(routes_bp)
app.register_blueprint(view_bp)
app.register_blueprint(auth_bp)

from server.controllers import user_info_pool, user_satelites_pool, satellite_users_pool
user_info_pool.show()
user_satelites_pool.show()
satellite_users_pool.show()

from redis_pool import RedisOperator
RedisOperator.clear()

