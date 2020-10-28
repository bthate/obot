# OLIB
#
#

"handler (hdl)"

import queue, _thread

from ol.obj import Object
from ol.tsk import start as launch

dispatchlock = _thread.allocate_lock()

class Handler(Object):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.stopped = False

    def dispatch(self, e):
        "overload this"

    def handler(self):
        "handler loop"
        while not self.stopped:
            event = self.queue.get()
            if not event:
                break
            if "orig" not in event:
                event.orig = repr(self)
            if event.txt:
                self.dispatch(event)
                #event.thrs.append(launch(self.dispatch, event))
            else:
                event.ready.set()

    def put(self, e):
        "put event on queue"
        self.queue.put_nowait(e)

    def start(self):
        "start handler"
        launch(self.handler)

    def stop(self):
        "stop handler"
        self.stopped = True
        self.queue.put(None)
