import sys
import redis
import json
from config import *
from flask import current_app
import time

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
r = redis.StrictRedis(connection_pool=pool)

# 查看/清空redis中所有数据 (测试用)
class RedisOperator:
    @staticmethod
    def clear():
        print("RedisOperator: clear")
        for k in r.keys():
            name = k.decode('utf-8')
            r.delete(name)

    @staticmethod
    def show():
        print("RedisOperator:")
        for k in r.keys():
            name = k.decode('utf-8')
            for key in r.hkeys(name):
                print(name, ":", key.decode('utf-8'), ":", json.loads(r.hget(name, key)))

# redis dict
class RedisPool:
    def __init__(self, name):
        self.name = name
        self.length = 0

    def set(self, k, v):
        if self.get(k) is None:
            self.length += 1
        # print(self.name, "set", k, v)
        r.hset(self.name, str(k), json.dumps(v))

    def get(self, k):
        v = r.hget(self.name, str(k))
        if v is None:
            return None

        return json.loads(v.decode('utf-8'))

    def pop(self, k):
        r.hdel(self.name, k)
        self.length -= 1

    def clear(self):
        print("cleared " + self.name)
        r.delete(self.name)
        self.length = 0

    def show(self):
        print(self.name + " (" + str(self.length) + ")" + ":")
        for k in r.hkeys(self.name):
            d = r.hget(self.name, k)
            print(k.decode('utf-8'), ':', json.loads(d))

    def search(self, val):
        for k in r.hkeys(self.name):
            res = json.loads(r.hget(self.name, k))
            if val in res:
                res['k'] = k
                return res
        return None

    def to_json(self):
        res = "{'" + self.name + "': '" + str(self.length) + "', {"
        index = 0
        for k in r.hkeys(self.name):
            d = r.hget(self.name, k)
            res += "'" + k.decode('utf-8') + "': '" + json.loads(d) + "', '" if index is not self.length - 1 else ""
            index += 1
        return res + "}}"
