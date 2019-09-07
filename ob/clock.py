""" timer, repeater. """

import ob
import threading
import time

from ob.kernel import k
from ob.utils import get_name

def __dir__():
    return ("Repeater", "Timer", "Timers")

class Timers(ob.Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopped = False
        self.cfg = ob.Cfg()
        self.timers = ob.Object()

    def loop(self):
        while not self._stopped:
            time.sleep(1.0)
            remove = []
            for t in self.timers:
                event = self.timers[t]
                if time.time() > t:
                    self.cfg.latest = time.time()
                    self.cfg.save()
                    event.raw(event.txt)
                    remove.append(t)
            for r in remove:
                del self.timers[r]

    def start(self):
        for e in k.db.all("ob.clock.Timers"):
            if "done" in e and e.done:
                continue
            if "time" not in e:
                continue
            if time.time() < int(e.time):
                self.timers[e.time] = e
        return k.launch(self.loop)

    def stop(self):
        self._stopped = True

class Timer(ob.Object):

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._name = kwargs.get("name", get_name(func))
        self.sleep = sleep
        self.args = args
        self.kwargs = kwargs
        self.state = ob.Object()
        self.timer = None

    def start(self):
        timer = threading.Timer(self.sleep, self.run, self.args, self.kwargs)
        timer.setName(self._name)
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer._func = self._func
        timer.start()
        self.timer = timer
        return timer

    def run(self, *args, **kwargs):
        self.state.latest = time.time()
        k.launch(self._func, *args, **kwargs)

    def exit(self):
        self.timer.cancel()

class Repeater(Timer):

    def run(self, *args, **kwargs):
        self._func(*args, **kwargs)
        return k.launch(self.start)
