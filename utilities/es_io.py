from elasticsearch import Elasticsearch, helpers
from config import conf

# 初始化es对象, 最大连接响应时间从配置文件中获取
es = Elasticsearch([conf.ES_URL], timeout=conf.ES_TIMEOUT)

# elasticsearch上传/下载类, 用于es的连接, 上传, 按关键词下载等操作
class ES:
    # 表索引
    table = ""
    # 数据类型
    type = ""

    def __init__(self, db, table, create=conf.ES_CREATE_ENABLE, **kwargs):
        self.table = db
        self.type = table

        body = {
            "settings": {
                "index.mapping.total_fields.limit": conf.ES_MAPPING_LIMIT,
            },
            "mappings": {
                self.type: {
                    "properties": kwargs
                }
            }
        }

        if create:
            # 删除之前存在的数据表
            es.indices.delete(index=table, ignore=[400, 404], timeout=conf.ES_TIMEOUT)
            # 在es中创建对应数据
            es.indices.create(index=table, ignore=400, timeout=conf.ES_TIMEOUT, body=body)

    def upload(self, id, data):
        res = es.index(index=self.table, doc_type=self.type, id=id, body=data)
        if 'result' in res and (res['result'] == 'created' or res['result'] == 'updated'):
            return False, res
        return True, res

    def upload_batch(self, id_field, batch):
        actions = []
        for bat in batch:
            # 拼接插入数据结构
            action = {
                "_index": self.table,
                "_type": self.type,
                "_id": bat[id_field],
                "_source": bat
            }
            actions.append(action)

        # 批量插入
        res = helpers.bulk(es, actions)
        return res

    def concurrent_upload(self, id_field, data, concurrent_num=5, max_workers=60, dynamic_min=10):
        from concurrent.futures.thread import ThreadPoolExecutor
        from utilities.concurrent_task import ConcurrentTask, ConcurrentTaskPool
        import math

        # python多线程池对象 (最大线程数从配置文件中获取)
        executor = ThreadPoolExecutor(max_workers=max_workers)

        # 并发任务列表
        tasks = []

        length = len(data)

        # 若数据条数大于最小并发触发数, 则执行并发上传; 否则, 执行单线程上传
        if length >= dynamic_min:
            # 近似等分待上传数据并注册并发任务
            for i in range(concurrent_num):
                ptr = math.floor(i / concurrent_num * length)
                ptr_ = math.floor((i + 1) / concurrent_num * length)
                slice = data[ptr: ptr_]
                # 注册并发任务
                tasks.extend([
                    ConcurrentTask(executor, task=self.upload_batch, targs=(id_field, slice))
                ])
        else:
            tasks.extend([
                ConcurrentTask(executor, task=self.upload_batch, targs=(id_field, data))
            ])

        # 并发任务池对象
        task_pool = ConcurrentTaskPool(executor)
        # 添加并执行es上传并发任务
        task_pool.addTasks(tasks)
        # 获取es上传结果列表 (当最晚执行完毕的任务结束后返回结果, 此间线程阻塞)
        results = task_pool.getResults()

        # 根据es上传结果列表计算上传成功的数据总数
        upload_num = 0
        for result in results:
            upload_num += result[0]
        print('concurrent uploaded: ', upload_num)

        return results

    def search(self, keyword):
        """

        """
        # query =
        body = {
            'query': {
                'bool': {
                    'should': [
                        {'match': {'norad_id': keyword}},
                    ]
                }
            },
            'from': 0,
            'size': conf.ES_QUERY_MAX_SIZE
        }

        # 进行查询下载操作, 其中最大下载数据条数从配置文件中获取
        response = es.search(index=self.table, size=conf.ES_QUERY_MAX_SIZE, body=body)

        # 若未查询到结果, 则返回空值
        if 'hits' in response and 'total' in response['hits'] and response['hits']['total'] != 0:
            data = []
            for dt in response['hits']['hits']:
                src = dt['_source']
                src['highlight'] = [] if 'highlight' not in dt else dt['highlight']
                data.append(src)
            return data
        return []

    def search_by_body(self, body):
        """

        """

        # 进行查询下载操作, 其中最大下载数据条数从配置文件中获取
        response = es.search(index=self.table, size=conf.ES_QUERY_MAX_SIZE, body=body)

        # 若未查询到结果, 则返回空值
        if 'hits' in response and 'total' in response['hits'] and response['hits']['total'] != 0:
            data = []
            for dt in response['hits']['hits']:
                src = dt['_source']
                src['highlight'] = [] if 'highlight' not in dt else dt['highlight']
                data.append(src)
            return data
        return []
