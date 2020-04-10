from server.controllers import *
from server.services.data_storage_service import UserManager, PriorityManager, SatelliteManager
from server.services.satellite_search_service import fetch_satellite_info

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

def controll_search_new_task(user_id, satellite_id):
    user = UserManager.get(user_id)
    if user is None:
        return RET.AUTHERR, None

    satellite = SatelliteManager.get(satellite_id)
    print('controll_search_new_task: satellite =', satellite)

    status, tasks = PriorityManager.insert(user.priority, satellite)
    if status == RET.OK:
        user.priority = tasks
        UserManager.set(user)
        return RET.OK, tasks

    return status, None

