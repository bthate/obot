""" OB threads (tasks). """

import logging
import ob
import queue
import threading
import time
import types

from ob.trace import get_exception
from ob.utils import get_name

def __dir__():
    return ("Task", "Launcher", "ps")

class Task(threading.Thread):

    def __init__(self, func, *args, name="noname", daemon=True):
        super().__init__(None, self.run, name, (), {}, daemon=daemon)
        self._result = None
        self._queue = queue.Queue()
        self._queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def run(self):
        func, args = self._queue.get()
        self._result = func(*args)

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

class Launcher:

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()
        self._stopped = False

    def launch(self, func, *args, **kwargs):
        name = ""
        try:
            name = kwargs.get("name", args[0].name or args[0].txt)
        except (AttributeError, IndexError):
            name = get_name(func)
        t = Task(func, *args, name=name)
        try:
            t.start()
        except RuntimeError:
            self._queue.put_nowait(t)
        return t

    def start(self):
        while not self._stopped:
            t = self._queue.get()
            t.start()
