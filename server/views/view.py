from . import *
from . import view_bp

@view_bp.route('/', methods=['GET', 'POST'])
@view_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_authenticated:
        print('authenticated', session.get('user_id'))

    return render_template('index.html')


    # user_id = session.get('user_id')
    # print(user_id)
    # if user_id is None:
    #     g.user = None
    #     return redirect(url_for('auth.login'))
    # return redirect(url_for('view.index'))

