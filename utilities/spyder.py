# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 17:27:48 2020

@author: HP
"""

import urllib.request
import urllib.response
import re
import time
import json
import math
from concurrent.futures.thread import ThreadPoolExecutor

# 单个并发任务类, 实现python异步非阻塞函数
class ConcurrentTask:
    def __init__(self, executor, task=None, callback=None, targs=None, cargs=None):
        """
        init
        :param executor: python.concurrent.futures ThreadingPoolExecutor实例
        :param task: 并发任务函数
        :param callback: 回调函数
        :param targs: 并发任务函数输入参数
        :param cargs: 回调函数输入参数
        """
        self.task = task
        self.callbackTask = callback
        self.targs = targs
        self.cargs = cargs
        self.future = None
        self.executor = executor

    def run(self):
        """
        开启新线程运行并发任务并在有结果返回时运行回调函数
        :return:
        """
        self.future = self.executor.submit(self.task, *self.targs)
        if self.callbackTask is not None:
            self.future.add_done_callback(self.__callback)

    def __callback(self, future):
        """
        传入并发任务的返回结果并执行回调函数
        :param future: python.concurrent.futures future实例
        :return:
        """
        if self.callbackTask is None:
            raise NotImplementedError
        try:
            self.callbackTask(*self.cargs, result=future.result())
        except:
            self.callbackTask(*self.cargs)

    def getResult(self):
        """
        获取单个并发任务执行结果
        :return: 执行结果
        """
        return self.future.result()

# 多并发任务管理池
class ConcurrentTaskPool:
    def __init__(self, executor=None):
        """
        init
        :param executor: python.concurrent.futures ThreadingPoolExecutor实例
        """
        self.tasks = []
        self.executor = executor

    def addTasks(self, tasks):
        """
        批量注册并执行并发任务
        :param tasks: 并发任务列表 [ConcurrentTask, ConcurrentTask, ...]
        :return:
        """
        for task in tasks:
            task.future = self.executor.submit(task.task, *task.targs)
            self.tasks.append(task)

    def add(self, concurrentTask):
        """
        注册并执行并发任务
        :param concurrentTask: 并发任务实例
        :return:
        """
        concurrentTask.future = self.executor.submit(concurrentTask.task, *concurrentTask.targs)
        self.tasks.append(concurrentTask)

    def getResults(self, wait=False):
        """
        获取并发任务执行结果 (当最晚执行完毕的任务结束后返回结果, 此间线程阻塞)
        :param wait: 设定获取结果时线程是否阻塞
        :return: 返回结果列表
        """
        self.executor.shutdown(wait=wait)
        results = []
        for task in self.tasks:
            result = task.future.result()
            # print('result: ', result)
            results.append(result)
        # 获取所有并发任务结果后清空任务列表
        self.tasks.clear()
        return results


'''
for dev
'''

class Spyder():
    def __init__(self,satellite_number):
        self.satellite_number = satellite_number
        self.url = 'https://www.n2yo.com/satellite/?s='

    def get_url(self):
        self.url += self.satellite_number

    def get_response(self):
        self.get_url()
        response = urllib.request.urlopen(self.url)
        return response

    def download(self):
        res = self.get_response()
        with open('{} {}'.format('sat' , self.satellite_number),'wb') as f:
            f.write(res.read())

    def parse(self):
        pattern = re.compile(r'.*?<pre?>(.*?)</pre>',re.S)
        result = re.findall(pattern, self.get_response().read().decode())
        return result[0].split()


class SatCatalog:
    # Int'l Code, NORAD ID, Status, Name, Source, Launch Date, Launch Site, Decay Date, _0_, _1_, _2_, _3_, _4_
    head = {
        'Int\'l Code': 12,
        'NORAD ID': 18,
        'Status': 22,
        'Name': 48,
        'Source': 55,
        'Launch Date': 66,
        'Launch Site': 74,
        'Decay Date': 85,
        '_0_': 95,
        '_1_': 101,
        '_2_': 109,
        '_3_': 117,
        '_4_': 128
    }

    def __init__(self, start=None, end=None):
        self.__data = None
        self.start = start
        self.end = end

    def read_raw(self, dir):
        with open(dir, 'r') as file:
            lines = file.readlines()
        self.__data = lines if self.start is None or self.end is None else lines[self.start : self.end + 1]

    def to_table(self):
        assert self.__data is not None

        lines = self.__data
        table = [list(self.head.keys())]
        col_idxs = [0] + list(self.head.values()) + [len(lines[len(lines) - 1])]

        for line in lines[1:len(lines)]:
            row = ''
            for i in range(len(col_idxs) - 1):
                cur = col_idxs[i]
                next = col_idxs[i + 1]
                row += line[cur:next] + ','
            values = row.split(',')
            vals = []
            for value in values:
                val = value.lstrip().rstrip()
                if val.replace('.', '').isdigit():
                    val = float(val) if '.' in val else int(val)
                vals.append(val)
            table.append(vals[0:len(vals) - 1])
        return table

    def to_json(self):
        table = self.to_table()
        satellites = []
        for arr in table[1:len(table)]:
            col = 0
            satellite = {}
            for key in list(self.head.keys()):
                satellite[key] = arr[col]
                col += 1
            satellites.append(satellite)

        return satellites

    def write_ripe(self, dir, ripe):
        with open(dir, 'w') as file:
            file.write(json.dumps(ripe))

    def read_ripe(self, dir):
        with open(dir, 'r') as file:
            return json.loads(file.read())[self.start:self.end + 1]


def get_sat(start, end):
    sat_cat = SatCatalog(start, end)

    sat_cat.read_raw(RAW_DIR)
    data = sat_cat.to_json()

    sat_cat.write_ripe(RIPE_DIR, ripe=data)

def concurrent_tasks(length, task):
    # python多线程池对象 (最大线程数从配置文件中获取)
    executor = ThreadPoolExecutor(max_workers=100)

    global NUM
    NUM = 0
    # 并发任务列表
    tasks = []
    # 获取origins和extracts中数据条数 (两者相等)
    # 从配置文件中获取es上传并发数
    concurrentNum = CONCURRENT_NUM
    # 若数据条数大于最小并发触发数, 则执行并发上传; 否则, 执行单线程上传
    # 近似等分待上传数据并注册并发任务
    for i in range(concurrentNum):
        ptr = math.floor(i / concurrentNum * length)
        ptr_ = math.floor((i + 1) / concurrentNum * length) - 1

        print(ptr, ptr_)
        # 注册并发任务 (简略新闻数据和原始新闻数据分开上传)
        tasks.extend([
            ConcurrentTask(executor, task=task, targs=(RES_DIR_ + str(i) + '.json', ptr, ptr_, i)),
        ])

    # 并发任务池对象
    taskPool = ConcurrentTaskPool(executor)
    # 添加并执行es上传并发任务
    taskPool.addTasks(tasks)
    # 获取es上传结果列表 (当最晚执行完毕的任务结束后返回结果, 此间线程阻塞)
    results = taskPool.getResults(wait=True)

    # 根据es上传结果列表计算上传成功的数据总数
    excepts = []
    for result in results:
        excepts += result

def get_tle(dir, start, end, index):
    sat_cat = SatCatalog(start, end)

    satellites = sat_cat.read_ripe(RIPE_DIR)

    res = []
    excepts = []
    global NUM

    with open(dir, 'a') as file:
        file.write('[')

    idx = 0
    for sat in satellites:
        norad_id = sat['NORAD ID']

        try:
            tle = Spyder(str(norad_id)).parse()
            dt = {str(norad_id): tle} if tle != [] else {str(norad_id): ['None']}
        except:
            dt = {str(norad_id): ['Error']}
            excepts.append(norad_id)

        with open(dir, 'a') as file:
            if idx != len(satellites) - 1:
                file.write(json.dumps(dt) + ', ')
            else:
                file.write(json.dumps(dt))

        res.append(dt)
        NUM += 1
        idx += 1
        print(NUM, '/', 45475, '(', str(index), '):    ' ,dt)

    with open(dir, 'a') as file:
        file.write(']')

    return excepts


RAW_DIR = '../../data/raw_satcat.txt'
RIPE_DIR = '../../data/sattle/ripe_satcat.json'
RES_DIR_ = '../../data/sattle/res_'
CONCURRENT_NUM = 60
NUM = 0

# if __name__ == '__main__':
#     timer = time.time()
#
#     start = 0
#     end = 45475
#
#     get_sat(0, end)
#
#     print(end - start / 6)
#
#
#     excepts = concurrent_tasks(end - start, get_tle)
#
#     print(excepts)
#
#     print('Running time (spyder):' + str(time.time() - timer))