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
    uploadCount = 0
    # 下载计数器
    downloadCount = 0

    def __init__(self, table, create=conf.ES_CREATE_ENABLE):
        self.table = table

        body = {
            "settings": {
                "index.analysis.analyzer.default.type": "ik_max_word",
                "index.analysis.analyzer.default_search.type": "ik_max_word",
                "index.mapping.total_fields.limit": conf.ES_MAPPING_LIMIT,
            },
            "mappings": {
                "doc": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "index_options": "offsets",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_max_word"
                        }
                    }
                }
            }
        }

        if create:
            # 删除之前存在的数据表
            es.indices.delete(index=table, ignore=[400, 404], timeout=conf.ES_TIMEOUT)
            # 在es中创建对应数据
            es.indices.create(index=table, ignore=400, timeout=conf.ES_TIMEOUT, body=body)

    def searchByKeywords(self, timestamp, keywords, time_range):
        """

        """
        # 生成关键词查询字典
        keywordQueryBody = []
        for keyword in keywords:
            keywordQueryBody.extend([{'term': {conf.DOWNLOAD_FIELD_0: keyword}}, {'match': {conf.DOWNLOAD_FIELD_1: keyword}}])

        # query = timestamp - time_range < copyDate <= timestamp && (keyword1 in [field1, ...] || keyword2 in [] ...)
        body = {
            "query": {"bool": {"must": [
                {"range": {conf.DOWNLOAD_FIELD_TIME: {"gt": timestamp - time_range, "lte": timestamp}}},
                {"bool": {"should": keywordQueryBody}}
            ]}},
            "highlight": {
                "pre_tags": ["<K>"],
                "post_tags": ["</K>"],
                "fields": {
                    "content": {},
                    "topkeyword": {}
                }
            },
            "collapse": {
                "field": "id.keyword"
            },
            "from": 0,
            "size": conf.ES_QUERY_MAX_SIZE
        }

        # 进行查询下载操作, 其中最大下载数据条数从配置文件中获取
        response = es.search(index=conf.ES_NEWS_INDEX, size=conf.ES_QUERY_MAX_SIZE, body=body)

        # 若未查询到结果, 则返回空值
        if 'hits' in response and 'total' in response['hits'] and response['hits']['total'] != 0:
            data = []
            for dt in response['hits']['hits']:
                dtSource = dt['_source']
                dtSource['highlight'] = [] if 'highlight' not in dt else dt['highlight']
                data.append(dtSource)
            return {'timestamp': timestamp, 'type': 'none', 'data': data}
        return {'timestamp': timestamp, 'type': 'none', 'data': []}

    def searchByKeyword(self, timestamp, keyword, time_range):
        """
        下载数据 (按 单个关键词 进行不分词查询)
        :param timestamp: 当前时间戳
        :param keyword: 待查询关键词
        :param time_range: 查询时间范围
        :param args: ['字段1']
        :return: {
                   'timestamp': (int),
                   'type': (str),
                   'data': [{'timestamp': (int), 'type': (str), 'query_keyword': (str), ...}, ...]
                 }
        """
        # 生成关键词查询字典
        keywordQueryBody = {
            'match_phrase': {
                conf.DOWNLOAD_FIELD_0: keyword
            }
        }

        # query = timestamp - time_range < copyDate <= timestamp && keyword in field
        body = {
            "query": {
                "bool": {
                    "must": [{
                        "range": {
                            "copyDate": {
                                "gt": timestamp - time_range,
                                "lte": timestamp
                            }
                        }
                    }, keywordQueryBody]
                }
            },
            "from": 0,
            "size": conf.ES_QUERY_MAX_SIZE
        }
        # 进行查询下载操作, 其中最大下载数据条数从配置文件中获取
        response = es.search(index=self.table, size=conf.ES_QUERY_MAX_SIZE, body=body)

        # 若未查询到结果, 则返回空值
        self.downloadCount += 1
        if 'hits' in response and 'total' in response['hits'] and response['hits']['total'] != 0:
            res = {}
            data = []
            num = 0
            for dt in response['hits']['hits']:
                dtSource = dt['_source']
                dtSource['query_keyword'] = keyword
                data.append(dtSource)
                if num == 0:
                    res['timestamp'] = dtSource['timestamp']
                    res['type'] = dtSource['type']
            res['data'] = data
            return res
        return {'timestamp': timestamp, 'type': 'none', 'data': []}

    def searchAll(self):
        """
        查询表中所有数据
        :return: {
                   'timestamp': (int),
                   'type': (str),
                   'data': [{'timestamp': (int), 'type': (str), 'query_keyword': (str), ...}, ...]
                 }
        """
        # query = all
        body = {
            "query": {
                "match_all": {}
            }
        }
        # 进行查询下载操作, 其中最大下载数据条数从配置文件中获取
        response = es.search(index=self.table, size=conf.ES_QUERY_MAX_SIZE, body=body)

        # 若未查询到结果, 则返回空值
        if 'hits' in response and 'total' in response['hits'] and response['hits']['total'] != 0:
            res = {}
            data = []
            num = 0
            for dt in response['hits']['hits']:
                dtSource = dt['_source']
                data.append(dtSource)
                if num == 0:
                    res['timestamp'] = dtSource['timestamp']
            res['data'] = data
            return res
        return None

    def uploadBatch(self, data):
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
        self.uploadCount += 1
        return res

