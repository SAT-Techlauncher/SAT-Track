from . import *
from . import auth_bp

@auth_bp.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'POST':
        email = request.form.get('email')

        print(email, User.get(Utils.to_hash(email)))

        if User.get(Utils.to_hash(email)) is not None:
            print('user has been existed before register')
            return jsonify(
                code=RET.AUTHERR
            )

        return jsonify(
            code=RET.OK
        )

    return jsonify(
        code=RET.SNTERR
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=Utils.to_hash(form.password.data)
        )

        if User.get(Utils.to_hash(form.email.data)) is not None:
            print('user has been existed when register')
            return redirect(url_for('auth.register', code=RET.OK))

        User.create(user)
        print('user', user.to_dict())

        return redirect(url_for('auth.login'))

    return render_template('register.html', title="Register", form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    email = request.form.get('email')
    password = Utils.to_hash(request.form.get('password'))

    if form.validate_on_submit():
        validation, id = User.validate_user(email, password)

        if validation is RET.OK:
            # session.clear()
            # session['user_id'] = id

            user = User.get(id)
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

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.get(user_id) if user_id is not None else None