import json
import difflib
import numpy as np
import math

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


RAW_TEXT_ = '../data/'
RIPE_TEXT_ = '../data/lib/'

def generate_country_json_from_iso_country_code():
    with open(RAW_TEXT_ + 'iso_country_code.json') as f:
        iso_country_code = json.loads(f.read())

    abbrevs = {}
    iso_codes = {}
    countries = {}
    for iso in iso_country_code:
        if iso['code_2'] == 'CN':
            abbrevs.update({'prc': ''})

        abbrevs.update({iso['code_2'].lower(): '', iso['code_3'].lower(): ''})
        iso_codes.update({iso['iso_code'].lower(): ''})
        countries.update({iso['country'].lower(): ''})

        print(iso['country'], iso['code_2'], iso['code_3'])

    with open(RIPE_TEXT_ + 'countries_abbrev.json', 'w') as f:
        f.write(json.dumps(abbrevs))
    with open(RIPE_TEXT_ + 'countries_iso_code.json', 'w') as f:
        f.write(json.dumps(iso_codes))
    with open(RIPE_TEXT_ + 'countries_fullname.json', 'w') as f:
        f.write(json.dumps(countries))

def generate_countries_words_json_from_fullname_json():
    with open(RIPE_TEXT_ + 'countries_fullname.json', 'r') as f:
        countries = json.loads(f.read())

    country_words, counts = [], {}
    for country in countries.keys():
        words = country.split(' ')
        country_words.extend(words)
        for word in words:
            counts[word] = 1 if word not in counts else counts[word] + 1

    ws = list()
    max_val, min_val = -100, 100
    for count in counts.values():
        quality = 1 / len(counts.keys())
        quatify = count / sum(counts.values())
        w = round(quality / quatify, 4)
        max_val = w if max_val < w else max_val
        min_val = w if min_val > w else min_val
        ws.append(w)

    weights = {}
    words = list(counts.keys())
    for i in range(len(words)):
        weights[words[i]] = round((ws[i] - min_val) / (max_val - min_val), 4)

    with open(RIPE_TEXT_ + 'countries_words.json', 'w') as f:
        f.write(json.dumps(weights))

def calculate_characters_distribution_for_codes():
    with open(RAW_TEXT_ + 'iso_country_code.json', 'r') as f:
        satellites = json.loads(f.read())

    digit_counts, alpha_counts, sign_counts = 0, 0, 0
    digit_dists, alpha_dists, sign_dists = [], [], []

    for satellite in satellites:
        intl_code = satellite['intl_code']
        digit_idxs, alpha_idxs, sign_idxs = 0, 0, 0
        avg_idx = (len(intl_code) - 1) / 2

        for idx in range(len(intl_code)):
            s = intl_code[idx]

            if s.isdigit():
                digit_counts += 1
                digit_idxs += (idx - avg_idx) * 1
            elif s.isalpha():
                alpha_counts += 1
                alpha_idxs += (idx - avg_idx) * 1
            else:
                sign_counts += 1
                sign_idxs += (idx - avg_idx) * 1

        digit_dists.append(round(math.sqrt(digit_idxs / len(intl_code)), 4) if digit_idxs > 0 else
                           round(- math.sqrt(- digit_idxs / len(intl_code)), 4))
        alpha_dists.append(round(math.sqrt(alpha_idxs / len(intl_code)), 4) if alpha_idxs > 0 else
                           round(- math.sqrt(- alpha_idxs / len(intl_code)), 4))
        sign_dists.append(round(math.sqrt(sign_idxs / len(intl_code)), 4) if sign_idxs > 0 else
                          round(- math.sqrt(- sign_idxs / len(intl_code)), 4))

    char_total = digit_counts + alpha_counts + sign_counts
    digit_rate = round(digit_counts / char_total, 4)
    alpha_rate = round(alpha_counts / char_total, 4)
    sign_rate = round(sign_counts / char_total, 4)

    print('characteristic total =', char_total)
    print('frequency(c) =', digit_rate, alpha_rate, sign_rate)

    gen_total = len(satellites)
    digit_dist = round(sum(digit_dists) / gen_total, 4)
    alpha_dist = round(sum(alpha_dists) / gen_total, 4)
    sign_dist = round(sum(sign_dists) / gen_total, 4)

    print('general total =', gen_total)
    print('distribution(c) =', digit_dist, alpha_dist, sign_dist)

    print(min(digit_dists), '~', max(digit_dists), ';', min(alpha_dists), '~', max(alpha_dists), ';', min(sign_dists), '~', max(sign_dists))

