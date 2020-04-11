import json
import difflib
import numpy as np
import math
from config import conf

with open(conf.RIPE_TEXT_ + 'countries_abbrev.json', 'r') as f:
    COUNTRIES_ABBREV = json.loads(f.read())
with open(conf.RIPE_TEXT_ + 'countries_iso_code.json', 'r') as f:
    COUNTRIES_ISO_CODE = json.loads(f.read())
with open(conf.RIPE_TEXT_ + 'countries_words.json', 'r', encoding='unicode_escape') as f:
    COUNTRIES_WORDS = json.loads(f.read())
with open(conf.RIPE_TEXT_ + 'countries_fullname.json', 'r', encoding='unicode_escape') as f:
    COUNTRIES_NAMES = json.loads(f.read())

DIGIT_RATE, ALPHA_RATE, SIGN_RATE = 0.7357, 0.1591, 0.1051
DIGIT_DIST_RANGE, ALPHA_DIST_RANGE, SIGN_DIST_RANGE = [-1.0, -0.6667], [0.6667, 1.0445], [-0.3015, 0.0]

NOUNS = ['satellite']
ADJECTIVES = ['active', 'inactive', 'operational', 'nonoperational', 'partially operational', 'backup',
              'standby', 'spare', 'extended_mission', 'decayed', 'unknown',
              'current', 'recent', 'past',
              'on orbit', 'off orbit']
VERBS = ['launch', 'decay']
ADVERBS = ['not', 'and', 'or', 'either', 'neither', 'nor', 'on', 'off', 'in', 'during', 'out', 'from', 'for']

with open(conf.RIPE_TEXT_ + 'stop_words.json', 'r') as f:
    STOP_WORDS = json.loads(f.read())

SPLIT_CHARS = {".", "/", ",", "_"}

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

def deploy_ranks(words, **ranks):
    dic = {}
    for word in words.split(' '):
        rank = ranks[word]
        dic.update({word: rank})

    lst = list(dic.values())
    for i in range(len(lst)):
        lst[i] = [lst[i]] if not isinstance(lst[i], list) else lst[i]

    routes = set()
    route = {}

    def routing(mat, dep, w, arr):
        for i in range(len(mat[dep])):
            route.update({str(dep): mat[dep][i]})

            if len(route) == len(mat):
                routes.add(tuple(route.values()))

            if dep < len(mat) - 1:
                routing(mat, dep + 1, w, arr)

    routing(lst, 0, 0, [])

    ranks_routes = []
    for route in list(routes):
        new_ranks = ranks.copy()
        parts = list(dic.keys())
        for i in range(len(parts)):
            new_ranks[parts[i]] = route[i]
        ranks_routes.append(new_ranks)

    return ranks_routes


def is_number(word, **ranks):
    if str(word).isdigit():
        if len(word) - 1 > len(str(int(word))):
            return 0.8
        return 0.7
    return 0

def is_unknown(word, **ranks):
    if word.isdigit():
        return True

    return False

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
        return 0.7

    iso_codes = list(COUNTRIES_ISO_CODE.keys())
    iso_prox, iso_idx = max_prox(str_prox, word, list(iso_codes))
    iso_prox_, iso_idx_ = max_prox(edit_distance_prox, word, list(iso_codes))

    fullname_words, weights = COUNTRIES_WORDS.keys(), COUNTRIES_WORDS.values()
    fullname_prox, fullname_idx = max_prox(str_prox, word, list(fullname_words), list(weights))
    fullname_prox_, fullname_idx_ = max_prox(edit_distance_prox, word, list(fullname_words), list(weights))

    iso_w_prox = round(0.5 * iso_prox + 0.5 * iso_prox_, 4)
    fullname_w_prox = round(0.5 * fullname_prox + 0.5 * fullname_prox_, 4)

    return max([fullname_w_prox, iso_w_prox, full_name_prox])

