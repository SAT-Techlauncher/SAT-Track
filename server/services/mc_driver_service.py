from server.models import Utils

def send_data_to_slave():

    current_unixtime = Utils.get_current_time()

    return