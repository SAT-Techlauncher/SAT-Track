from . import *
from . import view_bp
from server.services.data_storage_service import UserManager

@view_bp.route('/', methods=['GET', 'POST'])
@view_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session.get('user_id')
    print('authenticated: ', user_id)

    user_info_pool.show()
    # satellite_database.show()

    if user_id is None:
        return redirect(url_for('auth.login', code=RET.AUTHERR))

    if request.method == 'GET':
        print('index:', user_id)


    return render_template(
        'index.html',
        code=RET.OK
    )

@view_bp.route('/getUserInfo', methods=['GET'])
def get_user_info():
    if request.method == 'GET':
        user_id = session.get('user_id')

        status, user = controll_get_user_info(user_id)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                username=user.name,
                priority=user.priority
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR
    )

@view_bp.route('/orderUpTask', methods=['GET'])
def order_up_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = int(request.args.get('id'))

        status, tasks = controll_order_up_task(user_id, satellite_id)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                priority=tasks
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/orderDownTask', methods=['GET'])
def order_down_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = int(request.args.get('id'))

        status, tasks = controll_order_down_task(user_id, satellite_id)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                priority=tasks
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/deleteTask', methods=['GET'])
def delete_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = int(request.args.get('id'))

        status, tasks = controll_delete_task(user_id, satellite_id)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                priority=tasks
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/activateTask', methods=['GET'])
def activate_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = int(request.args.get('id'))

        status, is_active = controll_activate_task(user_id, satellite_id)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                active=is_active
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/searchSatellite', methods=['GET'])
def search_satellite():
    if request.method == 'GET':
        user_id = session.get('user_id')
        user_input = request.args.get('input')
        print(user_input)

        if user_input == '':
            return jsonify(
                code=RET.SNTERR,
            )

        status, satellites, beyond_lmt = controll_search_satellites(user_id, user_input)

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                lst=satellites,
                more=beyond_lmt
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/selectSatellite', methods=['GET'])
def select_satellite():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = request.args.get('id')
        if satellite_id is None:
            return jsonify(
                code=RET.SNTERR,
            )

        status, tasks = controll_select_satellite(user_id, int(satellite_id))

        if status == RET.OK:
            return jsonify(
                code=RET.OK,
                priority=tasks
            )
        else:
            return jsonify(
                code=RET.SNTERR,
            )
    return jsonify(
        code=RET.REQERR,
    )

@view_bp.route('/satelliteInfo?<string:satinfo>', methods=['GET'])
def satellite_info(satinfo):
    try:
        satinfo = json.loads(satinfo)
    except Exception as e:
        return jsonify(
            code=RET.SNTERR,
            msg=str(e)
        )

    if request.method == 'GET':
        user_id = "5d109b88a0f925ccb8e957ea6d867911" # session.get('user_id')

        try:
            data = controll_modify_sat_info(user_id, satinfo)
        except Exception as e:
            user = UserManager.get(user_id)
            data = satinfo
            data.update({'username': user.get_name(), 'ip': user.ip})
            print(e)

        return render_template(
            'info.html',
            **data
        )

    return jsonify(
        code=RET.REQERR,
    )


@view_bp.route('/getSatInfo', methods=['GET'])
def get_sat_info():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = request.args.get('id')

        if satellite_id is None:
            return jsonify(
                code=RET.SNTERR,
            )

        status, satinfo = controll_get_sat_info(user_id, int(satellite_id))

        return redirect(url_for('view.satellite_info', satinfo=json.dumps(satinfo)))

    return jsonify(
        code=RET.REQERR
    )


# @view_bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#     g.user = UserManager.get(user_id) if user_id is not None else None

@view_bp.after_request
def after_app_request(response):
    api_name = request.url
    user_ip = request.remote_addr
    user_id = session.get('user_id')

    user = UserManager.get(user_id)
    if user is None:
        return response

    UserManager.set(user.set_ip(user_ip))

    if str(response.status_code).startswith('4') or str(response.status_code).startswith('5'):
        ...
    print('{"api_name": "%s", "user_id": "%s", "user_ip": "%s", "status_code":"%s"}' % (
            api_name, user_id, user_ip, response.status_code))
    return response
