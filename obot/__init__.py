""" object bot """

__version__ = 8

import ob
import queue
import sys
import threading

from ob import Cfg
from ob.kernel import k
from ob.handler import Event, Handler
from ob.shell import enable_history, set_completer

def __dir__():
    return ("Bot",)

class Bot(Handler):

    """basic bot class. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self.cfg = Cfg()
        ob.update(self.cfg, {"prompt": True, "verbose": True})
        self.channels = []

    def _raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(str(txt) + "\n")
        sys.stdout.flush()

    def announce(self, txt):
        """ announce txt on all registered channels. """
        if self.cfg.verbose:
            for channel in self.channels:
                self.say(channel, txt)

    def dispatch(self, event):
        """ run handlers/callbacks for this event. """
        return super().dispatch(event)

    def event(self):
        """ return the event to be handled, default takes event from queue. """
        return super().event()

    def put(self, event):
        """ send an event to the handler. """
        return super().put(event)
        
    def say(self, orig, channel, txt, mtype=None):
        """ say some txt on a channel. """
        self._raw(txt)

    def start(self, nohandler=False):
        """ start the bot and add it to kernel's fleet. """
        super().start(nohandler)
        k.fleet.add(self)
