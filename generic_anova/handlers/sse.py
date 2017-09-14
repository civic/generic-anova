
from tornado import (
    gen,
    iostream,
    ioloop,
    web,
    queues
)
import uuid
import json


class Publisher:

    def __init__(self):
        self.subscribers = {}

    def get_subscribers(self):
        yield from self.subscribers.values()

    def publish(self, data):
        for sub in self.get_subscribers():
            sub.send(data)

    def create_subscriber(self):
        sub = Subscriber(self)
        self.subscribers[sub.uid] = sub
        return sub

    def close(self):
        for sub in self.get_subscribers():
            sub.close()

        self.subscribers.clear()

    def release(self, subscriber):
        if subscriber.uid in self.subscribers:
            self.subscribers.pop(subscriber.uid)


class Subscriber:
    END_STREAM = {}

    def __init__(self, publisher):
        self.queue = queues.Queue()
        self.uid = str(uuid.uuid1())
        self.publisher= publisher
        self._closed = False

    def send(self, data):
        self.queue.put(data)

    def unsubscribe(self):
        self.publisher.release(self)

    def close(self):
        if not self._closed:
            self._closed = True
            self.queue.put(self.END_STREAM)


publisher = Publisher()

@gen.coroutine
def factory(handler, request):

    sub = publisher.create_subscriber()
    sub.send({'event': 'init'})
    return sub

class SSEHandler(web.RequestHandler):

    @gen.coroutine
    def prepare(self):
        try:
            self.subscriber = yield factory(self, self.request)
        except Exception as e:
            gen.app_log.exception("invalid request")
            self.send_error(500)
            return

        if self.subscriber:
            gen.app_log.debug("create SSEHandler %s", self.subscriber.uid)
            self.set_header('content-type', 'text/event-stream')
            self.set_header('cache-control', 'no-cache')

    @gen.coroutine
    def get(self):
        try:
            while True:
                data = yield self.subscriber.queue.get()
                try:
                    if data == Subscriber.END_STREAM:
                        break
                    self.write("data: %s\n\n" % json.dumps(data))
                    self.flush()
                finally:
                    self.subscriber.queue.task_done()
        except iostream.StreamClosedError:
            self.subscriber.unsubscribe()

    def on_connection_close(self):
        gen.app_log.debug("close SSEHandler %s", self.subscriber.uid)

    def on_finish(self):
        if hasattr(self, "subscriber"):
            gen.app_log.debug("finish SSEHandler %s", self.subscriber.uid)
            self.subscriber.unsubscribe()


