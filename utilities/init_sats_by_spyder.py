# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 17:27:48 2020

@author: HP
"""

import urllib.request
import urllib.response
import re
import json

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

URL = 'http://doc.chacuo.net/iso-3166-1'
RAW_DIR = '../data/raw_iso_country_code.html'
RIPE_DIR = '../data/iso_country_code.json'

class Code:
    def __init__(self, code_2, code_3, number, iso_code, country):
        self.code_2 = code_2
        self.code_3 = code_3
        self.number = number
        self.iso_code = iso_code
        self.country = country

    def __str__(self):
        res = ''
        res += str(self.code_2) + ', '
        res += str(self.code_3) + ', '
        res += str(self.number) + ', '
        res += str(self.iso_code) + ', '
        res += str(self.country)
        return res

    def keys(self):
        return ('code_2', 'code_3', 'number', 'iso_code', 'country')

    def __getitem__(self, item):
        return getattr(self, item)

def get_iso_country_codes(manually=True):
    if not manually:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

        url = URL

        r = requests.get(url=url, headers=headers)
        html = r.content.decode('utf-8')
    else:
        with open(RAW_DIR, 'r', encoding='utf-8') as f:
            html = f.read()

    soup = bs(html, 'html.parser')
    raw_codes = soup.find_all('tr')
    codes = []

    for raw_code in raw_codes:
        tds = raw_code.find_all('td')

        try:
            code_2 = tds[0].text
            code_3 = tds[1].text
            number = tds[2].text
            iso_code = tds[3].text
            country = tds[4].text

            code = Code(code_2, code_3, number, iso_code, country)
            codes.append(code)
        except:
            continue

    lst = []
    for code in codes:
        lst.append(dict(code))

    with open(RIPE_DIR, 'w') as file:
        file.write(json.dumps(lst))


from bs4 import BeautifulSoup as bs
import requests
import json

URL = 'https://celestrak.com/satcat/maps/map' + '^_^' + '.php'
URL_ = 'https://www.celestrak.com/satcat/launchsites.php'
INDEX_DIR = '../data/satellites.json'
RIPE_DIR = '../data/launch_sites.json'

def get_launch_sites():
    with open(INDEX_DIR, 'r') as file:
        satellites = json.loads(file.read())

    launch_sites = set()
    for satellite in satellites:
        launch_sites.add(satellite['launch_site'])

    lst = []
    for site in launch_sites:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            url = URL.replace('^_^', site)
            r = requests.get(url=url, headers=headers)
            html = r.content.decode('utf-8')

            soup = bs(html, 'html.parser')
            launch_site = soup.find_all('h2')[0].text
            lst.append({site: str(launch_site)})
            print(site, launch_site)
        except:
            print('error', site)

    with open(RIPE_DIR, 'w') as file:
        file.write(json.dumps(lst))

'''
WSC Wenchang Satellite Launch Center
SUBL Submarine Launch Platform (mobile)
WRAS Western Range Airspace
ERAS Eastern Range Airspace
'''

RIPE_DIR = '../data/status.json'
STATUS = [
    '+  Operational',
    '-  Nonoperational',
    'P  Partially Operational',
    'B  Backup/Standby',
    'S  Spare',
    'X  Extended Mission',
    'D  Decayed',
    '?  Unknown',
    '*  Active'
    ]

def get_status():
    status = STATUS

    lst = []
    for stat in status:
        kv = stat.split('  ')
        k, v = kv[0], kv[1]
        lst.append({k: v})

    with open(RIPE_DIR, 'w') as file:
        file.write(json.dumps(lst))
