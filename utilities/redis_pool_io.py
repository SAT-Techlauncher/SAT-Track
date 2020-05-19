import sys
import redis
import json
from config import conf
from flask import current_app
import time

pool = redis.ConnectionPool(host=conf.REDIS_HOST, port=conf.REDIS_PORT, db=conf.REDIS_DB, password=conf.REDIS_PASSWORD)
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
    def show(name=''):
        print("RedisOperator:")
        for key in r.hkeys(name):
            print(name, ":", key.decode('utf-8'), ":", json.loads(r.hget(name, key)))

# redis dict
class RedisPool:
    def __init__(self, name):
        self.name = name

    def set(self, k, v):
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

    def get_all(self):
        kvs = {}
        for k in r.hkeys(self.name):
            d = r.hget(self.name, k)
            kvs.update({k.decode('utf-8'): json.loads(d)})
        return kvs

    def clear(self):
        print("cleared " + self.name)
        r.delete(self.name)
        self.length = 0

    def show(self, prefix=''):
        print(prefix, self.name + " (" + str(self.get_length()) + ")" + ":")
        for k in r.hkeys(self.name):
            d = r.hget(self.name, k)
            print(k.decode('utf-8'), ':', json.loads(d))

    def get_length(self):
        try:
            return len(r.hkeys(self.name))
        except:
            return 0

    def get_size(self):
        return str(round((sys.getsizeof(r.hkeys(self.name)) + sys.getsizeof(r.hvals(self.name))) / (1024 * 1), 2)) + 'KB'

    def info(self, prefix=''):
        length = self.get_length()
        size = self.get_size()
        return prefix + self.name + " (" + str(length) + ", " + str(size) + ")"

    def to_json(self):
        res = "{'" + self.name + "': '" + str(self.length) + "', {"
        index = 0
        for k in r.hkeys(self.name):
            d = r.hget(self.name, k)
            res += "'" + k.decode('utf-8') + "': '" + json.loads(d) + "', '" if index is not self.length - 1 else ""
            index += 1
        return res + "}}"
