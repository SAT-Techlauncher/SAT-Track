from . import *

class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.id = Utils.to_hash(email)

    def to_dict(self):
        return self.__dict__

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        res = user_info_pool.get(user_id)
        if res is not None:
            return User(
                email=res['email'],
                password=res['password']
            )
        return None

    @staticmethod
    def create(user):
        user.id = Utils.to_hash(user.email)
        user_info_pool.set(str(user.id), {'email': user.email, 'password': user.password})
        user_info_pool.show()

    @staticmethod
    def validate_user(email, password):
        user = user_info_pool.get(Utils.to_hash(email))
        print('user:', user)

        if user is None:
            print('user doesn\'t exist')
            return RET.NODATA, None

        if user['password'] != password:
            print('password is wrong')
            return RET.AUTHERR, None

        return RET.OK, Utils.to_hash(email)

class Satellite:
    def __init__(self):
        ...