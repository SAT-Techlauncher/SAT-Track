from flask import Blueprint

routes_bp = Blueprint('routes', __name__)
view_bp = Blueprint('view', __name__)
auth_bp = Blueprint('auth', __name__)

from flask import request, current_app, render_template, jsonify, redirect, session, url_for, g, flash
from flask_login import login_user, logout_user, login_required, current_user
from server.controllers import user_info_pool, satellite_pool
from server.controllers.user_behavior_controller import *
from server.controllers.satellite_tracking_controller import controll_satellite_tracking
from server.models.form import LoginForm, RegisterForm
from server.models.objects import User
from server.services.data_storage_service import *
from server.models.status_code import RET
from utilities.utils import Utils
import json
