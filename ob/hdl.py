""" event callback dispatcher. """

import inspect
import logging
import ob
import os
import pkgutil
import queue
import time
import threading

from ob.cls import Cfg, Register
from ob.err import ENOTIMPLEMENTED
from ob.ldr import Loader
from ob.pst import Persist
from ob.thr import Launcher
from ob.tms import days
from ob.trc import get_exception
from ob.utl import get_name
from ob.cls import get_type

def __dir__():
    return ("Handler", "aliases")

aliases = {
           "c": "cmds",
           "cfg": "show cfg",
           "f": "find",
           "l": "log",
           "ps": "show tasks",
           "t": "todo",
           "u": "show uptime",
           "v": "show version"
           }

class Handler(Loader, Launcher):

    """ event Handler class. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._outqueue = queue.Queue()
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._stopped = False
        self._threaded = False
        self._type = get_type(self)
        self.cfg = Cfg()
        self.classes = []
        self.cmds = {}
        self.handlers = []
        self.modules = {}
        self.names = {}
        self.sleep = False
        self.state = ob.Object()
        self.state.last = time.time()
        self.state.nrsend = 0

    def aliased(self, txt):
        """ return aliased version of txt. """
        spl = txt.split()
        if spl and spl[0] in aliases:
            cmd = spl[0]
            v = aliases.get(cmd, None)
            if v:
                return v.split()[0]
        return txt

    def get_cmd(self, cmd):
        """ return matching function. """
        cmd = self.aliased(cmd)
        func = self.cmds.get(cmd, None)
        if not func and self.cfg.autoload:
            mn = self.names.get(cmd, None)
            if mn:
                self.load_mod(mn)
        return self.cmds.get(cmd, None)

    def get_handler(self, cmd):
        cmd = self.aliased(cmd)
        func = self.handler.get(cmd, None)
        if not func and self.cfg.autoload:
            mn = self.names.get(cmd, None)
            if mn:
                self.load_mod(mn)
        return self.cmds.get(cmd, None)

    def handle(self, e):
        """ return the event to be handled. """
        thrs = []
        for h in self.handlers:
            h(self, e)

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
        logging.warn("stop %s" % get_name(self))
        self._ready.set()

    def input(self):
        """ start a input loop. """
        while not self._stopped:
            e = self.poll()
            self.put(e)

    def load_mod(self, mn, force=True):
        """ load module and scan for functions. """
        mod = super().load_mod(mn, force=force)
        self.scan(mod)
        return mod

    def output(self):
        self._outputed = True
        while not self._stopped:
            channel, txt, type = self._outqueue.get()
            if txt:
                if self.sleep:
                    if (time.time() - self.state.last) < 3.0:
                        time.sleep(1.0 * (self.state.nrsend % 10))
                self._say(channel, txt, type)

    def poll(self):
        """ poll for an event. """
        raise ENOTIMPLEMENTED

    def put(self, event):
        """ put event on queue. """
        self._queue.put_nowait(event)

    def register(self, handler):
        """ register a handler for a command. """
        logging.debug("register %s" % get_name(handler))
        if handler not in self.handlers:
            self.handlers.append(handler)

    def say(self, channel, txt, type="chat"):
        print(txt)

    def scan(self, mod):
        """ scan a module for commands/callbacks. """
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if "event" in o.__code__.co_varnames:
                if o.__code__.co_argcount == 1 and key not in self.cmds:
                    self.cmds[key] = o
                    self.modules[key] = o.__module__
                elif o.__code__.co_argcount == 2 and key not in self.handlers:
                    self.handlers.append(o)
        for key, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, Persist):
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

    def sync(self, other):
        self.handlers = other.handlers
        self.cmds.update(other.cmds)

    def walk(self, pkgname):
        """ scan package for module to load. """
        try:
            mod = self.load_mod(pkgname)
        except ModuleNotFoundError:
            logging.debug("not found %s" % pkgname)
            return []
        mods = [mod,]
        try:
            mns = pkgutil.iter_modules(mod.__path__, mod.__name__+".")
        except:
            mns = pkgutil.iter_modules([mod.__file__,], mod.__name__+".")
        for n in mns:
            skip = False
            for ex in self.cfg.exclude.split(","):
                if ex and ex in n[1]:
                    skip = True
            if skip:
                continue
            logging.warn("load %s" % str(n[1]))
            try:
                mods.append(self.load_mod(n[1], force=True))
            except ModuleNotFoundError:
                logging.debug("not found %s" % n[1])
        for m in mods:
            self.scan(m)
        return mods
