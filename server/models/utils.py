import datetime
import time

class Utils:
    @staticmethod
    def get_current_unixtime():
        return time.mktime(datetime.datetime.now().timetuple())