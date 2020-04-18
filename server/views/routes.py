from . import *
from . import routes_bp

# app routes
@routes_bp.route('/tracking', methods=['GET', 'POST'])
def search_satellite():
    """
    1. Get satellite id from frontend. -> views.search_new_task
    2. Check if satellite information has already been in database.
    3. Fetch satellite information (id, location, ...) from external website.
    4. Send satellite information to slave-computer.
    5. Get satellite signal from slave-computer.
    6. Return satellite signal to user.
    """
    if request.method == 'POST':
        return jsonify(
            code=RET.REQERR
        )

    if request.method == 'GET':
        try:
            satellite_id = request.args.get('id')

            from server.controllers.satellite_tracking_controller import controll_satellite_tracking
            data = controll_satellite_tracking(satellite_id)

            return jsonify(
                code=RET.OK,
                data=data
            )
        except:
            return jsonify(
                code=RET.EXECERR
            )

    return jsonify(
        code=RET.UNKNOWN
    )

