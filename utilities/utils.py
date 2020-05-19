import datetime
import time
import hashlib
import sys
import pytz
import math

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
    def to_unixtime(datetime, format='%Y-%m-%d'):
        return int(time.mktime(time.strptime(datetime, format)))

    @staticmethod
    def to_hash(val):
        return hashlib.md5(val.encode('utf-8')).hexdigest() if val is not None else None

    @staticmethod
    def to_all_unixtime(date):
        if date == '':
            return None
        base = datetime.datetime.strptime('1970-01-01 08:00:00', '%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.strptime(date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        return int((date - base).total_seconds())

    @staticmethod
    def to_all_datetime(unixtime, format='%Y-%m-%d'):
        base = datetime.datetime.strptime('1970-01-01 08:00:00', '%Y-%m-%d %H:%M:%S')
        date = datetime.datetime.fromtimestamp(abs(unixtime))
        delta = int((date - base).days) if unixtime > 0 else - int((date - base).days)
        return datetime.datetime.strftime(base + datetime.timedelta(days=delta, hours=-8), format)

class StrUtils:
    @staticmethod
    def __stringifiable(v):
        try:
            str(v)
            return True
        except:
            return False

    @staticmethod
    def isint(v):
        if not StrUtils.__stringifiable(v):
            return False

        s = str(v)

        if s.count('.') != 0:
            return False

        try:
            int(s)
            return True
        except:
            return False

    @staticmethod
    def isfloat(v):
        if StrUtils.isint(v):
            return False

        s = str(v)

        if s.count('.') == 0:
            return False

        try:
            float(s)
            return True
        except:
            return False

    @staticmethod
    def isrealnum(v):
        if StrUtils.isfloat(v) or StrUtils.isint(v):
            return True
        return False


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

# 近似等分数组
def approx_bisection(lst, slice_num=5, dynamic_min=5):
    slices = []
    length = len(lst)

    # 若数据条数大于最小设定值, 则执行分组; 否则, 不执行分组
    if length >= dynamic_min:
        # 近似等分数据
        for i in range(slice_num):
            ptr = math.floor(i / slice_num * length)
            ptr_ = math.floor((i + 1) / slice_num * length)
            slice = lst[ptr: ptr_]
            slices.append(slice)
    else:
        slices.append(lst)

    return slices