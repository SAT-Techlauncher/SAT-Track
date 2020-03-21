import time

# single concurrent task class, implementing async non-block function
class ConcurrentTask:
    def __init__(self, executor, task=None, callback=None, targs=None, cargs=None):
        """
        init
        :param executor: python.concurrent.futures ThreadingPoolExecutor instance
        :param task: concurrent task function
        :param callback: callback function
        :param targs: parameters of concurrent task function
        :param cargs: parameters of callback task function
        """
        self.task = task
        self.callbackTask = callback
        self.targs = targs
        self.cargs = cargs
        self.future = None
        self.executor = executor

    def run(self):
        """
        start new threading to execute concurrent task and call callback function when result returned
        :return:
        """
        self.future = self.executor.submit(self.task, *self.targs)
        if self.callbackTask is not None:
            self.future.add_done_callback(self.__callback)

    def __callback(self, future):
        """
        input result of concurrent task and execute callback function
        :param future: python.concurrent.futures future instance
        :return:
        """
        if self.callbackTask is None:
            raise NotImplementedError
        try:
            self.callbackTask(*self.cargs, result=future.result())
        except:
            self.callbackTask(*self.cargs)

    def getResult(self):
        """
        get result of single concurrent task
        :return: executing result
        """
        return self.future.result()

# multi-concurrent task managing pool
class ConcurrentTaskPool:
    def __init__(self, executor=None):
        """
        init
        :param executor: python.concurrent.futures ThreadingPoolExecutor instance
        """
        self.tasks = []
        self.executor = executor

    def addTasks(self, tasks):
        """
        register and execute concurrent tasks in batch
        :param tasks: concurrent tasks list: [ConcurrentTask, ConcurrentTask, ...]
        :return:
        """
        for task in tasks:
            task.future = self.executor.submit(task.task, *task.targs)
            self.tasks.append(task)

    def add(self, concurrentTask):
        """
        register and execute concurrent task
        :param concurrentTask: ConcurrentTask instance
        :return:
        """
        concurrentTask.future = self.executor.submit(concurrentTask.task, *concurrentTask.targs)
        self.tasks.append(concurrentTask)

    def getResults(self, wait=False):
        """
        get concurrent tasks executing results
        (return result when the last completed task finish, during waiting time threadings are blocked)
        :param wait: set up if threading blocked when getting results
        :return: return results list
        """
        self.executor.shutdown(wait=wait)
        results = []
        for task in self.tasks:
            result = task.future.result()
            # print('result: ', result)
            results.append(result)
        # clear tasks list after getting all concurrent tasks results
        self.tasks.clear()
        return results