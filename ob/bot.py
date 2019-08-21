""" provide persistence through save/load to JSON files. """

import queue
import sys
import threading

from . import Cfg, classes
from .kernel import k
from .handler import Event, Handler
from .shell import enable_history, set_completer

def __dir__():
    return ("Bot", "Console")

class Bot(Handler):

    """ Basic bot class. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self.cfg = Cfg()
        self.cfg.update({"prompt": True, "verbose": True})
        self.channels = []

    def _say(self, *args):
        """ say some text on some channel. """
        if self.cfg.verbose and len(args) > 1:
            self.raw(str(args[1]) + "\n")

    def announce(self, txt):
        """ announce txt on all registered channels. """
        for channel in self.channels:
            self.say(channel, txt)

    def cmd(self, txt, origin=""):
        """ execute a command on this bot. """
        event = Event()
        event.batch = True
        event.txt = txt
        event.options = k.cfg.options
        event.origin = origin or "root@shell"
        self.dispatch(event)
        event.wait()
        for val in event.result:
            self.say("", val)

    def output(self):
        """ an optional output thread. """
        self._outputed = True
        while not self._stopped:
            channel, txt, otype = self._outqueue.get()
            if txt:
                self._say(channel, txt, otype)
    def raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(txt)
        sys.stdout.flush()

    def say(self, channel, txt, mtype=None):
        self._say(channel, txt, mtype)

    def start(self):
        super().start()
        k.fleet.add(self)

class Console(Bot):

    """ A console bot. """

    def __init__(self):
        super().__init__()
        self._prompted = threading.Event()
        self._prompted.set()

    def announce(self, txt):
        """ announce to console. """
        if k.cfg.test:
            raw(str(txt) + "\n")

    def dispatch(self, event):
        """ dispatch and wait for the event to finish. """
        super().dispatch(event)
        event.wait()
        self._prompted.set()
        return event

    def get_event(self):
        """ return a event by prompting for some text. """
        event = Event()
        event.direct = True
        event.options = k.cfg.options
        event.origin = "root@shell"
        self._prompted.wait()
        if self.cfg.prompt:
            event.txt = input("> ")
            event.txt = event.txt.rstrip()
        self._prompted.clear()
        return event

    def start(self):
        """ start the console. """
        super().start()
        set_completer(self.handlers)
        enable_history()