def is_intl_code(word, **ranks):
    if not (8 <= len(word) <= 12 and '-' in word):
        return 0

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

    digit_dist = round(math.sqrt(digit_idxs / len(word)), 4) if digit_idxs > 0 else round(
        - math.sqrt(- digit_idxs / len(word)), 4)
    alpha_dist = round(math.sqrt(alpha_idxs / len(word)), 4) if alpha_idxs > 0 else round(
        - math.sqrt(- alpha_idxs / len(word)), 4)
    sign_dist = round(math.sqrt(sign_idxs / len(word)), 4) if sign_idxs > 0 else round(
        - math.sqrt(- sign_idxs / len(word)), 4)

    # print('distribution(c) =', digit_dist, alpha_dist, sign_dist)

    digit_d_rate, alpha_d_rate, sign_d_rate = abs(digit_rate - DIGIT_RATE), abs(alpha_rate - ALPHA_RATE), abs(
        sign_rate - SIGN_RATE)
    freq_sim = 1 - (digit_rate * digit_d_rate + alpha_rate * alpha_d_rate + sign_rate * sign_d_rate)
    # print('freq_sim =', freq_sim)

    mid_dists = [sum(DIGIT_DIST_RANGE) / 2, sum(ALPHA_DIST_RANGE) / 2, sum(SIGN_DIST_RANGE) / 2]
    digit_d_dist, alpha_d_dist, sign_d_dist = abs(digit_dist - mid_dists[0]), abs(alpha_dist - mid_dists[1]), abs(
        sign_dist - mid_dists[2])
    dist_sim = 1 - (digit_rate * digit_d_dist + alpha_rate * alpha_dist + sign_rate * sign_dist) / avg_idx
    # print('dist_sim =', dist_sim)

    return round(freq_sim * dist_sim, 4)

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
        elif word == month[0:3]:
            return 0.8
        else:
            prox.append(round(0.5 * str_prox(word, month) + 0.5 * edit_distance_prox(word, month), 4))

    return round(max(prox), 4)

def is_day(word, **ranks):
    word = str(word).strip('th').strip('st').strip('nd').strip('rd')

    if word.isdigit() and 1 <= int(word) <= 31 and len(word) <= 2:
        return 0.8

    return 0

def is_date(words, **ranks):
    if len(words.split(' ')) < 2 or ranks == {}:
        return 0

    ranks = deploy_ranks(words, **ranks)

    proximities = []
    for rank in ranks:
        proximity = 0
        for word in words.split(' '):
            hits = rank[word] if isinstance(rank[word], list) else [rank[word]]

            for hit in hits:
                cls, rate = hit[0], hit[1]

                if cls == is_year.__name__:
                    proximity += 0.45 * rate
                elif cls == is_month.__name__:
                    proximity += 0.35 * rate
                elif cls == is_day.__name__:
                    proximity += 0.2 * rate
                else:
                    proximity += -1 * rate

        if proximity <= 0:
            proximity = 0

        proximities.append(proximity)

    return round(max(proximities), 4)

def is_noun(word, **ranks):
    if word.isdigit():
        return 0

    prox, idx = max_prox(str_prox, word, NOUNS)
    return round(0.5 * prox + 0.5 * edit_distance_prox(word, NOUNS[idx]), 4)

def is_verb(word, **ranks):
    if word.isdigit():
        return 0

    prox, idx = max_prox(str_prox, word, VERBS)
    return round(0.5 * prox + 0.5 * edit_distance_prox(word, VERBS[idx]), 4)

def is_adjective(word, **ranks):
    if word.isdigit():
        return 0

    prox, idx = max_prox(str_prox, word, ADJECTIVES)
    return round(0.5 * prox + 0.5 * edit_distance_prox(word, ADJECTIVES[idx]), 4)

def is_phrase(words, **ranks):
    noun_prox, verb_prox = 0, 0
    return 0

def is_sentence(words, **ranks):
    sub_prox, pred_prox, obj_prox = 0, 0, 0
    attr_prox, adv_prox, com_prox = 0, 0, 0
    return 0

from utilities.utils import approx_bisection
from utilities.concurrent_task import ConcurrentTaskPool, ConcurrentTask
from concurrent.futures.thread import ThreadPoolExecutor

CLASSIFIERS = [is_country, is_day, is_month, is_year, is_noun, is_verb, is_adjective, is_intl_code, is_number, is_date]

def classify(word, ranks):
    classifiers = CLASSIFIERS

    tasks = []
    executor = ThreadPoolExecutor(max_workers=20)

    classifier_slices = approx_bisection(classifiers, slice_num=3, dynamic_min=3)
    proximity = []
    for classifier_slice in classifier_slices:
        tasks.append(ConcurrentTask(executor, task=task_classify, targs=(classifier_slice, word, ranks)))

    task_pool = ConcurrentTaskPool(executor)
    task_pool.addTasks(tasks)
    proximities = task_pool.getResults()

    for prox in proximities:
        proximity.extend(prox)

    max_val = max(proximity)
    cls = []
    for i in range(len(proximity)):
        if proximity[i] == max_val:
            cls.append((classifiers[i].__name__, max_val))

    return proximity, cls

def task_classify(classifiers, word, ranks):
    proximity = []
    for classifier in classifiers:
        classification = classifier(word, **ranks)
        proximity.append(classification)
    return proximity