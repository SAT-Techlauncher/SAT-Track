from flask import request, current_app, render_template, jsonify
import json
from . import views

# log recording api request
@views.before_request
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
@views.after_request
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

# app routes
@views.route('/home', methods=['GET', 'POST'])
def home_page():
    return 'home_page'

@views.route('/test_error_log', methods=['GET', 'POST'])
def test_error_log():
    try:
        x = 1 / 0
    except Exception as e:
        current_app.logger.error('[Calculating error] x = 1 / 0')
    return 'testErrorLog'

@views.route('/version', methods=['GET', 'POST'])
def version():
    # test version auto-update
    return 'test version 0.0.01'

@views.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title="Index")

@views.route('/search_satellite', methods=['GET', 'POST'])
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
