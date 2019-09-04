""" event callback dispatcher. """

import inspect
import logging
import ob
import os
import pkgutil
import queue
import threading

from ob import Object
from ob.command import Command
from ob.loader import Loader
from ob.times import days
from ob.trace import get_exception
from ob.types import get_type
from ob.utils import get_name

def __dir__():
    return ("Event", "Handler")

class Event(Command):

    """ Basic event class. """

    def __init__(self):
        super().__init__()
        self._ready = threading.Event()
        self.direct = False
        self.type = "chat"
        self.name = ""
        self.orig = None
        self.origin = ""
        self.sep = "\n"

    def display(self, o, txt=""):
        """ display an object. """
        if "k" in self.options:
            self.reply("|".join(o))
            return
        if "d" in self.options:
            self.reply(str(o))
            return
        full = False
        if "f" in self.options:
            full = True
        if self.dkeys:
            txt += " " + ob.format(o, self.dkeys, full)
        else:
            txt += " " + ob.format(o, full=full)
        if "t" in self.options:
            txt += " " + days(o._path)
        txt = txt.rstrip()
        if txt:
            self.reply(txt)

    def ready(self):
        """ signal ready. """
        self._ready.set()

    def reply(self, txt):
        """ reply to the origin. """
        self.result.append(txt)

    def show(self):
        """ echo result to originating bot. """
        from ob.kernel import k
        for line in self.result:
            if self.orig == k:
                print(line)
                continue
            k.say(self.orig, self.channel, line, self.type)

    def wait(self):
        """ wait for event to finish. """
        self._ready.wait()
        thrs = []
        vals = []
        for thr in self._thrs:
            try:
                thr.join()
            except RuntimeError:
                vals.append(thr)
                continue
            thrs.append(thr)
        for val in vals:
            try:
                val.join()
            except RuntimeError:
                pass
        for thr in thrs:
            self._thrs.remove(thr)
        return self

class Handler(Loader):

    """ Event Handler class. """

    def __init__(self):
        super().__init__()
        self._outqueue = queue.Queue()
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._stopped = False
        self._threaded = False
        self._type = get_type(self)
        self.cfg = ob.Cfg()
        self.classes = []
        self.cmds = {}
        self.handlers = []
        self.modules = {}
        self.names = {}

    def event(self):
        return self._queue.get()

    def handle(self, e):
        """ return the event to be handled. """
        for h in self.handlers:
            h(self, e)
        e.ready()

    def handler(self):
        """ basic event handler routine. """
        while not self._stopped:
            e = self.event()
            try:
                self.handle(e)
            except Exception as ex:
                logging.error(get_exception())

    def load_mod(self, mn):
        """ load module and scan for functions. """
        mod = super().load_mod(mn)
        self.scan(mod)
        return mod

    def put(self, event):
        """ put event on queue. """
        self._queue.put_nowait(event)

    def register(self, handler):
        """ register a handler for a command. """
        if handler not in self.handlers:
            self.handlers.append(handler)

    def scan(self, mod):
        """ scan a module for commands/callbacks. """
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if o.__code__.co_argcount == 1 and "event" in o.__code__.co_varnames:
                self.cmds[key] = o
                self.modules[key] = o.__module__
            elif o.__code__.co_argcount == 2 and "handler" in o.__code__.co_varnames:
                self.register(o)
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, ob.Object):
                t = get_type(o)
                if t not in self.classes:
                    self.classes.append(t)
                w = t.split(".")[-1].lower()
                if w not in self.names:
                    self.names[w] = str(t)

    def start(self, handler=None):
        """ start this handler. """
        logging.warning("start %s" % get_name(self))
        ob.launch(handler or self.handler)

    def walk(self, pkgname):
        """ scan package for module to load. """
        mod = self.load_mod(pkgname)
        mods = [mod,]
        try:
            mns = pkgutil.iter_modules(mod.__path__, mod.__name__+".")
        except:
            mns = pkgutil.iter_modules([mod.__file__,], mod.__name__+".")
        for n in mns:
            logging.warn("load %s" % n[1])
            mods.append(self.load_mod(n[1]))
        for m in mods:
            self.scan(m)
        return mods
