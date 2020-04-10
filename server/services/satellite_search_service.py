from utilities.sebapi import SHD
from . import *


def fetch_satellite_info(id):
    print('fetch_satellite_info starts')

    res = {'name': 'NewStar-0' + str(id), 'long': 20.45, 'lat': 78.42, 'data': {}}


    # 规定字段类型 (若不加设定, 则可能导致字段类型不一致错误)
    res = shd = SHD(
        res,
        id=SHD.Integer,
        name=SHD.String,
        long=SHD.Float,
        lat=SHD.Float
    ).harmonize()

    satellite = Satellite(res)

    return satellite, shd

def extract_user_input_info(any):

    lst = any.split(' ')

    return

def smart_search_satellite():
    ...