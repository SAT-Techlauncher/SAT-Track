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

def generate_sources_from_raw_source_json():
    with open(RAW_TEXT_ + 'raw_source.txt', 'r') as f:
        lines = f.readlines()

    sources = {}
    for line in lines:
        abbrev = ''
        idx = 0
        while idx < len(line) and (line[idx].isalpha() or line[idx].isdigit()):
            s = line[idx]
            abbrev += s
            idx += 1

        fullname = line[idx: -1].lstrip().rstrip()

        sources.update({abbrev: fullname})
    print(sources)

    with open(RIPE_TEXT_ + 'source.json', 'w') as f:
        f.write(json.dumps(sources))

def upload_extracted_sats_to_es():
    with open(RIPE_TEXT_ + 'extracted_satellites.json', 'r') as file:
        sats = json.loads(file.read())

    satellites = []
    for id in sats:
        satellites.append({'norad_id': int(id), 'extracted': sats[id]})

    from utilities.sebapi import SHD
    shd = SHD(
        data=satellites,
        norad_id=SHD.Integer,
        extracted=SHD.String
    ).harmonize()

    from utilities.es_io import ES
    satellite_database = ES(
        db='satellites-extract',
        table='extract',
        create=True,
        norad_id={'type': 'keyword'},
        extracted={'type': 'text'}
    )
    satellite_database.concurrent_upload(
        id_field='norad_id',
        data=shd,
        concurrent_num=6
    )

    print('finished upload')

from utilities.sebapi import SOD

class Satellite(SOD):
    def __init__(self, dic, **kwargs):
        super().__init__(dic, **kwargs)

def to_standard_format(dic):
    for k in dic:
        if isinstance(dic[k], str):
            dic[k] = dic[k].lower()
    sat = Satellite(dic)

    id = sat.norad_id

    country_set = set()
    country_set.add(sat.source)
    country_set.add(SOURCES[sat.source.upper()].lower().replace(' ', '_'))

    for coun in COUNTRIES:
        country_set.add(coun['code_2'].lower())
        country_set.add(coun['code_3'].lower())
        country_set.add(coun['country'].lower().replace(' ', '_'))
        break

    source = ''
    for country in country_set:
        source += country + ' '
    source = source[0: len(source) - 1]

    from utilities.utils import Utils

    launch_date = sat.launch_date.replace('-', '_') + ' ' + str(Utils.to_all_unixtime(sat.launch_date))

    launch_site = ''
    for site in SITES:
        site_abbrev = list(site.keys())[0]
        site_fullname = list(site.values())[0]
        if sat.launch_site == site_abbrev.lower():
            launch_site = sat.launch_site + ' ' + site_fullname.lower().replace(' ', '_')
            break

    decay_date = '' if sat.decay_date == '' else sat.decay_date.replace('-', '_') + ' ' + str(Utils.to_all_unixtime(sat.decay_date))


    status = sat.status
    for stat in STATUS:
        status_abbrev = list(stat.keys())[0]
        status_fullname = list(stat.values())[0]
        for s in sat.status:
            if s == status_abbrev.lower():
                status += ' ' + status_fullname.lower()

    trackable = 'trackable' if sat.tle != [] else 'untrackable'

    data = sat.intl_code + ' ' + \
           sat.name.replace(' ', '_') + ' ' + \
           source + ' ' + launch_date + ' ' + \
           launch_site + ' ' + decay_date + ' ' + \
           status + ' ' + trackable

    return id, data

def generate_extracted_satellites_from_satellites_json():
    """
    id code      name       source                 country                               datetime   unixtime
    5  1958-002b vanguard_1 pres asia organization us usa united_states_of_america_(usa) 2020-04-13 23571113

    function
    gps global_...

    launch_site                                status   if_has_tle
    afetr air_force_eastern_test_range_(afetr) * active trackable

    {'intl_code': '1958-002B', 'tle': [], 'norad_id': 5, 'status': '*', 'name': 'VANGUARD 1', 'source': 'US', 'launch_date': '1958-03-17', 'launch_site': 'AFETR', 'decay_date': '', '_0_': 132.7, '_1_': 34.3, '_2_': 3834, '_3_': 649, '_4_': 0.122}
    """
    dic = {}
    for sat in SATS:
        sat_id, satellite = to_standard_format(sat)
        dic.update({sat_id: satellite})
        print(satellite)

    with open(RIPE_TEXT_ + 'extracted_satellites.json', 'w') as f:
        f.write(json.dumps(dic))


with open(RAW_TEXT_ + 'satellites.json', 'r') as f:
    SATS = json.loads(f.read())
with open(RAW_TEXT_ + 'iso_country_code.json', 'r') as f:
    COUNTRIES = json.loads(f.read())
with open(RAW_TEXT_ + 'launch_sites.json', 'r') as f:
    SITES = json.loads(f.read())
with open(RAW_TEXT_ + 'status.json', 'r') as f:
    STATUS = json.loads(f.read())
with open(RAW_TEXT_ + 'source.json', 'r') as f:
    SOURCES = json.loads(f.read())

