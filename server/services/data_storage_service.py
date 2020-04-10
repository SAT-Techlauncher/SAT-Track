from . import *

class UserManager:
    @staticmethod
    def create(user):
        user.id = Utils.to_hash(user.email)
        user_info_pool.set(str(user.id), {'email': user.email, 'password': user.password, 'priority': []})
        user_info_pool.show()

    @staticmethod
    def get(id):
        res = user_info_pool.get(id)

        if res is None:
            return None

        print('get user(', res['email'], ')\'s info:', res['priority'])
        return User(
            email=res['email'],
            password=res['password'],
            priority=res['priority']
        )

    @staticmethod
    def set(user):
        user_info_pool.set(str(user.id), {'email': user.email, 'password': user.password, 'priority': user.priority})
        print('set user(', user.email, ')\'s info:', user.priority)

    @staticmethod
    def validate_user(email, password):
        user = user_info_pool.get(Utils.to_hash(email))

        if user is None:
            print('user doesn\'t exist')
            return RET.NODATA, None

        if user['password'] != password:
            print('password is wrong')
            return RET.AUTHERR, None

        print('validate user (', user, ')')
        return RET.OK, Utils.to_hash(email)

class PriorityManager:
    @staticmethod
    def order_up(tasks, satellite_id):
        priority = Priority(tasks)
        try:
            satellite_index = priority.index(satellite_id)
            satellite = priority.pop(satellite_index)
            priority.insert(0, satellite)
            print('ordered up', satellite_id, 'and now the list is', priority)
            return RET.OK, priority.to_dict()
        except:
            print('failed to order up', satellite_id)
            return RET.EXECERR, None

    @staticmethod
    def order_down(tasks, satellite_id):
        priority = Priority(tasks)
        try:
            satellite_index = priority.index(satellite_id)
            satellite = priority.pop(satellite_index)
            priority.insert(len(priority), satellite)
            print('ordered down', satellite_id, 'and now the list is', priority)
            return RET.OK, priority.to_dict()
        except:
            print('failed to order down', satellite_id)
            return RET.EXECERR, None

    @staticmethod
    def delete(tasks, satellite_id):
        priority = Priority(tasks)
        try:
            priority.remove(satellite_id)
            print('deleted sat', satellite_id, 'and now the list is', priority)
            return RET.OK, priority.to_dict()
        except:
            print('failed to delete sat', satellite_id)
            return RET.EXECERR, None

    @staticmethod
    def activate(tasks, satellite_id):
        priority = Priority(tasks)
        try:
            task = priority.get(satellite_id)
            print('before ', priority)
            task.activate()
            print('after', priority)
            # index = priority.index(satellite_id)
            # task = priority.pop(index)
            # executable = task.activate()
            # priority.insert(index, task)
            print('activated sat', satellite_id, 'and now the list is', priority)
            return RET.OK, priority.to_dict(), task.is_active()
        except:
            print('failed to activate sat', satellite_id)
            return RET.EXECERR, [], None

    @staticmethod
    def insert(tasks, satellite):
        priority = Priority(tasks)
        satellite_id = satellite.norad_id
        try:
            priority.insert(0, Task(
                id=satellite_id,
                name=satellite.name,
                is_active=True,
                is_executing=False
            ))
            print('inserted ', satellite_id, 'and now the list is', priority)
            return RET.OK, priority.to_dict()
        except:
            print('failed to insert', satellite_id)
            return RET.EXECERR, None

class SatelliteManager:
    @staticmethod
    def get(info):
        satellite_database.search(info)


