# encoding: utf-8
import requests
import math
import ephem
import json

from utilities.es_io import ES
from config import conf


def get_location_from_ip(ip):

    lat, long = __ip2location(ip)
    elev = __location2elevation(lat, long)

    return {
        'lat': lat,
        'long': long,
        'elev': elev
    }


def __ip2location(ip):
    url = conf.IPSTACK_API_URL % {'ip': ip, 'key': conf.IPSTACK_API_KEY}

    latitude, longitude = -35.2712287902832, 149.1183624267578

    try:
        response = requests.get(url)
        js = response.json()
        lat = js['latitude']
        long =js['longitude']
        if lat is not None and long is not None:
            return lat, long
    except:
        ...

    return latitude, longitude


def __location2elevation(lat, long):
    url = conf.GOOGLEMAP_API_URL % {'lat': str(lat), 'long': str(long), 'key': conf.GOOGLEMAP_API_KEY}

    try:
        response = requests.get(url).json()
        print(response)
        return response['results'][0]['elevation']
    except:
        return None

def get_tracking_info_from_es(sat_id, location):
    sat_db = ES(
        db='satellites',
        table='satellite',
        create=False
    )
    try:
        sat = sat_db.search_by_keyword('match', 'norad_id', sat_id)[0]
        az_alt_v = __calculate_by_tle(name=sat['name'], tle=sat['tle'], location=location)
        return az_alt_v
    except Exception as e:
        return {'az': None, 'alt': None, 'vel': None}


def __calculate_by_tle(name, tle, location):
    line1 = name
    line2 = tle[0]
    line3 = tle[1]
    me = ephem.Observer()
    me.lon, me.lat, me.elevation = location['lat'], location['long'], location['elev']
    sat = ephem.readtle(line1, line2, line3)
    me.date = ephem.now()
    sat.compute(me)

    az = sat.az * 180.0 / math.pi  # 卫星的方位角
    alt = sat.alt * 180.0 / math.pi  # 卫星的仰角
    vel = sat.range_velocity

    return {'az': az, 'alt': alt, 'vel': vel}
