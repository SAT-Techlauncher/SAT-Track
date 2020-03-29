from . import *
from . import auth_bp

@auth_bp.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'POST':
        email = request.form.get('email')

        print(email, UserManager.get(Utils.to_hash(email)))

        if UserManager.get(Utils.to_hash(email)) is not None:
            print('user has been existed before register')
            return jsonify(
                code=RET.AUTHERR
            )

        return jsonify(
            code=RET.OK
        )

    return jsonify(
        code=RET.REQERR
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=Utils.to_hash(form.password.data)
        )

        if UserManager.get(Utils.to_hash(form.email.data)) is not None:
            print('user has been existed when register')
            return redirect(url_for('auth.register', code=RET.OK))

        UserManager.create(user)
        print('user', user.to_dict())

        return redirect(url_for('auth.login'))

    return render_template('register.html', title="Register", form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    email = request.form.get('email')
    password = Utils.to_hash(request.form.get('password'))

    if form.validate_on_submit():
        validation, id = UserManager.validate_user(email, password)

        if validation is RET.OK:
            session.clear()
            session['user_id'] = id

            user = UserManager.get(id)
            login_user(user, form.remember_me.data)

            return redirect(url_for('view.index'))
        else:
            return redirect(url_for('auth.register'))

    return render_template('login.html', title="Login", form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# @auth_bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#     g.user = User.get(user_id) if user_id is not None else None
#
# # log report api response
# @auth_bp.after_request
# def after_app_request(response):
#     api_name = request.url
#     user_ip = request.remote_addr
#     try:
#         user_name = request.remote_user
#     except Exception as e:
#         user_name = e
#     response_data = response.json
#     if str(response.status_code).startswith('4') or str(response.status_code).startswith('5') :
#          current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' %(api_name, user_ip, user_name, response.status_code))
#     else:
#         current_app.logger.info('{"api_name": "%s", "user_ip": "%s", "user_name": "%s", "status_code":"%s"}' % (
#         api_name, user_ip, user_name, response.status_code))
#     return response