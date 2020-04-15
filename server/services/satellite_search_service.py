from utilities.doc_classifier import classify, CLASSIFIERS, SPLIT_CHARS, STOP_WORDS
from config import conf

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
    print(any, '\n')

    preprocessed = ''
    for s in any:
        if s not in SPLIT_CHARS:
            preprocessed += s
        else:
            preprocessed += ' '

    words = []
    for word in preprocessed.split(' '):
        try:
            word = STOP_WORDS[word]
        except:
            ...

        if word != '':
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

    import time
    start = time.time()
    ranks = {}
    for line in doc:
        for word in line:
            word = word if '_' not in word else word.split('_')[0]
            proximity, cls = classify(word, ranks)
            ranks.update({word: cls})
            print(word, '=' * (len(max(line)) - len(word) + 3) + '>', proximity)
        print()

    print('time = ', time.time() - start, '\n')

    classes = {classifier.__name__: [] for classifier in CLASSIFIERS}

    for word in ranks.keys():
        hits = ranks[word]

        for hit in hits:
            cls, rate = hit[0], hit[1]

            if rate < 0.5:
                continue

            has_inserted = False
            for i in range(len(classes[cls])):
                if rate >= classes[cls][i][1]:
                    classes[cls].insert(i, (word, rate))
                    has_inserted = True
                    break

            if not has_inserted:
                classes[cls].append((word, rate))

    res = {}
    for k in classes.keys():
        if classes[k] == []:
            continue
        res.update({k: classes[k]})

    return res

def turn_to_query_body(classes, user_input):
    should = []
    # for k in classes.keys():
    #     print('{' + str(k) + ': ' + str(classes[k]) + '}')
    #     if k == 'is_number' or k == 'is_year' or k == 'is_month' or k == 'is_day':
    #         should.append({'match': {'norad_id': classes[k][0]}})
    should.append({'match': {'extracted': user_input}})

    body = {
        'query': {
            'bool': {
                'should': should
            }
        },
        'from': 0,
        'size': conf.ES_QUERY_MAX_SIZE
    }

    return body

def search_satellites_from_es():
    from utilities.es_io import ES

    satellite_database = ES(
        db='satellites-extract',
        table='extract',
        create=False
    )

    '''
    1958-002b from US
    the satellite that us launched in 17th mar, 1958
    '''
    user_input = '17th mar, 1958 us'
    classes = extract_user_input_info(user_input)
    search_body = turn_to_query_body(classes, user_input)

    res = satellite_database.search_by_body(search_body)

    if res == []:
        return None

    import json
    with open('../../data/satellites.json', 'r') as f:
        satellites = json.loads(f.read())
    for sat in satellites:
        if sat['norad_id'] == res[0]['norad_id']:
            return sat

    # print(len(res))
    # for sat in res:
    #     print(sat['extracted'][0:30], end=';    ')


# search_satellites_from_es()
