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
                self.say(repr(self), channel, txt, otype)

    def _raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(txt)
        sys.stdout.flush()

    def announce(self, txt):
        """ announce txt on all registered channels. """
        if self.cfg.verbose:
            for channel in self.channels:
                self.say(channel, txt)

    def say(self, channel, txt, mtype=None):
        """ say some txt on a channel. """
        self._raw(channel, txt, mtype)

    def start(self):
        """ start the bot and add it to kernel's fleet. """
        super().start()
        k.fleet.add(self)
        ob.launch(self.shell)
