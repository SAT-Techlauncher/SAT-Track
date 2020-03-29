class Simulation:
    @staticmethod
    def init_db(user_id, user_info_pool, satellite_database):
        priority = [
            {"id": "#000", "name": "GPS-xxx", "active": False, "executing": False},
            {"id": "#002", "name": "SATELLITE", "active": True, "executing": False},
            {"id": "#003", "name": "SEBASTIAN-2020", "active": False, "executing": False},
            {"id": "#001", "name": "BEI-DOU", "active": True, "executing": False}
        ]
        origin = user_info_pool.get(user_id)
        origin['priority'] = priority
        user_info_pool.set(user_id, origin)

        satellite_database.set('#000', {'name': 'GPS-xxx', 'long': 0, 'lat': 0, 'data': 'GPS-data'})
        satellite_database.set('#001', {'name': 'BEI-DOU', 'long': 10, 'lat': 10, 'data': 'BEI-data'})
        satellite_database.set('#002', {'name': 'SATELLITE', 'long': -20, 'lat': 20, 'data': 'SAT-data'})
        satellite_database.set('#003', {'name': 'SEBASTIAN-2020', 'long': -30, 'lat': 30, 'data': 'Seb-data'})

    @staticmethod
    def get_from_db(pool, id):
        pool.get(id)

# 数据 打包/解析 Sebastian's Harmonized Data (SHD)
class SHD:
    """
    data: 待打包数据
    types: 为数据设置特殊报错属性类型 (暂时提供Integer, Float, String等类型)
    parsed: 打包 / 解析状态
    """
    def __init__(self, data, **kwargs):
        self.data = data
        self.types = kwargs
        self.parsed = False

    # 一致化数据格式
    def harmonize(self):
        self.parse()
        self.unparse()
        return self.data

    # 打包映射数据
    def parse(self):
        res = self.data if self.parsed else self.__parse(self.data)
        self.parsed = True
        self.data = res
        return self.data

    # 打包数据 (内部方法)
    def __parse(self, data, **kwargs):
        if str(type(data)) == "<class 'list'>":
            return self.__lst(data, **kwargs)
        elif str(type(data)) == "<class 'dict'>":
            return self.__dic(data, **kwargs)
        else:
            return self.__base(data, **kwargs)

    # 打包列表 (内部方法)
    def __lst(self, data, **kwargs):
        if data is []:
            return {}

        res = "{"
        idx = 0
        for ele in data:
            sub = ele
            ele = self.__parse(sub)
            if str(type(ele)) == "<class 'str'>":
                ele = "'" + ele + "'"
            res += "'" + self.__idx(idx) + "'" + ": " + str(ele)
            idx += 1
            if idx != len(data):
                res += ", "

        res += "}"
        try:
            res = eval(res)
        except:
            res = {'_0_': None}
        return res

    # 打包字典 (内部方法)
    def __dic(self, data, **kwargs):
        for k in data.keys():
            sub = data[k]
            data[k] = self.__parse(sub, k=k)
            if str(k).isdigit():
                k_ = self.__key(k)
                data.update({k_: data.pop(k)})
        res = data
        return res

    # 打包基础类型 (内部方法)
    def __base(self, data, **kwargs):
        if 'k' in kwargs:
            k = kwargs['k']
            if k in self.types:
                res = self.types[k](self, data)
                return res
        res = data
        return res

    # 解析映射数据
    def unparse(self):
        res = self.data if not self.parsed else self.__unparse(self.data)
        self.parsed = False
        self.data = res
        return self.data

    # 解析数据 (内部方法)
    def __unparse(self, data, **kwargs):
        if str(type(data)) != "<class 'dict'>":
            return self.__unbase(data)
        elif self.__a_idx() in data:
            return self.__unlst(data)
        else:
            return self.__undic(data)

    # 解析列表 (内部方法)
    def __unlst(self, data, **kwargs):
        lst = []
        for k in data:
            res = self.__unparse(data[k])
            lst.append(res)
        return lst

    # 解析字典 (内部方法)
    def __undic(self, data, **kwargs):
        dic = {}
        for k in data:
            if self.__is_key(k):
                k_ = self.__unkey(k)
                data.update({k_: data.pop(k)})
                k = k_
            dic[k] = self.__unparse(data[k])
        return dic

    # 解析基础类型 (内部方法)
    def __unbase(self, data, **kwargs):
        return data

    # 创建格式化数据中列表索引格式 '_n_'
    def __idx(self, v):
        return "_" + str(v) + "_"

    # 格式化数据中键的规定索引格式 '_n_'
    def __a_idx(self):
        return "_" + str(0) + "_"

    # 创建格式化数据中非法键的合法形式
    def __key(self, v):
        return "str_" + v

    # 将合法形式的键还原
    def __unkey(self, s):
        return s[4:len(s)]

    # 判断格式化数据中键是否被合法化
    def __is_key(self, s):
        pre = s[0:4]
        post = s[4:len(s)]
        if pre == "str_" and post.isdigit():
            return True
        return False

    def Integer(self, v):
        return int(v)

    def Float(self, v):
        return float(v)

    def String(self, v):
        return str(v)

    class __Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    def to_object(self):
        if not self.parsed:
            return None

        return self.__to_object(self.data)

    def __to_object(self, dic):
        if not isinstance(dic, dict):
            return dic

        inst = self.__Dict()
        for k, v in dic.items():
            inst[k] = self.__to_object(v)
        return inst

    @staticmethod
    def test():
        user = {'000': {'email': 'u6631954@anu.edu.au', 'password': '96e79218965eb72c92a549dd5a330112',
                        'priority': [{'id': 0, 'name': 'GPS-xxx'}, {'id': 2, 'name': 'SATELLITE'},
                                     {'id': 3, 'name': 'SEBASTIAN-2020'}, {'id': 1, 'name': 'BEI-DOU'}]}}

        data = SHD(user)

        print('parsed data' if data.parsed else 'unparsed data', ':\n   ', data.data, '\n')

        data.parse()

        print('parsed data' if data.parsed else 'unparsed data', ':\n   ', data.data, '\n')

        obj = data.to_object()

        print('obj:\n   ', obj.str_000, '\n')

        data.unparse()

        print('parsed data' if data.parsed else 'unparsed data', ':\n   ', data.data, '\n')

'''
Sebastian's Dictionary Objectification (SDO): dict => json => class
'''


class A:
    def __init__(self, id, name):
        self.__id=id
        self.__name=name

    def to_dict(self):
        return self.__dict__

a = A(0, 4)
print(a.to_dict())