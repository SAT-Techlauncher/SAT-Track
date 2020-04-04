from server.services.es_io import SHD
from utilities.spyder import Spyder
from . import *


def fetch_satellite_info(id):
    print('fetch_satellite_info starts')

    res = {'name': 'NewStar-0' + str(id), 'long': 20.45, 'lat': 78.42, 'data': {}}

    if id == 25544:
        try:
            res = Spyder(id).parse()
        except:
            print('spyder error:', res)

    # 规定字段类型 (若不加设定, 则可能导致字段类型不一致错误)
    res = shd = SHD(
        res,
        id=SHD.Integer,
        name=SHD.String,
        long=SHD.Float,
        lat=SHD.Float
    ).harmonize()

    satellite = Satellite(
        id=id,
        name=res['name'],
        long=res['long'],
        lat=res['lat']
    )

    return satellite, shd