from server.controllers import *
from server.services.data_storage_service import UserManager, PriorityManager, SatelliteManager, TrackingManager
from server.services.satellite_search_service import search_satellites_from_es
from server.services.satellite_tracking_service import get_location_from_ip, get_tracking_info_from_es


def controll_get_user_info(user_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    return RET.OK, user


def controll_order_up_task(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    status, tasks = PriorityManager.order_up(user.priority, satellite_id)
    if status == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, tasks

    return status, None


def controll_order_down_task(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    status, tasks = PriorityManager.order_down(user.priority, satellite_id)
    if status == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, tasks

    return status, None


def controll_delete_task(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    status, tasks = PriorityManager.delete(user.priority, satellite_id)
    if status == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, tasks

    return status, None


def controll_activate_task(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    status, tasks, is_active = PriorityManager.activate(user.priority, satellite_id)
    if status == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, is_active

    return status, None


def controll_search_satellites(user_id, user_input):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None, None

    satellite_lst = search_satellites_from_es(user_input)
    print()
    print('controll_search_new_task:')
    print(len(satellite_lst))
    for sat in satellite_lst[0:10]:
        print(sat)
    print('...')
    print()

    status, res = SatelliteManager.to_satellites(satellite_lst)

    if status == RET.OK:
        if 0 < len(res) <= conf.SEARCH_RESULT_LMT:
            satellites = res
            beyond_lmt = False
        else:
            satellites = res[0 : conf.SEARCH_RESULT_LMT]
            beyond_lmt = True
        return RET.OK, satellites, beyond_lmt

    errors = res
    print('error in controll_search_satellites: errors(' + str(len(errors)) + ') =', errors)
    return status, errors, None


def controll_select_satellite(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    status_0, satellite = SatelliteManager.get(satellite_id)
    if status_0 != RET.OK:
        return status_0, None

    status_1, tasks = PriorityManager.insert(user.priority, satellite)
    if status_1 == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, tasks

    print('error in controll_select_satellite: error =', tasks)
    return status_1, None


def controll_get_sat_info(user_id, satellite_id):
    user = UserManager.get(user_id)

    if user is None:
        return RET.AUTHERR, None

    status_0, satellite = SatelliteManager.get(satellite_id)
    if status_0 != RET.OK:
        return status_0, None

    status_1, track_info = TrackingManager.get(sid=satellite_id)
    if status_1 != RET.OK:
        user_location = get_location_from_ip(user.ip)
        az_alt_v = get_tracking_info_from_es(satellite_id, user_location)
        track_info = dict()
        track_info.update(**az_alt_v, **user_location, ip=user.ip)
        TrackingManager.set(satellite_id, az_alt_v=az_alt_v, loc=user_location, ip=user.ip)

    satinfo = dict(**satellite.to_dict(), **track_info)
    return RET.OK, satinfo


def controll_modify_sat_info(user_id, satinfo):
    user = UserManager.get(user_id)

    data = dict()
    fields = [
        'intl_code', 'norad_id', 'name', 'source', 'launch_date', 'decay_date',
        'full_site', 'group', 'status', 'az', 'alt', 'vel', 'lat', 'long', 'elev'
    ]

    for field in fields:
        val = satinfo[field]
        if val is None:
            continue

        if StrUtils.isfloat(str(val)):
            satinfo[field] = round(float(val), 2)

        if field == 'source':
            satinfo[field] = val.upper()
        elif field == 'full_site' or field == 'group':
            lst = val.split(' ')
            modified = ''
            for e in lst:
                if e[0] == '(':
                    modified += e.upper() + ' '
                    continue
                if e == 'the' or e == 'of':
                    modified += e + ' '
                    continue
                modified += e[0].upper() + e[1:len(e)] + ' '
            satinfo[field] = modified.rstrip()
        data.update({field: satinfo[field]})
    data.update({'username': user.get_name(), 'ip': user.ip})
    print('<----->', satinfo['name'], data)

    return data