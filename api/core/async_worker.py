from threading import Thread


class WorkerController(object):

    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass


WORKER_CONTROLLER = WorkerController()


class AsyncWorker(Thread):
    ASYNC_WORKER_INFO = dict()

    def __init__(self, params, ticket_id):
        Thread.__init__(self)
        self.params = params
        self.ticket_id = ticket_id
        self.daemon = True
        self.start()

    def run(self):
        AsyncWorker.ASYNC_WORKER_INFO[self.ticket_id] = {
            # 保存一些业务信息，之后轮询的时候，可以作为输出返回
            "some": "information",
            "status": "running"
        }
        WORKER_CONTROLLER.run(self.params)
