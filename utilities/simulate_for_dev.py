class Simulation:
    @staticmethod
    def init_db(user_id, user_info_pool, satellite_database):
        priority = [
            {"id": "#000", "name": "GPS-xxx", "active": False, "executing": False},
            {"id": "#002", "name": "SATELLITE", "active": True, "executing": False},
            {"id": "#003", "name": "SEBASTIAN-2020", "active": False, "executing": False},
            {"id": "#001", "name": "BEI-DOU", "active": True, "executing": False}
        ]
        origin = user_info_pool.get(user_id)
        origin['priority'] = priority
        user_info_pool.set(user_id, origin)

        satellite_database.set('#000', {'name': 'GPS-xxx', 'long': 0, 'lat': 0, 'data': 'GPS-data'})
        satellite_database.set('#001', {'name': 'BEI-DOU', 'long': 10, 'lat': 10, 'data': 'BEI-data'})
        satellite_database.set('#002', {'name': 'SATELLITE', 'long': -20, 'lat': 20, 'data': 'SAT-data'})
        satellite_database.set('#003', {'name': 'SEBASTIAN-2020', 'long': -30, 'lat': 30, 'data': 'Seb-data'})

    @staticmethod
    def get_from_db(pool, id):
        pool.get(id)

from utilities.sebapi import SOD

class Satellite(SOD):
    def __init__(self, dic, **kwargs):
        super().__init__(dic, **kwargs)

class TLE(SOD):
    def __init__(self, dic, **kwargs):
        super().__init__(dic, **kwargs)

import json

with open('../data/sattle.json', 'r') as file:
    tles = json.loads(file.read())

with open('../data/satinfo.json', 'r') as file:
    sats = json.loads(file.read())

print(len(tles) / len(sats))

print(tles[0:5])
print(sats[0:5])

print(len(tles), len(sats))

head_tles = ['intl_code', 'norad_id',
             'status', 'name',
             'source', 'launch_date',
             'launch_site', 'decay_date'] + \
            ['_' + str(i) + '_' for i in range(5)]

head_sats = ['norad_id', 'tle']
