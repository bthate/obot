""" object bot """

__version__ = 12

import ob
import queue
import sys
import threading

from ob import k
from ob.cls import Cfg
from ob.hdl import Event, Handler
from ob.shl import enable_history, set_completer

def __dir__():
    return ("Bot",)

class Bot(Handler):

    """basic bot class. """

    def __init__(self):
        super().__init__()
        self.cfg = Cfg()
        ob.update(self.cfg, {"prompt": True, "verbose": True})
        self.channels = []

    def announce(self, txt):
        """ announce txt on all registered channels. """
        if self.cfg.verbose:
            for channel in self.channels:
                self.say(channel, txt)

    def raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(str(txt) + "\n")
        sys.stdout.flush()

    def say(self, channel, txt, mtype=None):
        """ say some txt on a channel. """
        if self._outputed:
            self._outqueue.put((channel, txt, mtype))
        else:
            self.raw(txt)

    def start(self, handler=True, input=True, output=True):
        """ start the bot and add it to kernel's fleet. """
        super().start(handler, input, output)
        k.fleet.add(self)