def edit_distance(word1, word2):
    len1 = len(word1)
    len2 = len(word2)
    dp = np.zeros((len1 + 1, len2 + 1))
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            delta = 0 if word1[i - 1] == word2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + delta, min(dp[i - 1][j] + 1, dp[i][j - 1] + 1))
    return dp[len1][len2]

def edit_distance_prox(str1, str2):
    length = len(str1) if len(str1) > len(str2) else len(str2)
    return round(1 - edit_distance(str1, str2) / length, 2)

def str_prox(str1, str2):
    return round(difflib.SequenceMatcher(None, str1, str2).quick_ratio(), 2)

def max_prox(cmp, o, lst, weights=None):
    weights = [1.0 for _ in lst] if weights is None else weights
    prox, index = 0.0, 0
    for i in range(len(lst)):
        tmp = cmp(o, lst[i]) * weights[i]
        (prox, index) = (tmp, i) if tmp > prox else (prox, index)
    return prox, index


def is_number(word, **ranks):
    if str(word).isdigit():
        if len(word) - 1 > len(str(int(word))):
            return 0.7
        return 0.5
    return 0

def is_unknown(word, **ranks):
    if word.isdigit():
        return True

    return False

def is_year(word, **ranks):
    if word.isdigit():
        if 1957 <= int(word) <= 2020:
            return 0.7
        if 57 <= int(word) <= 99 or 10 <= int(word) <= 20:
            return 0.3
        if 1 <= int(word) <= 20:
            return 0.1

    return 0

def is_month(word, **ranks):
    if word.isdigit() and len(word) < 3 and 1 <= int(word) <= 12:
        return 0.5

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    prox = []
    for m in months:
        month = m.lower()
        if word == month:
            return 0.9
        elif word in month:
            return 0.7
        else:
            prox.append(str_prox(word, month) * edit_distance_prox(word, month))

    return round(max(prox), 4)

def is_day(word, **ranks):
    if word.isdigit() and 1 <= int(word) <= 31 and len(word) <= 2:
        return 0.8
    return 0

def is_verb(word, **ranks):
    if word.isdigit():
        return 0

    prox, idx = max_prox(str_prox, word, verbs)
    return prox * round(edit_distance_prox(word, verbs[idx]), 4)

def is_adjective(word, **ranks):
    if word.isdigit():
        return 0

    prox, idx = max_prox(str_prox, word, adjectives)
    return prox * round(edit_distance_prox(word, adjectives[idx]), 4)

with open(RIPE_TEXT_ + 'countries_abbrev.json', 'r') as f:
    COUNTRIES_ABBREV = json.loads(f.read())
with open(RIPE_TEXT_ + 'countries_iso_code.json', 'r') as f:
    COUNTRIES_ISO_CODE = json.loads(f.read())
with open(RIPE_TEXT_ + 'countries_words.json', 'r', encoding='unicode_escape') as f:
    COUNTRIES_WORDS = json.loads(f.read())
with open(RIPE_TEXT_ + 'countries_fullname.json', 'r', encoding='unicode_escape') as f:
    COUNTRIES_NAMES = json.loads(f.read())

