import urllib.request
import urllib.response
import re
import time
import json
import ephem

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
        return result[0]

from config import conf

with open(conf.RAW_DIR_ + 'satellites.json', 'r') as f:
    SATS = json.loads(f.read())
LEN = len(SATS)

def get_format_tles(start_idx=0, focus=None):
    satellites = SATS

    focus = range(1, LEN + 1) if focus is None else focus

    tles, excepts = [], []
    length, count = LEN, start_idx
    for satellite in satellites[start_idx:len(satellites)]:
        start = time.time()
        norad_id = satellite['norad_id']
        count += 1

        if satellite['tle'] == [] or int(norad_id) not in focus:
            continue
        try:
            tle = Spyder(str(norad_id)).parse()
            lines = tle.replace('\r', '').rstrip('\n').lstrip('\n').split('\n')
            dt = {str(norad_id): lines}
            tles.append(dt)
            with open(conf.RAW_DIR_ + 'format_tle.txt', 'a') as f:
                f.write(json.dumps(dt) + '\n')
            print(count, '/', length, end=', ')
        except:
            excepts.append(norad_id)
            with open(conf.RAW_DIR_ + 'format_tle_errors.txt', 'a') as f:
                f.write(json.dumps(norad_id) + '\n')
            print(excepts, end=', ')
        print('spends', time.time() - start, 's')

    print(count)
    print(len(tles))
    print(len(excepts))

def get_errors_from_tles():
    with open(conf.RAW_DIR_ + 'format_tle_errors.txt', 'r') as f:
        lines = f.readlines()

    errors = []
    for line in lines:
        errors.append(int(json.loads(line)))

    # satellites = SATS
    #
    # # check if non-errors exist in errors
    # for satellite in satellites:
    #     norad_id = int(satellite['norad_id'])
    #     tle = satellite['tle']
    #
    #     if norad_id in errors and tle == []:
    #         print(norad_id)

    get_format_tles(0, errors)

def get_tle_from_tles():
    satellites = SATS

    with open(conf.RAW_DIR_ + 'format_tle.txt', 'r') as f:
        lines = f.readlines()

    tles = {}
    for line in lines:
        tles.update(json.loads(line))

    new_satellites = []
    for satellite in satellites:
        norad_id = satellite['norad_id']
        tle = satellite['tle']

        satellite['tle'] = tles[str(norad_id)] if tle != [] else satellite['tle']
        new_satellites.append(satellite)

    with open(conf.RIPE_DIR_ + 'satellites.json', 'w') as f:
        f.write(json.dumps(new_satellites))

def check_new_satellites():
    with open(conf.RIPE_DIR_ + 'satellites.json', 'r') as f:
        satellites = json.loads(f.read())
    print(len(satellites))

    for satellite in satellites[0:20]:
        for sat in SATS:
            if satellite['norad_id'] == sat['norad_id'] and sat['tle'] != []:
                print(satellite['tle'])
                print(sat['tle'])
                line1 = satellite['name']
                line2 = satellite['tle'][0]
                line3 = satellite['tle'][1]
                iss = ephem.readtle(line1, line2, line3)
                iss.compute('2020/3/23')
                print('%s %s' % (iss.sublong, iss.sublat))

        print()



check_new_satellites()
