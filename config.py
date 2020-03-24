import os

# log path
LOG_PATH = os.path.dirname(__file__) + '/logs/server.log'

# server address
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

# redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''
# user info table
USER_POOL_NAME = 'user_info_pool'
# user - satellites table
USER_SAT_POOL_NAME = 'user_satellites_pool'
# email - user table
EMAIL_USER_POOL_NAME = 'email_user_pool'
# satellite - user table
SATELLITE_USERS_POOL_NAME = 'satellite_users_pool'

# elasticsearch
ES_DB_INDEX = 'zzdb'
# es connection
ES_URL = '127.0.0.1'
# es max response time
ES_TIMEOUT = 60
# es max upload number of type
ES_MAPPING_LIMIT = 5000
# es max download number of data
ES_QUERY_MAX_SIZE = 5000
# es max concurrent task number
MAX_WORKERS = 5
# es上传下载时间间隔 (按秒计算)
UPLOAD_DOWNLOAD_INTERVAL = 1
# es上传启动并发最小数据量
MIN_UPLOAD_NUM_FOR_CONCURRENT_TASK = 5
# es上传并发数
UPLOAD_CONCURRENT_TASK_NUM = 3
# es下载启动并发最小数据量
MIN_DOWNLOAD_NUM_FOR_CONCURRENT_TASK = 3
# es下载并发数
DOWNLOAD_CONCURRENT_TASK_NUM = 3


