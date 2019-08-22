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
from ob.trace import get_exception

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

    def prompt(self):
        """ optional prompt. """

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        """ reply to the origin. """
        from ob.kernel import k
        self.result.append(txt)
        if self.direct:
            bot = k.fleet.get_bot(self.orig)
            bot.say(self.channel, txt, self.type)
        elif not self.batch:
            k.fleet.say(self.orig, self.channel, txt, self.type)

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
        self._type = ob.types.get_type(self)
        self.cfg = ob.Cfg()
        self.handlers = {}

    def get_event(self):
        return self._queue.get()

    def get_handler(self, cmd):
        return self.handlers.get(cmd, None)

    def dispatch(self, event):
        if not event.chk and event.txt:
            event.parse(event.txt)
        if not event.orig:
            event.orig = repr(self)
        event._func = self.get_handler(event.chk)
        if event._func:
            logging.warn("dispatch %s" % event.chk)
            try:
                event._func(event)
            except Exception as ex:
                logging.error(get_exception())
        return self.handle_event(event)

    def handle_event(self, event):
        event.ready()
        return event

    def loop(self):
        while not self._stopped:
            try:
                event = self.get_event()
            except EOFError:
                break
            if not event:
                continue
            thr = ob.launch(self.dispatch, event)
            if self._threaded:
                event._thrs.append(thr)
            else:
                thr.join()

    def load_mod(self, name, mod=None):
        mod = super().load_mod(name, mod)
        self.scan(mod)
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
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, ob.Object):
                t = ob.types.get_type(o)
                if t not in ob.classes:
                    ob.classes.append(t)
                w = t.split(".")[-1].lower()
                if w not in names:
                    names[w] = t

    def sync(self, bot):
        self.handlers.update(bot.handlers, skip=True)

    def start(self):
        return ob.launch(self.loop)

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
