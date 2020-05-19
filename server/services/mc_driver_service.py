from server.models import Utils

def send_data_to_slave(ip, params):
    current_unixtime = Utils.get_current_time()

    data = dict(ip=ip)
    data.update(**params)
    data.update(timestamp=current_unixtime)

    response = None

    return response