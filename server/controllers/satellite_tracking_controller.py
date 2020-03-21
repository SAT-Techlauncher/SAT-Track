

def satellite_tracking(id):
    """
    tracking satellite as clients require
    :param id: satellite id
    :return: data and information received from the tracked satellite
    """

    from server.services import search_satellite_in_database


    from server.services import fetch_satellite_location
    location = fetch_satellite_location(id)



    return None