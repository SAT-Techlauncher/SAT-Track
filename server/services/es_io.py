from elasticsearch import Elasticsearch, helpers
from config import conf

# 初始化es对象, 最大连接响应时间从配置文件中获取
es = Elasticsearch([conf.ES_URL], timeout=conf.ES_TIMEOUT)

# elasticsearch上传/下载类, 用于es的连接, 上传, 按关键词下载等操作
class ES:
    # 每条数据索引
    idx = 0
    # 表索引
    table = ""
    # 数据类型
    type = "doc"
    # 上传计数器
    upload_count = 0
    # 下载计数器
    download_count = 0

    def __init__(self, table, create=conf.ES_CREATE_ENABLE):
        self.table = table

        body = {
            "settings": {
                "index.mapping.total_fields.limit": conf.ES_MAPPING_LIMIT,
            },
            "mappings": {
                "doc": {
                    "properties": {

                    }
                }
            }
        }

        if create:
            # 删除之前存在的数据表
            es.indices.delete(index=table, ignore=[400, 404], timeout=conf.ES_TIMEOUT)
            # 在es中创建对应数据
            es.indices.create(index=table, ignore=400, timeout=conf.ES_TIMEOUT, body=body)

    def upload_batch(self, data):
        """
        批量上传数据 (使用helpers.bulk)
        :param data: 批量待上传数据, {'timestamp': (int), 'type': (str), 'data': [{'timestamp': (int), 'type': (str), ...}, ...]}
        :return: es.helpers.bulk上传返回结果
        """
        batch = data['data']

        actions = []
        for bat in batch:
            dt = bat
            # 注册时间戳和数据来源
            dt['timestamp'] = data['timestamp']
            dt['type'] = data['type']

            # 拼接插入数据结构
            action = {
                "_index": self.table,
                "_type": self.type,
                "_id": dt['id'],
                "_source": dt
            }
            actions.append(action)
            self.idx += 1

        # 批量插入
        res = helpers.bulk(es, actions)
        self.upload_count += 1
        return res

# Sebastian's Harmonized Data
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
        self.data = self.__harmonize(self.data)
        return self.data

    # 一致化 (内部方法)
    def __harmonize(self, data, **kwargs):
        if str(type(data)) == "<class 'list'>":
            return self.__harmonize_lst(data, **kwargs)
        elif str(type(data)) == "<class 'dict'>":
            return self.__harmonize_dic(data, **kwargs)
        else:
            return self.__base(data, **kwargs)

    def __harmonize_lst(self, data, **kwargs):
        res = []
        for ele in data:
            res.append(self.__harmonize(ele, **kwargs))
        return res

    def __harmonize_dic(self, data, **kwargs):
        res = {}
        for k in data:
            res.update({k: self.__harmonize(data[k], k=k)})
        return res

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

