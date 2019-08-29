""" event callback dispatcher. """

import inspect
import logging
import ob
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

modules = {}
names = {}

class Event(Command):

    """ Basic event class. """

    def __init__(self):
        super().__init__()
        self._ready = threading.Event()
        self.batch = False
        self.direct = False
        self.type = "chat"
        self.name = ""
        self.sep = "\n"

    def display(self, o, txt=""):
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
        self._ready.set()

    def reply(self, txt):
        """ reply to the origin. """
        from ob.kernel import k
        self.result.append(txt)

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

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._stopped = False
        self._threaded = False
        self._type = get_type(self)
        self.cbs = {}
        self.cfg = ob.Cfg()
        self.handlers = {}

    def get_handler(self, cmd):
        return self.handlers.get(cmd, None)

    def dispatch(self, event):
        if not event.chk and event.txt:
            event.parse(event.txt)
        if not event.orig:
            event.orig = repr(self)
        event._func = self.get_handler(event.chk)
        if event._func:
            event._func(event)
        for cb in self.cbs.values():
            logging.warning("cb %s" % str(cb))
            cb(e)
        self.show(event)
        event.ready()
        
    def handler(self):
        while not self._stopped:
            e = self._queue.get()
            logging.debug(e)
            thr2 = ob.launch(self.dispatch, e)
            if self._threaded:
                event._thrs.append(thr2)
            else:
                thr2.join()

    def load_mod(self, name, mod=None):
        try:
            mod = super().load_mod(name, mod)
            self.scan(mod)
        except ModuleNotFoundError:
            pass
        except Exception as ex:
            logging.error(get_exception())
        return mod

    def put(self, event):
        self._queue.put_nowait(event)

    def ready(self):
        self._ready.set()

    def register(self, cmd, handler):
        self.handlers[cmd] = handler

    def scan(self, mod):
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if "event" in o.__code__.co_varnames:
                self.register(key, o)
                modules[key] = o.__module__
                if "cb_" in key:
                    self.cbs[key] = o
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, ob.Object):
                t = get_type(o)
                if t not in ob.classes:
                    ob.classes.append(t)
                w = t.split(".")[-1].lower()
                if w not in names:
                    names[w] = str(t)

    def show(self, event):
        for line in event.result:
            print(line)

    def sync(self, bot):
        self.handlers.update(bot.handlers, skip=True)
        self.cbs.update(bot.cbs, skip=True)

    def start(self):
        logging.warning("start %s" % get_name(self))
        return ob.launch(self.handler)

    def stop(self):
        self._stopped = True

    def unload(self, modname):
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
        self._ready.wait()

    def walk(self, pkgname):
        mod = None
        try:
            mod = self.load_mod(pkgname)
        except ModuleNotFoundError:
            try:
                mod = self.load_mod("ob.%s" % pkgname)
            except ModuleNotFoundError:
                try:
                    mod = self.load_mod("obot.%s" % pkgname)
                except ModuleNotFoundError:
                    try:
                        mod = self.load_mod("%s.%s" % (self.cfg.name, pkgname))
                    except ModuleNotFoundError:
                       pass
        if not mod:
            logging.warn("not found %s" % pkgname)
            return
        res = [mod,]
        try:
            mods = pkgutil.iter_modules(mod.__path__, mod.__name__+".")
        except:
            mods = pkgutil.iter_modules([mod.__file__,], mod.__name__+".")
        for n in mods:
            logging.warn("load %s" % n[1])
            res.append(self.load_mod(n[1]))
        return res
