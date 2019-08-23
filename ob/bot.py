""" bot base class. """

import ob
import queue
import sys
import threading

from ob import Cfg, classes
from ob.kernel import k
from ob.handler import Event, Handler
from ob.shell import enable_history, set_completer

def __dir__():
    return ("Bot", "Console")

class Bot(Handler):

    """basic bot class. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self.cfg = Cfg()
        ob.update(self.cfg, {"prompt": True, "verbose": True})
        self.channels = []

    def _output(self):
        """ an optional output thread. """
        self._outputed = True
        while not self._stopped:
            channel, txt, otype = self._outqueue.get()
            if txt:
                self._say(channel, txt, otype)

    def _raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(txt)
        sys.stdout.flush()

    def _say(self, *args):
        """ say some text on some channel. """
        if self.cfg.verbose and len(args) > 1:
            self._raw(str(args[1]) + "\n")

    def announce(self, txt):
        """ announce txt on all registered channels. """
        if self.cfg.verbose:
            for channel in self.channels:
                self.say(channel, txt)

    def cmd(self, txt, origin=""):
        """ execute a command on this bot. """
        event = Event()
        event.batch = True
        event.txt = txt
        event.options = k.cfg.options
        event.origin = origin or "root@shell"
        k.dispatch(event)
        event.wait()
        for val in event.result:
            self.say("", val)

    def say(self, channel, txt, mtype=None):
        """ say some txt on a channel. """
        self._say(channel, txt, mtype)

    def start(self):
        """ start the bot and add it to kernel's fleet. """
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
        self._raw(str(txt) + "\n")

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
        set_completer(k.handlers)
        enable_history()
