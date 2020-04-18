from utilities.doc_classifier import classify, CLASSIFIERS, SPLIT_CHARS, STOP_WORDS
from . import *

def extract_user_input_info(any):

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
        #     print(word, '=' * (len(max(line)) - len(word) + 3) + '>', proximity)
        # print()

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

    # print('time = ', time.time() - start, '\n')

    return res

def to_date(classes):
    raw_date = classes['is_date'][0][0].split(' ')

    date_classes = {}
    for cls, hit in classes.items():
        if cls == 'is_year' or cls == 'is_day' or cls == 'is_month':
            date_classes.update({cls: hit})

    months = [month.lower() for month in ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']]
    mons = [month[0:3] for month in months]

    year_hit, month_hit, day_hit = [], [], []
    if 'is_year' in date_classes:
        year_hit = date_classes['is_year'][0]

    if 'is_month' in date_classes:
        for hit in date_classes['is_month']:
            if hit[0] == raw_date[1]:
                month_hit = hit

    if 'is_day' in date_classes:
        day_hit = date_classes['is_day']

    year, month, day = 0, 0, 0
    if year_hit != () and str(year_hit[0]).isdigit():
        year = year_hit[0]

    if month_hit != ():
        if str(month_hit[0]).isdigit():
            month = month_hit[0]
        elif month_hit[0] in months or month_hit[0] in mons:
            lst = months if month_hit[0] in months else mons
            month = str(lst.index(month_hit[0]) + 1)
        month = '0' + month if len(month) == 1 else month

    if day_hit != ():
        d = ''
        for s in day_hit[0]:
            d = d + s if str(s).isdigit() else d + ''
        day = '0' + d if len(d) == 1 else d

    ripe_date = str(year) + '-' + str(month) + '-' + str(day)

    return ripe_date, Utils.to_all_unixtime(ripe_date)

def turn_to_query_body(classes, user_input):
    origin_query = {}
    should_query = set().union({})
    should = []
    must = []
    numbers = []

    for k in classes.keys():
        # print('{' + str(k) + ': ' + str(classes[k]) + '}')

        top_hit = classes[k][0][0]

        if k == 'is_date' and classes[k][0][1] >= 0.7:
            must.append({'match': {'launch_unixtime': to_date(classes)[1]}})
            # must.append({'match': {'launch_unixtime': Utils.to_all_unixtime(top_hit)}})
            numbers.extend(top_hit.split(' '))
        elif ('is_date' not in classes.keys() or classes['is_date'][0][1] < 0.7) \
                and (k == 'is_number' or k == 'is_year' or k == 'is_month' or k == 'is_day'):
            for hit in classes[k]:
                should_query.add(('term', 'norad_id', int(hit[0]))) if str(hit[0]).isnumeric() else ...
            numbers.extend(top_hit.split(' '))
        elif k == 'is_intl_code':
            must.append({'match': {'intl_code': top_hit}})
            numbers.extend(top_hit.split(' '))

    origin_input = user_input.lower().rstrip().lstrip()
    extract_input = ''
    origin_count, extract_count = 1, 1
    for word in origin_input.split(' '):
        if word not in set(numbers) and word != '':
            extract_input += word + ' '
            extract_count += 1
        origin_count += 1

    if origin_count - extract_count <= 2:
        extract_input = origin_input

    extract_input = extract_input.lstrip().rstrip()
    origin_query.update({'match': {'extract': extract_input}}) \
        if extract_input != '' and not extract_input.isnumeric() else ...

    for query in should_query:
        (method, field, value) = query
        should.append({method: {field: value}})

    should.extend([origin_query]) if origin_query != {} else ...
    should.extend(must)

    body = {
        'query': {
            'bool': {
                'should': should
            }
        },
        'from': 0,
        'size': conf.ES_QUERY_MAX_SIZE
    }
    print('satellite_search_service:', body)

    return body

def search_satellites_from_es(user_input):
    classes = extract_user_input_info(user_input)
    search_body = turn_to_query_body(classes, user_input)

    res = satellite_database.search_by_body(search_body)

    # name norad_id intl_code launch_date status tle
    lst = []
    for sat in res:
        lst.append({
            'name': sat['name'],
            'norad_id': sat['norad_id'],
            'intl_code': sat['intl_code'],
            'launch_date': sat['launch_date'],
            'status': sat['status'],
            'tle': sat['tle']
        })

    return lst

# search_satellites_from_es('beidou 2018 1 11')
