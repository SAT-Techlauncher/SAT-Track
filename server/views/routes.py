from . import *
from . import routes_bp

# app routes
@routes_bp.route('/search_satellite', methods=['GET', 'POST'])
def search_satellite():
    """
    1. Get satellite id from frontend.
    2. Check if satellite information has already been in database.
    3. Fetch satellite information (id, location, ...) from external website.
    4. Send satellite information to slave-computer.
    5. Get satellite signal from slave-computer.
    6. Return satellite signal to user.
    """
    if request.method == 'GET':
        return 'GET method'

    if request.method == 'POST':
        try:
            satellite_id = request.form['id']

            from server.controllers import satellite_tracking
            data = satellite_tracking(satellite_id)

            return jsonify({
                'code': '001',
                'data': data
            })
        except:
            return 'got no id'

    return 'None'

@routes_bp.route('/getPriorityList', methods=['GET'])
def get_priority_list():
    if request.method == 'GET':
        user_id = session.get('user_id')



        return jsonify(
            code=RET.OK,
        )

    return jsonify(
        code=RET.SNTERR
    )


# log recording api request
@routes_bp.before_request
def before_app_request():
    api_name = request.url
    user_ip = request.remote_addr
    try:
        user_name = request.remote_user
    except Exception as e:
        user_name = e
    try:
        # receive frontend data
        request_data = json.loads(request.get_data())
    except Exception as e:
        request_data = request.form.to_dict()
    current_app.logger.info('{"api_name":"%s", "user_ip":"%s", "user_name":"%s"}'
                            % (api_name, user_ip, user_name))

# log report api response
@routes_bp.after_request
def after_app_request(response):
    api_name = request.url
    user_ip = request.remote_addr
    try:
        user_name = request.remote_user
    except Exception as e:
        user_name = e
    response_data = response.json
    if str(response.status_code).startswith('4') or str(response.status_code).startswith('5') :
         current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' %(api_name, user_ip, user_name, response.status_code))
    else:
        current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' % (
        api_name, user_ip, user_name, response.status_code))
    return response


@view_bp.route('/test', methods=['GET'])
def test():
    return 'data of a satellite'
