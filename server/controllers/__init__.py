from flask_apscheduler import APScheduler

from config import conf
from server.models.status_code import *
from utilities.es_io import ES
from utilities.redis_pool_io import RedisPool
from server.controllers.controller_manager import ControllerManager

# 定时任务
scheduler = APScheduler()

# 用户信息池 { key : user_id, value: { email, password }}
user_info_pool = RedisPool(conf.USER_POOL_NAME)
# 用户-卫星关联池 { key: user_id, value: satellite_id }
# user_satelites_pool = RedisPool(conf.USER_SAT_POOL_NAME)
# 卫星-用户关联池 ( 速度优化 ) { key : satellite_id, value: user_id }
# satellite_users_pool = RedisPool(conf.SATELLITE_USERS_POOL_NAME)

# 卫星信息数据库 { key: sat_id, value: { name, location, data } }
satellite_pool = RedisPool(conf.ES_DATA_INDEX)
satellite_database = ES(conf.ES_DATA_INDEX, create=True)

