import os
import sys

class BASE:
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
    # satellite - user table
    TRACKING_POOL_NAME = 'tracking_pool'

    # elasticsearch
    ES_DATA_INDEX = 'SAT'
    # es connection
    ES_URL = '127.0.0.1'
    # es max response time
    ES_TIMEOUT = 60
    # es max upload number of type
    ES_MAPPING_LIMIT = 5000
    # es max download number of data
    ES_QUERY_MAX_SIZE = 5000
    # es max concurrent task number
    MAX_WORKERS = 10
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

    # 是否删除已存在的es索引表并建立新表
    ES_CREATE_ENABLE = False
    # 启动服务器时是否清空redis
    CLEAR_REDIS = False

    # 一次查询返回最大卫星数据条数
    SEARCH_RESULT_LMT = 100

    # 文本分析语料库
    RAW_DIR_ = os.path.dirname(__file__) + '/data/'
    RIPE_DIR_ = os.path.dirname(__file__) + '/data/lib/'

    GOOGLEMAP_API_URL = 'https://maps.googleapis.com/maps/api/elevation/json?locations=%(lat)s,%(long)s&key=%(key)s'
    GOOGLEMAP_API_KEY = 'AIzaSyCLfxHknd8lggQOOqLV3LHoSBAhMmLOZsU'
    IPSTACK_API_URL = 'http://api.ipstack.com/%(ip)s?access_key=%(key)s'
    IPSTACK_API_KEY = 'ac5dc2221554ed9fb1ec670d69aabb02'

    POLLING_INTERVAL = 60


class DEMO(BASE):
    SERVER_HOST = '0.0.0.0'


conf = DEMO

if len(sys.argv) < 2:
    conf = BASE
elif sys.argv[1] == 'demo':
    conf = DEMO


