from server.controllers import *
from server.services.data_storage_service import UserManager, PriorityManager, SatelliteManager
from server.services.satellite_search_service import search_satellites_from_es

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
        return RET.AUTHERR, None

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
        satellites = res if 0 < len(res) <= 10 else res[0 : conf.SEARCH_RESULT_LMT]
        return RET.OK, satellites

    errors = res
    print('error in controll_search_satellites: errors(' + str(len(errors)) + ') =', errors)
    return status, errors

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