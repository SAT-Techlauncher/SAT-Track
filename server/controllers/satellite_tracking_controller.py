from concurrent.futures.thread import ThreadPoolExecutor

from server.services.data_storage_service import UserManager, SatelliteManager, TrackingManager
from server.services.satellite_tracking_service import get_location_from_ip, get_tracking_info_from_es
from server.services.mc_driver_service import send_data_to_slave
from utilities.concurrent_task import ConcurrentTask, ConcurrentTaskPool
from utilities.utils import approx_bisection
from config import conf


def controll_satellite_tracking():
    """
    :return: data and information received from the tracked satellite
    """

    all_users = UserManager.get_all_users()

    user_slices = approx_bisection(all_users)

    tasks = []
    executor = ThreadPoolExecutor(max_workers=conf.MAX_WORKERS)
    for slice in user_slices:
        tasks.append(ConcurrentTask(executor, task=task_tracking, targs=(slice, 0)))
    taskPool = ConcurrentTaskPool(executor)
    taskPool.addTasks(tasks)

    return taskPool.getResults()

def task_tracking(users, pld=0):
    responses = []
    print('satellite tracking ->')
    for user in users:
        user_location = get_location_from_ip(user.ip)
        for sat in user.priority:
            az_alt_v = get_tracking_info_from_es(sat['id'], user_location)

            TrackingManager.set(
                sid=sat['id'],
                az_alt_v=az_alt_v,
                loc=user_location,
                ip=user.ip
            )
            response = send_data_to_slave(user.ip, az_alt_v)
            responses.append({
                'user': user.id,
                'ip': user.ip,
                'sat': sat['id'],
                'response': response
            })
    return responses