# 数据打包/解析类, 用于将数据打包成合法格式上传至es
class Data:
    # 待打包数据
    data = None
    # 基本类型字段的合法类型映射字典, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
    types = []

    def __init__(self, data=None):
        self.data = data

    def parse(self, data):
        """
        打包映射数据 (外部方法)
        :param data: 待打包数据
        :return: 合法格式数据
        """
        return self.__parse(data)

    def extract_parse(self, data, *args):
        """
        打包并提取简略数据
        :param data: 待打包数据
        :param args: 待提取字段
        :return: 合法格式原始数据, 合法格式简略数据
        """
        res = self.__parse(data)
        lst = []
        for ele in res['data']:
            dic = {'timestamp': data['timestamp'], 'type': data['type']}
            for arg in args:
                dic[arg] = ele[arg]
            lst.append(dic)
        res_ = {'timestamp': data['timestamp'], 'type': data['type'], 'data': lst}
        return res, res_

    def __parse(self, data, **kwargs):
        """
        打包数据 (内部方法)
        :param data: 待打包数据
        :param kwargs: 待规范 字段-基本类型 参数, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
        :return: 合法格式数据
        """
        # 按待打包数据类型分配至不同打包方法
        if str(type(data)) == "<class 'list'>":
            res = self.__lst(data, **kwargs)
        elif str(type(data)) == "<class 'dict'>":
            res = self.__dic(data, **kwargs)
        else:
            res = self.__base(data, **kwargs)
        return res

    def __lst(self, data, **kwargs):
        """
        打包列表 (内部方法)
        :param data: 待打包数据
        :param kwargs: 待规范 字段-基本类型 参数, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
        :return: 合法格式列表数据
        """
        for ele in data:
            sub = ele
            ele = self.__parse(sub)
        return data

    def __dic(self, data, **kwargs):
        """
        打包字典 (内部方法)
        :param data: 待打包数据
        :param kwargs: 待规范 字段-基本类型 参数, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
        :return: 合法格式字典数据
        """
        for k in data.keys():
            sub = data[k]
            data[k] = self.__parse(sub, k=k)
        res = data
        return res

    def __base(self, data, **kwargs):
        """
        打包基本类型数据 (内部方法)
        :param data: 待打包数据
        :param kwargs: 待规范 字段-基本类型 参数, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
        :return: 合法格式基本类型数据
        """
        if 'k' in kwargs:
            k = kwargs['k']
            if k in self.types:
                res = self.types[k](self, data)
                return res
        res = data
        return res

    def set(self, **kwargs):
        """
        为es的映射设置特殊报错字段类型 (暂时提供Integer, Float, String等类型)
        :param kwargs: 待规范 字段-基本类型 参数, {'字段1': '基本类型1', '字段2': '基本类型2', ...}
        :return:
        """
        self.types = kwargs

    def Integer(self, v):
        return int(v)

    def Float(self, v):
        return float(v)

    def String(self, v):
        return str(v)

