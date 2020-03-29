from . import *
from . import view_bp

@view_bp.route('/', methods=['GET', 'POST'])
@view_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session.get('user_id')
    print('authenticated: ', user_id)

    if conf.CLEAR_REDIS:
        from server.services.simulate_for_dev import Simulation
        Simulation.init_db(user_id, user_info_pool, satellite_database)

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

        user = controll_get_user_info(user_id)

        return jsonify(
            code=RET.OK,
            username=user.name,
            priority=user.priority
        )

    return jsonify(
        code=RET.REQERR
    )

@view_bp.route('/orderUpTask', methods=['GET'])
def order_up_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = request.args.get('id')

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
        satellite_id = request.args.get('id')

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
        satellite_id = request.args.get('id')

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
        satellite_id = request.args.get('id')

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

@view_bp.route('/searchNewTask', methods=['GET'])
def search_new_task():
    if request.method == 'GET':
        user_id = session.get('user_id')
        satellite_id = request.args.get('id')

        status, tasks = controll_search_new_task(user_id, satellite_id)

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


        # @view_bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#     g.user = User.get(user_id) if user_id is not None else None
#
# # log report api response
# @view_bp.after_request
# def after_app_request(response):
#     api_name = request.url
#     user_ip = request.remote_addr
#     try:
#         user_name = request.remote_user
#     except Exception as e:
#         user_name = e
#     response_data = response.json
#     if str(response.status_code).startswith('4') or str(response.status_code).startswith('5'):
#         current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' % (
#         api_name, user_ip, user_name, response.status_code))
#     else:
#         current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' % (
#             api_name, user_ip, user_name, response.status_code))
#     return response