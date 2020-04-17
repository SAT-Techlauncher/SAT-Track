import json
import math

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

def generate_source_jsons_from_source_json():
    with open(RAW_TEXT_ + 'source.json', 'r') as f:
        source = json.loads(f.read())

    abbrevs = {}
    sources = {}
    for src in source:
        abbrevs.update({src.lower(): '', src.lower(): ''})
        sources.update({source[src].lower(): ''})

    with open(RIPE_TEXT_ + 'sources_abbrev.json', 'w') as f:
        f.write(json.dumps(abbrevs))
    with open(RIPE_TEXT_ + 'sources_fullname.json', 'w') as f:
        f.write(json.dumps(sources))

def generate_sources_words_json_from_fullname_json():
    with open(RIPE_TEXT_ + 'sources_fullname.json', 'r') as f:
        sources = json.loads(f.read())

    source_words, counts = [], {}
    for country in sources.keys():
        words = country.split(' ')
        source_words.extend(words)
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

    with open(RIPE_TEXT_ + 'sources_words.json', 'w') as f:
        f.write(json.dumps(weights))

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

def generate_sources_countries_mapping():
    with open(RIPE_TEXT_ + 'countries_words.json', 'r') as f:
        countries_words = json.loads(f.read())
    with open(RAW_TEXT_ + 'iso_country_code.json', 'r') as f:
        countries = json.loads(f.read())
    with open(RAW_TEXT_ + 'source.json', 'r') as f:
        sources = json.loads(f.read())

    all = set()
    hits_raw_match = set()
    for source in sources.values():
        all.add(source)
        for sources_word in source.split(' '):
            for country in countries:
                fullname = country['country']
                for countries_word in fullname.split(' '):
                    rate = countries_words[countries_word.lower()]
                    if countries_word == sources_word and rate == 1.0:
                        hits_raw_match.add((source, fullname))

    hits_not_equals_or_contains = set()
    for hit in hits_raw_match:
        if not (hit[0] == hit[1] or hit[0] in hit[1] or hit[1] in hit[0]):
            hits_not_equals_or_contains.add(hit)

    hits_ripe_match_0 = hits_raw_match.difference(hits_not_equals_or_contains)

    hits_source_match_0 = set()
    for hit in hits_ripe_match_0:
        hits_source_match_0.add(hit[0])

    hits_ripe_match_1 = set()
    hits_ripe_match_1.add(('France/Germany', 'France'))
    hits_ripe_match_1.add(('France/Germany', 'Germany'))
    hits_ripe_match_1.add(('China/Brazil', 'China'))
    hits_ripe_match_1.add(('China/Brazil', 'Brazil'))
    hits_ripe_match_1.add(('United States/Brazil', 'United States of America (USA)'))
    hits_ripe_match_1.add(('United States/Brazil', 'Brazil'))
    hits_ripe_match_1.add(('Singapore/Japan', 'Singapore'))
    hits_ripe_match_1.add(('Singapore/Japan', 'Japan'))
    hits_ripe_match_1.add(('France/Italy', 'France'))
    hits_ripe_match_1.add(('France/Italy', 'Italy'))
    hits_ripe_match_1.add(('Turkmenistan/Monaco', 'Turkmenistan'))
    hits_ripe_match_1.add(('Turkmenistan/Monaco', 'Monaco'))
    hits_ripe_match_1.add(('Singapore/Taiwan', 'Singapore'))
    hits_ripe_match_1.add(('Singapore/Taiwan', 'Taiwan'))

    hits_ripe_match_1.add(('Taiwan (Republic of China)', 'China'))
    hits_ripe_match_1.add(('United States', 'United States of America (USA)'))
    hits_ripe_match_1.add(('United Kingdom', 'Great Britain (United Kingdom; England)'))
    hits_ripe_match_1.add(('Democratic People\'s Republic of Korea', 'North Korea'))
    hits_ripe_match_1.add(('Republic of Korea', 'South Korea'))
    hits_ripe_match_1.add(('Republic of Sudan', 'Sudan'))
    hits_ripe_match_1.add(('Netherlands', 'Netherlands'))
    hits_ripe_match_1.add(('Morroco', 'Morocco'))
    hits_ripe_match_1.add(('Vietna', 'Vietnam'))
    hits_ripe_match_1.add(('Philippines (Republic of the Philippines)', 'The Philippines'))
    hits_ripe_match_1.add(('Indian Space Research Organisation', 'India'))

    hits_ripe_match_1.add(('ORBCOMM', 'Commercial')) # Orbcomm
    hits_ripe_match_1.add(('Globalstar', 'Commercial')) # Loral Cor－poration, Qualcomm, Airtouch, Alcatel, Alenia, China Telecom, Dacom, Daimler-Benz Aerospac－e, France Telecom, Hyundai, Vodafone, Elascom
    hits_ripe_match_1.add(('Iridium', 'Commercial')) # Motorola Inc
    hits_ripe_match_1.add(('Asia Broadcast Satellite', 'Commercial'))
    hits_ripe_match_1.add(('RascomStar-QAF', 'Commercial')) # RascomStar-QAF
    hits_ripe_match_1.add(('O3b Networks', 'Commercial')) # Google, Liberty Global, HSBC
    hits_ripe_match_1.add(('SES', 'Commercial'))
    hits_ripe_match_1.add(('Sea Launch', 'Commercial'))

    hits_ripe_match_1.add(('North Atlantic Treaty Organization', 'International'))
    hits_ripe_match_1.add(('European Space Research Organization', 'International'))
    hits_ripe_match_1.add(('European Organization for the Exploitation of Meteorological Satellites (EUMETSAT)', 'International'))
    hits_ripe_match_1.add(('International Telecommunications Satellite Organization (INTELSAT)', 'International'))
    hits_ripe_match_1.add(('European Space Agency', 'International'))
    hits_ripe_match_1.add(('People\'s Republic of China/European Space Agency', 'International'))
    hits_ripe_match_1.add(('People\'s Republic of China/European Space Agency', 'China'))
    hits_ripe_match_1.add(('Asia Satellite Telecommunications Company (ASIASAT)', 'International'))
    hits_ripe_match_1.add(('European Telecommunications Satellite Organization (EUTELSAT)', 'International'))
    hits_ripe_match_1.add(('Arab Satellite Communications Organization', 'International'))
    hits_ripe_match_1.add(('International Space Station', 'International'))
    hits_ripe_match_1.add(('New ICO', 'International'))
    hits_ripe_match_1.add(('International Mobile Satellite Organization (INMARSAT)', 'International'))

    hits_ripe_match_1.add(('Commonwealth of Independent States (former USSR)', ''))
    hits_ripe_match_1.add(('Unknown', ''))
    hits_ripe_match_1.add(('none', ''))


    hits_ripe_match = hits_ripe_match_1.union(hits_ripe_match_0)

    print('hits_ripe_match =', len(hits_ripe_match), '/', len(all))

    count = 1
    sources_countries_mapping = {}
    for hit in hits_ripe_match:
        src, coun = hit[0], hit[1]
        key = ''
        for k, v in sources.items():
            if src == v:
                key = k.lower()
                if k not in sources_countries_mapping:
                    sources_countries_mapping.update({k.lower(): [v.lower(), ';']})
                count += 1

        for country in countries:
            if coun == country['country']:
                sources_countries_mapping[key].extend([country['code_2'].lower(), country['code_3'].lower(), country['country'].lower(), ';'])
    print(count, '/', len(sources_countries_mapping))

    with open(RIPE_TEXT_ + 'sources_countries_mapping.json', 'w') as f:
        f.write(json.dumps(sources_countries_mapping))

def generate_groups_mapping_from_sat_groups():
    with open(RAW_TEXT_ + 'sat_groups.json', 'r') as f:
        groups = json.loads(f.read())

    mapping = {}
    for dt in groups:
        group = list(dt.keys())[0]
        satellites = dt[group]
        for satellite in satellites:
            norad_id = satellite['NORAD_ID']
            mapping.update({norad_id: group})

    with open(RIPE_TEXT_ + 'satellites_groups_mapping.json', 'w') as f:
        f.write(json.dumps(mapping))