def is_country(word, **ranks):
    if word.isdigit():
        return 0.01

    full_name_prox = 0
    # fullnames = list(COUNTRIES_NAMES.keys())
    # str_name_prox, str_name_idx = max_prox(str_prox, word, list(fullnames))
    # edit_name_prox, edit_name_idx = max_prox(edit_distance_prox, word, list(fullnames))
    # full_name_prox = (str_name_prox + edit_name_prox) / 2

    abbrevs = list(COUNTRIES_ABBREV.keys())
    if word in abbrevs:
        return 0.6

    iso_codes = list(COUNTRIES_ISO_CODE.keys())
    iso_prox, iso_idx = max_prox(str_prox, word, list(iso_codes))

    fullname_words, weights = COUNTRIES_WORDS.keys(), COUNTRIES_WORDS.values()
    fullname_prox, fullname_idx = max_prox(str_prox, word, list(fullname_words), list(weights))

    iso = iso_codes[iso_idx]
    fullname = list(fullname_words)[fullname_idx]

    iso_w_prox = round(iso_prox * edit_distance_prox(word, iso), 4)
    fullname_w_prox = round(fullname_prox, 4)

    return max([fullname_w_prox, iso_w_prox, full_name_prox])

DIGIT_RATE, ALPHA_RATE, SIGN_RATE = 0.7357, 0.1591, 0.1051
DIGIT_DIST_RANGE, ALPHA_DIST_RANGE, SIGN_DIST_RANGE = [-1.0, -0.6667], [0.6667, 1.0445], [-0.3015, 0.0]

def intl_code_sim(word, **ranks):
    digit_counts, alpha_counts, sign_counts = 0, 0, 0
    digit_idxs, alpha_idxs, sign_idxs = 0, 0, 0
    avg_idx = (len(word) - 1) / 2

    for idx in range(len(word)):
        s = word[idx]

        if s.isdigit():
            digit_counts += 1
            digit_idxs += (idx - avg_idx) * 1
        elif s.isalpha():
            alpha_counts += 1
            alpha_idxs += (idx - avg_idx) * 1
        else:
            sign_counts += 1
            sign_idxs += (idx - avg_idx) * 1

    char_total = digit_counts + alpha_counts + sign_counts
    digit_rate = round(digit_counts / char_total, 4)
    alpha_rate = round(alpha_counts / char_total, 4)
    sign_rate = round(sign_counts / char_total, 4)

    # print('frequency(c) =', digit_rate, alpha_rate, sign_rate)

    digit_dist = round(math.sqrt(digit_idxs / len(word)), 4) if digit_idxs > 0 else round(- math.sqrt(- digit_idxs / len(word)), 4)
    alpha_dist = round(math.sqrt(alpha_idxs / len(word)), 4) if alpha_idxs > 0 else round(- math.sqrt(- alpha_idxs / len(word)), 4)
    sign_dist = round(math.sqrt(sign_idxs / len(word)), 4) if sign_idxs > 0 else round(- math.sqrt(- sign_idxs / len(word)), 4)

    # print('distribution(c) =', digit_dist, alpha_dist, sign_dist)

    digit_d_rate, alpha_d_rate, sign_d_rate = abs(digit_rate - DIGIT_RATE), abs(alpha_rate - ALPHA_RATE), abs(sign_rate - SIGN_RATE)
    freq_sim = 1 - (digit_rate * digit_d_rate + alpha_rate * alpha_d_rate + sign_rate * sign_d_rate)
    # print('freq_sim =', freq_sim)

    mid_dists = [sum(DIGIT_DIST_RANGE) / 2, sum(ALPHA_DIST_RANGE) / 2, sum(SIGN_DIST_RANGE) / 2]
    digit_d_dist, alpha_d_dist, sign_d_dist = abs(digit_dist - mid_dists[0]), abs(alpha_dist - mid_dists[1]), abs(sign_dist - mid_dists[2])
    dist_sim = 1 - (digit_rate * digit_d_dist + alpha_rate * alpha_dist + sign_rate * sign_dist) / avg_idx
    # print('dist_sim =', dist_sim)

    return round(freq_sim * dist_sim, 4)

def is_intl_code(word, **ranks):
    if 8 <= len(word) <= 12 and '-' in word:
        return intl_code_sim(word)
    return 0

