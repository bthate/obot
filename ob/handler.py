""" event callback dispatcher. """

import inspect
import logging
import ob
import os
import pkgutil
import queue
import threading

from ob import Object, Register
from ob.command import Command
from ob.errors import ENOTIMPLEMENTED
from ob.loader import Loader
from ob.obj import format
from ob.times import days
from ob.tasks import Launcher
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
        self.sep = "\n"

class Handler(Loader, Launcher):

    """ Event Handler class. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._stopped = False
        self._threaded = False
        self._type = get_type(self)
        self.cfg = ob.Cfg()
        self.classes = []
        self.cmds = Register()
        self.handlers = []
        self.modules = {}
        self.names = {}

    def get_cmd(self, cmd):
        """ return matching function. """
        func = self.cmds.get(cmd, None)
        if not func:
            mn = self.names.get(func, None)
            if mn:
                self.load_mod(mn)
        return self.cmds.get(cmd, None)

    def handle(self, e):
        """ return the event to be handled. """
        thrs = []
        for h in self.handlers:
            if "threaded" in dir(h) and h.threaded:
                thrs.append(self.launch(h, self, e))
            else:
                h(self, e)
        for thr in thrs:
            thr.join()
        e.ready()

    def handler(self):
        """ basic event handler routine. """
        while not self._stopped:
            e = self._queue.get()
            if not e:
                break
            try:
                self.handle(e)
            except Exception as ex:
                logging.error(get_exception())
        self._ready.set()

    def input(self):
        """ start a input loop. """
        while not self._stopped:
            e = self.poll()
            self.put(e)

    def load_mod(self, mn):
        """ load module and scan for functions. """
        mod = super().load_mod(mn)
        self.scan(mod)
        return mod

    def output(self):
        self._outputed = True
        while not self._stopped:
            channel, txt, type = self._outqueue.get()
            if txt:
                self.say(channel, txt, type)

    def poll(self):
        """ poll for an event. """
        raise ENOTIMPLEMENTED

    def put(self, event):
        """ put event on queue. """
        self._queue.put_nowait(event)

    def register(self, handler):
        """ register a handler for a command. """
        if handler not in self.handlers:
            self.handlers.append(handler)

    def say(self, channel, txt, type="chat"):
        print(txt)

    def scan(self, mod):
        """ scan a module for commands/callbacks. """
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if o.__code__.co_argcount == 1 and "event" in o.__code__.co_varnames:
                self.cmds[key] = o
                self.modules[key] = o.__module__
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, ob.Object):
                t = get_type(o)
                if t not in self.classes:
                    self.classes.append(t)
                w = t.split(".")[-1].lower()
                if w not in self.names:
                    self.names[w] = str(t)

    def start(self, handler=True, input=True, output=True):
        """ start this handler. """
        logging.warning("start %s" % get_name(self))
        if handler:
            self.launch(self.handler)
        if input:
            self.launch(self.input)
        if output:
            self.launch(self.output)

    def stop(self):
        self._stopped = True
        self._queue.put(None)
        
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
