import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_cors import CORS

from config import conf

app = Flask(__name__)

app.debug = False

app.config['SECRET_KEY'] = 'dev'

# cross-origin resource sharing
# CORS(OpticalCharacterRecognition)
CORS(app, supports_credentials=True,
     expose_headers="content-disposition, filename")

# server log
#  log size: maxBytes=1024000, remain logs number: backupCount
file_handler = RotatingFileHandler(conf.LOG_PATH, maxBytes=1024000, backupCount=100, encoding='utf-8')
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

from server.services.data_storage_service import UserManager
@login_manager.user_loader
def load_user(user_id):
    return UserManager.get(user_id)

from server.views.routes import routes_bp
from server.views.view import view_bp
from server.views.auth import auth_bp

app.register_blueprint(routes_bp)
app.register_blueprint(view_bp)
app.register_blueprint(auth_bp)

from server.services import user_info_pool
if conf.CLEAR_REDIS:
    user_info_pool.clear()
else:
    user_info_pool.show()

from utilities.redis_pool_io import RedisOperator
RedisOperator.show(conf.USER_SAT_POOL_NAME)
