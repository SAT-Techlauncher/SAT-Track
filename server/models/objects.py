from . import *
from flask_login import UserMixin
import json

class User(UserMixin):
    def __init__(self, email, password, priority=list()):
        self.email = email
        self.password = password
        self.id = Utils.to_hash(email)
        self.name = email.split('@')[0]
        self.priority = priority

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def to_dict(self):
        return self.__dict__

class Priority:
    def __init__(self, priority):
        """
        turn priority json [{'id': id, 'name', name}, ...] into list [Task(id, name), ...]
        :param priority: [Task(id_0, name_0), Task(id_1, name_1), ...]
        """

        self.__tasks = [Task(task['id'], task['name'], task['active'], task['executing']) for task in priority]
        self.__task_ids = [task['id'] for task in priority]

    def get(self, id):
        try:
            index = self.__task_ids.index(id)
            return self.__tasks[index]
        except:
            return None

    def insert(self, index, task):
        self.__task_ids.insert(index, task.id)
        return self.__tasks.insert(index, task)

    def remove(self, id):
        self.__tasks.remove(self.get(id))
        self.__task_ids.remove(id)
        return None

    def pop(self, index):
        self.__task_ids.pop(index)
        return self.__tasks.pop(index)

    def index(self, id):
        return self.__task_ids.index(id)

    def __len__(self):
        return len(self.__tasks)

    def to_dict(self):
        return eval(str(self))

    def to_list(self):
        return self.__tasks

    def __str__(self):
        lst = []
        for task in self.__tasks:
            lst.append(task.to_dict())
        return str(lst)

class Task:
    def __init__(self, id, name, is_active, is_executing):
        self.id = id
        self.name = name
        self.__is_active = is_active
        self.__is_executing = is_executing

    def activate(self):
        self.__is_active = False if self.__is_active else True
        self.__is_executing = False if not self.__is_active else self.__is_executing
        return self.__is_active

    def execute(self):
        self.__is_executing = True if self.__is_active is True and self.__is_executing is False else False
        return self.__is_executing

    def is_active(self):
        return self.__is_active

    def is_executing(self):
        return self.__is_executing

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'active': self.__is_active,
            'executing': self.__is_executing
        }

    def __str__(self):
        return str(self.to_dict())

class Satellite(SOD):
    def __init__(self, dic, **kwargs):
        super().__init__(dic, **kwargs)

    def Upper(self, v):
        v = str(v) if not isinstance(v, str) else v
        return v.upper()

    def String(self, v):
        return str(v) if v is not None else str('none')














