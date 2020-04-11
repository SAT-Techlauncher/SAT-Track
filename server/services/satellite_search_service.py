from utilities.doc_classifier import classify, CLASSIFIERS, SPLIT_CHARS, STOP_WORDS
from config import conf

# from utilities.sebapi import SHD
# from . import *
#
#
# def fetch_satellite_info(id):
#     print('fetch_satellite_info starts')
#
#     res = {'name': 'NewStar-0' + str(id), 'long': 20.45, 'lat': 78.42, 'data': {}}
#
#     # 规定字段类型 (若不加设定, 则可能导致字段类型不一致错误)
#     res = shd = SHD(
#         res,
#         id=SHD.Integer,
#         name=SHD.String,
#         long=SHD.Float,
#         lat=SHD.Float
#     ).harmonize()
#
#     satellite = Satellite(res)
#
#     return satellite, shd

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
        if word != '' and word not in STOP_WORDS:
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

    print('time = ', time.time() - start, '\n')

    classes = {classifier.__name__: [] for classifier in CLASSIFIERS}

    for word in ranks.keys():
        hits = ranks[word]

        for hit in hits:
            cls, rate = hit[0], hit[1]

            has_inserted = False
            for i in range(len(classes[cls])):
                if rate >= classes[cls][i][1]:
                    classes[cls].insert(i, (word, rate))
                    has_inserted = True
                    break

            if not has_inserted:
                classes[cls].append((word, rate))

    for k in classes.keys():
        print(k, ':', classes[k])

    return classes

def turn_to_query(classes):

    keyword = ''

    body = {
        'query': {
            'bool': {
                'should': [
                    {'match_phrase_prefix': {'name': keyword}},
                    {'match_phrase_prefix': {'intl_code': keyword}},
                    {'match_phrase_prefix': {'source': keyword}},
                ]
            }
        },
        'from': 0,
        'size': conf.ES_QUERY_MAX_SIZE
    }

    return body

def search_satellites_from_es():
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
    classes = extract_user_input_info('gps')
    search_body = turn_to_query(classes)

    # res = satellite_database.search(keyword)
    # print(len(res))
    # for sat in res:
    #     print(sat['name'], end=', ')



search_satellites_from_es()
