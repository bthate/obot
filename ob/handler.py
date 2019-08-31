""" event callback dispatcher. """

import inspect
import logging
import ob
import ob.tables
import os
import pkgutil
import queue
import threading

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
        self.cbs = {}
        self.cfg = ob.Cfg()
        self.handlers = {}

    def get_handler(self, cmd):
        """ return a handler for a command. """
        h = self.handlers.get(cmd, None)
        if not h and cmd in ob.tables.modules:
            mn = ob.tables.modules[cmd]
            self.load_mod(mn)
            h = self.handlers.get(cmd, None)
            logging.warning("autoload %s" % mn)
        return h

    def dispatch(self, event):
        """ dispatch a event to its handler/callbacks. """
        if not event.chk and event.txt:
            event.parse(event.txt)
        if not event.orig:
            event.orig = repr(self)
        event._func = self.get_handler(event.chk)
        if event._func:
            event._func(event)
        for cb in self.cbs.values():
            logging.warning("cb %s" % str(cb))
            cb(event)
        event.show()
        event.ready()

    def event(self):
        """ return the event to be handled. """
        return self._queue.get()

    def input(self):
        """ input loop. override event() to return the event to be handled."""
        while not self._stopped:
            e = self.event()
            self.put(e)

    def handler(self):
        """ basic event handler routine. """
        while not self._stopped:
            e = self._queue.get()
            thr2 = ob.launch(self.dispatch, e)
            if self._threaded:
                event._thrs.append(thr2)
            else:
                thr2.join()

    def load_mod(self, name, mod=None):
        """ loading a module and scan for handlers/commands. """
        mod = super().load_mod(name, mod)
        self.scan(mod)
        return mod

    def output(self):
        """ an optional output thread. """
        while not self._stopped:
            orig, channel, txt, otype = self._outqueue.get()
            if txt:
                self.say(orig, channel, txt, otype)

    def put(self, event):
        """ put event on queue. """
        self._queue.put_nowait(event)

    def ready(self):
        """ signal this handler as ready. """
        self._ready.set()

    def register(self, cmd, handler):
        """ register a handler for a command. """
        self.handlers[cmd] = handler

    def scan(self, mod):
        """ scan a module for commands/callbacks. """
        if "classes" not in dir(ob.tables):
            ob.tables.classes = []
        if "modules" not in dir(ob.tables):
            ob.tables.modules = {}
        if "names" not in dir(ob.tables):
            ob.tables.names = {}
        if "classes" not in dir(ob.tables):
            ob.tables.classes = []
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if "event" in o.__code__.co_varnames:
                if "cb_" in key and key not in self.cbs:
                    self.cbs[key] = o
                else:
                    self.register(key, o)
                    ob.tables.modules[key] = o.__module__
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, ob.Object):
                t = get_type(o)
                if t not in ob.tables.classes:
                    ob.tables.classes.append(t)
                w = t.split(".")[-1].lower()
                if w not in ob.tables.names:
                    ob.tables.names[w] = str(t)

    def say(self, orig, channel, txt, type):
        """ say txt in channel of bot with origin orig. """
        pass

    def sync(self, bot):
        """ synchronize this handler handlers/callbacks with that of provided bot's. """
        self.handlers.update(bot.handlers)
        self.cbs.update(bot.cbs)

    def start(self):
        """ start this handler. """
        logging.warning("start %s" % get_name(self))
        ob.launch(self.handler)
        ob.launch(self.input)
        ob.launch(self.output)

    def stop(self):
        """ stop this handler. """
        self._stopped = True

    def unload(self, modname):
        """ unload a module. """
        mod = self.table.get(modname, None)
        if mod:
            for key, func, name, kind in self.scan(mod):
                if name == modname:
                    try:
                        del self.handlers[key]
                    except KeyError:
                        pass
                    if kind == "class":
                        ob.table.classes.remove(key)
        super().unload(modname)

    def wait(self):
        """ wait for this handler to be ready. """
        self._ready.wait()

    def walk(self, pkgname):
        """ scan package for module to load. """
        mod = self.load_mod(pkgname)
        res = [mod,]
        try:
            mods = pkgutil.iter_modules(mod.__path__, mod.__name__+".")
        except:
            mods = pkgutil.iter_modules([mod.__file__,], mod.__name__+".")
        for n in mods:
            logging.warn("load %s" % n[1])
            res.append(self.load_mod(n[1]))
        return res
