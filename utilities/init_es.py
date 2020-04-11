import json

RAW_TEXT_ = '../data/'
RIPE_TEXT_ = '../data/lib/'

def generate_satsjson_from_satinfottle():
    with open('../data/sattle.json', 'r') as file:
        tles = json.loads(file.read())

    with open('../data/satinfo.json', 'r') as file:
        sats = json.loads(file.read())

    head_sats = ['intl_code', 'norad_id',
                 'status', 'name',
                 'source', 'launch_date',
                 'launch_site', 'decay_date'] + \
                ['_' + str(i) + '_' for i in range(5)]

    head_tles = ['norad_id', 'tle']

    tles_num = 0
    tles_dic = {}
    for tle in tles:
        tles_num += 1
        print(tles_num, '/', len(tles))
        dic = {}
        idx = 0
        for k in tle.keys():
            dic[head_tles[idx]] = tle[k]
            idx += 1
        tles_dic[tle['NORAD ID']] = dic

    sats_num = 0
    sats_dic = {}
    for sat in sats:
        sats_num += 1
        print(sats_num, '/', len(sats_dic))
        dic = {}
        idx = 0
        for k in sat.keys():
            dic[head_sats[idx]] = sat[k]
            idx += 1
            dic.update({'tle': []})
            sats_dic[sat['NORAD ID']] = dic

    trackables = list(set(sats_dic.keys()).intersection(set(tles_dic.keys())))

    track_num = 0
    for norad_id in trackables:
        track_num += 1
        print(track_num, '/', len(trackables))
        sats_dic[norad_id]['tle'] = tles_dic[norad_id]['tle']

    print(len(sats_dic))

    satellites = list(sats_dic.values())

    with open('../data/satellites.json', 'w') as file:
        file.write(json.dumps(satellites))

    print('finished write')

def upload_satjson_to_es():
    with open('../data/satellites.json', 'r') as file:
        sats = json.loads(file.read())

    na = 0
    print(len(sats))
    satellites = []
    template = ['_' + str(i) + '_' for i in range(5)]

    from utilities.utils import Utils

    countries = set()
    for sat in sats:
        countries.add(sat['source'])

        sat['launch_date'] = Utils.to_all_unixtime(sat['launch_date'])
        sat['decay_date'] = Utils.to_all_unixtime(sat['decay_date']) if sat['decay_date'] != '' else ''

        for k in template:
            if sat[k] == '':
                sat[k] = ''

        if sat['_4_'] == 'N/A':
            na += 1
            sat['_4_'] = ''
        else:
            sat['_4_'] = float(sat['_4_'])
        satellites.append(sat)

    print('na', na)
    print(len(satellites), countries)

    from utilities.es_io import ES
    from utilities.sebapi import SHD

    '''
    {"intl_code": "1958-002B", "tle": 
        ["1", "5U", "58002B", "20094.40380137", "+.00000161", "+00000-0", "+21977-3", "0", "9998", 
         "2", "5", "034.2452", "099.5269", "1847031", "014.5693", "350.1537", "10.84830151197102"], 
     "norad_id": 5, "status": "*", "name": "VANGUARD 1", "source": "US", "launch_date": "1958-03-17",
     "launch_site": "AFETR", "decay_date": "", "_0_": 132.7, "_1_": 34.3, "_2_": 3834, "_3_": 649, "_4_": 0.122}
    '''

    shd = SHD(
        data=satellites,
        intl_code=SHD.String,
        norad_id=SHD.Integer,
        launch_date=SHD.Integer,
        decay_date=SHD.Integer,
        _0_=SHD.Float,
        _1_=SHD.Float,
        _2_=SHD.Float,
        _3_=SHD.Float,
        _4_=SHD.Float,
    ).harmonize()

    # satellite_database = ES(
    #     db='satellites',
    #     table='satellite',
    #     create=True,
    #     norad_id={'type': 'keyword'},
    #     intl_code={'type': 'keyword'},
    #     source={'type': 'keyword'},
    #     status={'type': 'keyword'},
    #     launch_date={'type': 'long', 'ignore_malformed': False, 'null_value': None},
    #     decay_date={'type': 'long', 'ignore_malformed': True, 'null_value': None},
    #     _0_={'type': 'float', "null_value": None},
    #     _1_={'type': 'float', "null_value": None},
    #     _2_={'type': 'float', "null_value": None},
    #     _3_={'type': 'float', "null_value": None},
    #     _4_={'type': 'float', "null_value": None},
    # )
    # satellite_database.concurrent_upload(
    #     id_field='norad_id',
    #     data=shd,
    #     concurrent_num=6
    # )

    print('finished upload')

'''
id code      name       country                               unixtime launch_site                                status   if_has_tle
5  1958-002b vanguard_1 us usa united_states_of_america_(usa) 23571113 afetr air_force_eastern_test_range_(afetr) * active trackable
'''

# if __name__ == '__main__':
#     generate_satsjson_from_satinfottle()
#     upload_satjson_to_es()

