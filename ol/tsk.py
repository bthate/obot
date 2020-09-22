# OLIB - object library
#
#

import ol
import queue
import threading

class Task(threading.Thread):

    def __init__(self, func, *args, name="noname", daemon=True):
        super().__init__(None, self.run, name, (), {}, daemon=daemon)
        self._name = name
        self._result = None
        self._queue = queue.Queue()
        self._queue.put((func, args))
        self.sleep = 0
        self.state = ol.Object()

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def run(self):
        func, args = self._queue.get()
        self.setName(self._name)
        try:
            self._result = func(*args)
        except EOFError:
            _thread.interrupt_main()
        except Exception as _ex:
            print(ol.utl.get_exception())

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

       
def launch(func, *args, **kwargs):
    name = kwargs.get("name", ol.get_name(func))
    t = Task(func, *args, name=name, daemon=True)
    t.start()
    return t
