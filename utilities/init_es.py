import json

RAW_TEXT_ = '../data/'
RIPE_TEXT_ = '../data/lib/'

from utilities.sebapi import SOD

class Satellite(SOD):
    def __init__(self, dic, **kwargs):
        super().__init__(dic, **kwargs)

def generate_satellites_json_from_satinfottle():
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

def upload_sats_to_es():
    sats = SATS
    with open(RIPE_TEXT_ + 'extracts.json', 'r') as f:
        extracts = json.loads(f.read())

    from utilities.utils import Utils

    templates = ['_' + str(i) + '_' for i in range(5)]
    satellites = []
    keys = [
        'intl_code', 'norad_id', 'name', 'source', 'launch_date', 'decay_date', 'launch_unixtime', 'decay_unixtime',
        'launch_site', 'status', 'extract', 'tle'
    ]

    for sat in sats:
        for k in sat.keys():
            if isinstance(sat[k], str):
                sat[k] = sat[k].lower()
        for i in range(len(templates)):
            sat.pop(templates[i])
        sat.update({'launch_unixtime': Utils.to_all_unixtime(sat['launch_date'])})
        sat.update({'decay_unixtime': Utils.to_all_unixtime(sat['decay_date'])})
        sat.update({'extract': extracts[str(sat['norad_id'])]})

        satellite = {}
        for key in keys:
            satellite.update({key: sat[key]})

        satellites.append(satellite)

    from utilities.es_io import ES
    from utilities.sebapi import SHD

    shd = SHD(
        data=satellites,
        intl_code=SHD.String,
        norad_id=SHD.Integer,
        name=SHD.String,
        launch_date=SHD.String,
        launch_unixtime=SHD.Integer,
        decay_date=SHD.String,
        decay_unixtime=SHD.Integer
    ).harmonize()

    print(len(shd))

    satellite_database = ES(
        db='satellites',
        table='satellite',
        create=True,
        norad_id={'type': 'keyword'},
        intl_code={'type': 'keyword'},
        source={'type': 'keyword'},
        status={'type': 'keyword'},
        launch_unixtime={'type': 'long', 'ignore_malformed': False, 'null_value': None},
        decay_unixtime={'type': 'long', 'ignore_malformed': True, 'null_value': None},
        extract={'type': 'text'}
    )
    satellite_database.concurrent_upload(
        id_field='norad_id',
        data=shd,
        concurrent_num=6
    )

    print('finished upload')

def to_extract_format(dic):
    for k in dic:
        if isinstance(dic[k], str):
            dic[k] = dic[k].lower()
    sat = Satellite(dic)

    id = sat.norad_id

    source = sat.source + ';'
    for s in SRC_COUN_MAPPING[sat.source]:
        source += s + ' '
    source = source.replace(';', ' ')

    launch_site = ''
    for site in SITES:
        site_abbrev = list(site.keys())[0]
        site_fullname = list(site.values())[0]
        if sat.launch_site == site_abbrev.lower():
            launch_site = ' ' + sat.launch_site + '  ' + site_fullname.lower()
            break

    status = sat.status
    for stat in STATUS:
        status_abbrev = list(stat.keys())[0]
        status_fullname = list(stat.values())[0]
        for s in sat.status:
            if s == status_abbrev.lower():
                status += ' ' + status_fullname.lower()

    group = ''
    if str(id) in SAT_GROUP_MAPPING:
        group += ' ' + SAT_GROUP_MAPPING[str(id)].lower()

    trackable = 'trackable' if sat.tle != [] else 'untrackable'

    data = sat.name + ' | ' + \
           source + ' | ' + \
           launch_site + ' | ' + \
           group + ' | ' + \
           status + ' | ' + trackable

    return id, data

def generate_extracts_from_satellites_json():
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
    idx = 0
    for sat in SATS:
        sat_id, satellite = to_extract_format(sat)
        dic.update({sat_id: satellite})
        idx += 1
        print(idx, '/', len(SATS))

    with open(RIPE_TEXT_ + 'extracts.json', 'w') as f:
        f.write(json.dumps(dic))


with open(RIPE_TEXT_ + 'satellites.json', 'r') as f:
    SATS = json.loads(f.read())
with open(RAW_TEXT_ + 'launch_sites.json', 'r') as f:
    SITES = json.loads(f.read())
with open(RAW_TEXT_ + 'status.json', 'r') as f:
    STATUS = json.loads(f.read())
with open(RIPE_TEXT_ + 'sources_countries_mapping.json', 'r') as f:
    SRC_COUN_MAPPING = json.loads(f.read())
with open(RIPE_TEXT_ + 'satellites_groups_mapping.json', 'r') as f:
    SAT_GROUP_MAPPING = json.loads(f.read())


# if __name__ == '__main__':
#     generate_extracts_from_satellites_json()
#     upload_sats_to_es()