def is_date(words, **ranks):
    if len(words.split(' ')) < 2 or ranks == {}:
        return 0

    proximity = 0
    for word in words.split(' '):
        cls, rate = list(ranks[word].keys())[0], list(ranks[word].values())[0]
        if cls == is_year.__name__:
            proximity += 0.45 * rate
        elif cls == is_month.__name__:
            proximity += 0.35 * rate
        elif cls == is_day.__name__:
            proximity += 0.2 * rate
        else:
            proximity += -1 * rate

    if proximity <= 0:
        return 0

    # print(words, '=' * (20 - len(words) + 3) + '>', round(proximity, 4), day_prox, ranks)
    return round(proximity, 4)

def is_phrase(words, **ranks):
    noun_prox, verb_prox = 0, 0
    return 0

def is_sentence(words, **ranks):
    sub_prox, pred_prox, obj_prox = 0, 0, 0
    attr_prox, adv_prox, com_prox = 0, 0, 0
    return 0

CLASSIFIER = [is_country, is_day, is_month, is_year, is_intl_code, is_number, is_date]

def classify(word, ranks):
    classifiers = CLASSIFIER
    proximity = {}
    for classifier in classifiers:
        proximity.update({classifier.__name__: 0})
    assert len(classifiers) == len(proximity)

    lst = []
    for classifier in classifiers:
        lst.append(classifier(word, **ranks))

    cls = {}
    max_val = max(lst)
    idx = 0
    for k in proximity.keys():
        proximity[k] = lst[idx]
        cls.update({k: max_val})
        idx += 1
    print(cls)

    return proximity, cls

adjectives = ['active', 'inactive', 'operational', 'nonoperational', 'partially_operational', 'backup',
              'standby', 'spare', 'extended_mission', 'decayed', 'unknown',
              'current', 'recent', 'past',
              'on_orbit', 'off_orbit']
verbs = ['launch', 'decay']
adverbs = ['not', 'and', 'or', 'either', 'neither', 'nor', 'on', 'off', 'in', 'during', 'out', 'from', 'for']

with open(RIPE_TEXT_ + 'stop_words.json', 'r') as f:
    stop_words = STOP_WORDS = json.loads(f.read())

SPLIT_CHARS = {".", "/", ","}

def extract_user_input_info(any):
    print(any, '\n')

    preprocessed = ''
    for s in any:
        if s not in SPLIT_CHARS:
            preprocessed += s
        else:
            preprocessed += ' '

    words = []
    for word in preprocessed.split(' '):
        if word != '' and word not in stop_words:
            words.append(word)

    length = len(words)
    print(words, '\n')

    doc = []
    res = []
    for i in range(length):
        lst = []
        for j in range(length - i):
            text = ''
            for char in words[j:j+i+1]:
                text += char.lower() + ' '
            lst.append(text.rstrip(' '))
            res.append(words[j:j+i+1])
        doc.append(lst)

    rates = {}
    hits = {}
    for cls in CLASSIFIER:
        rates[cls.__name__] = 0
        hits[cls.__name__] = '_'

    ranks = {}
    for line in doc:
        for word in line:
            proximity, classes = classify(word, ranks)
            cls = list(classes.keys())[0]
            prox = classes[cls]

            print(word, '=' * (len(max(line)) - len(word) + 3) + '>', classes, proximity)

            if prox > 0.4:
                if prox > rates[cls]:
                    rates[cls] = prox
                    hits[cls] = word

            for c in classes:
                ranks.update({word: {c: proximity[c]}})

        print()

    return 0

def es_search():
    from utilities.es_io import ES

    satellite_database = ES(
        db='satellites',
        table='satellite',
        create=False
    )

    '''
    1958-002b from US
    the satellite that launched in 17th mar, 1958
    '''
    keyword = extract_user_input_info('chinese satellite in mar 3 1997')
    # res = satellite_database.search(keyword)
    # print(len(res))
    # for sat in res:   ffffttgf  fffffffffff
    #     print(sat['name'], end=', ')

    '''
    5 1958-002b vanguard_1 us usa united_states_of_america_(usa) 1958-03-17 march
     afetr air_force_eastern_test_range_(afetr) * active trackable
    '''

    #

es_search()

# if __name__ == '__main__':
#     generate_satsjson_from_satinfottle()
#     upload_satjson_to_es()


