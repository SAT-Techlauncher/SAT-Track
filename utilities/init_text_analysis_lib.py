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
