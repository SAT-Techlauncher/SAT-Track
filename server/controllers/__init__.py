from config import USER_POOL_NAME, USER_SAT_POOL_NAME, EMAIL_USER_POOL_NAME, SATELLITE_USERS_POOL_NAME
from redis_pool import RedisPool
from .satellite_tracking_controller import satellite_tracking

# 用户信息池 { key : user_id, value: { email, password }}
user_info_pool = RedisPool(USER_POOL_NAME)
# 用户-卫星关联池 { key: user_id, value: satellite_id }
user_satelites_pool = RedisPool(USER_SAT_POOL_NAME)
# 卫星-用户关联池 ( 速度优化 ) { key : satellite_id, value: user_id }
satellite_users_pool = RedisPool(SATELLITE_USERS_POOL_NAME)
