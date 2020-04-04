import sys
import time
from flask import current_app
from . import *

sec = 0
min = 0

# 系统计时器, 每秒执行一次, 用以注册系统中的各种定时任务事件
@scheduler.task(trigger='cron', id='timer', second='*/1', max_instances=5)
def timer():
    global sec
    sec += 1

    global min
    if sec % 60 == 0:
        min += 1

    # 当秒数超过系统最大整数值后归零
    if sec == sys.maxsize - 1:
        sec = 0


