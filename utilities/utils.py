import datetime
import time
import hashlib
import sys
import pytz

class Utils:
    @staticmethod
    def get_current_time():
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timestamp = time.mktime(time.strptime(now, "%Y-%m-%d %H:%M:%S"))
        return int(timestamp), str(now)

    @staticmethod
    def to_datetime(unixtime):
        return datetime.datetime.fromtimestamp(unixtime, pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def to_hash(val):
        return hashlib.md5(val.encode('utf-8')).hexdigest() if val is not None else None

# 先入先出有序集合 (开发用)
class LinkSetQueue():
    """ FIFO linked set """

    def __init__(self):
        self.map = {}
        self.tail = "head"
        self.map["head"] = {"next": "null"}

    def __contains__(self, key):
        return key in self.map

    def __len__(self):
        return len(self.map) - 1

    def isEmpty(self):
        if self.getHead() == "null":
            return True
        else:
            return False

    def clear(self):
        self.map.clear()
        self.tail = "head"
        self.map["head"] = {"next": "null"}

    def getTail(self):
        return self.tail

    def getHead(self):
        return self.map["head"]["next"]

    def put(self, e):
        #      self.test_output("OrderedMapQueue")
        item = str(e)
        if item not in self.map:
            self.map[item] = {"next": "null"}
            self.map[self.tail]["next"] = item
            self.tail = item

    def get(self):
        if not self.isEmpty():
            head_task = self.map["head"]["next"]
            rt_value = "%s" % (head_task)
            self.map["head"]["next"] = self.map[head_task]["next"]
            del self.map[head_task]
            if head_task == self.tail:
                self.tail = "head"
            return int(rt_value)
        return None

    def test_output(self, name=""):
        print(sys.stderr, name)
        print(sys.stderr, "-" * 10 + "TEST_OUTPUT" + "-" * 10)
        print(sys.stderr, "Tail: %s\nHead: %s\nLength: %s" % (self.getTail(), self.getHead(), self.__len__()))
        head = "head"
        while head != "null":
            print(sys.stderr, "%s\t%s" % (head, self.map[head]["next"]))
            head = self.map[head]["next"]

    def show(self):
        res = '['
        head = "head"
        index = 0
        while head != "null":
            if index == len(self.map) - 1:
                res += head
            elif head != "null" and head != "head":
                res += head + ', '
            head = self.map[head]["next"]
            index += 1
        res += ']'
        print(res)