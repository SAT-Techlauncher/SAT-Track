from flask_apscheduler import APScheduler

from config import conf
from server.models.status_code import *
from server.controllers.controller_manager import ControllerManager

# 定时任务
scheduler = APScheduler()
