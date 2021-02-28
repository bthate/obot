# This file is placed in the Public Domain.

"event handler"

# imports

import os
import queue
import threading
import time

from . import Object, ObjectList, Cfg, Default, items, update
from .itr import find_cmds, walk
from .prs import parse
from .thr import launch
from .utl import direct, has_mod, locked, spl

import _thread

# defines

loadlock = _thread.allocate_lock()

# classes

class Bus(Object):

    objs = []

    def __call__(self, *args, **kwargs):
        return Bus.objs

    def __iter__(self):
        return iter(Bus.objs)

    @staticmethod
    def add(obj):
        Bus.objs.append(obj)

    @staticmethod
    def announce(txt, skip=None):
        for h in Bus.objs:
            if skip is not None and isinstance(h, skip):
                continue
            if "announce" in dir(h):
                h.announce(txt)

    @staticmethod
    def by_orig(orig):
        for o in Bus.objs:
            if repr(o) == orig:
                return o

    @staticmethod
    def say(orig, channel, txt):
        for o in Bus.objs:
            if repr(o) == orig:
                o.say(channel, str(txt))

class Event(Default):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.channel = ""
        self.done = threading.Event()
        self.orig = None
        self.result = []
        self.thrs = []
        self.type = "event"
        self.txt = ""

    def direct(self, txt):
        Bus.say(self.orig, self.channel, txt)

    def parse(self):
        parse(self, self.txt)

    def ready(self):
        self.done.set()

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            self.direct(txt)

    def wait(self, timeout=1.0):
        self.done.wait(timeout)
        for thr in self.thrs:
            thr.join()

class Command(Event):

    def __init__(self, txt, **kwargs):
        super().__init__([], **kwargs)
        self.type = "cmd"
        if txt:
            self.txt = txt.rstrip()

class Handler(Object):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.cbs = Object()
        self.cfg = Cfg()
        self.cmds = Object()
        self.pnames = Object()
        self.modnames = Object()
        self.names = ObjectList()
        self.queue = queue.Queue()
        self.started = []
        self.stopped = False
        self.table = Object()
        if not args:
            from .tbl import tbl
        else:
            tbl = args[0]
        update(self.names, tbl["names"])
        update(self.modnames, tbl["modnames"])
        update(self.pnames, tbl["pnames"])

    def add(self, cmd, func):
        self.cmds[cmd] = func

    def announce(self, txt):
        self.direct(txt)

    def clone(self, hdl):
        update(self.cmds, hdl.cmds)
        update(self.cbs, hdl.cbs)
        update(self.modnames, hdl.modnames)
        update(self.names, hdl.names)
        update(self.pnames, hdl.pnames)
        self.table = hdl.table

    def cmd(self, txt):
        c = Command(txt)
        c.orig = repr(self)
        cmd(self, c)
        c.wait()

    def direct(self, txt):
        pass

    def dispatch(self, event):
        if event.type and event.type in self.cbs:
            self.cbs[event.type](self, event)

    def get_cmd(self, cmd):
        if cmd not in self.cmds:
            mn = getattr(self.modnames, cmd, None)
            if mn:
                mod = self.load(mn)
        return getattr(self.cmds, cmd, None)

    def get_mod(self, mn):
        if mn in self.table:
            return self.table[mn]

    def get_names(self, nm):
        return getattr(self.names, nm, [nm,])

    def init(self, mns):
        thrs = []
        for mn in spl(mns):
            mn = getattr(self.pnames, mn, mn)
            mod = self.get_mod(mn)
            if mod and "init" in dir(mod):
                thrs.append(launch(mod.init, self))
        return thrs

    def input(self):
        while not self.stopped:
            try:
                e = self.poll()
            except EOFError:
                break
            self.put(e)
            e.wait()

    @locked(loadlock)
    def load(self, mn):
        mod = direct(mn)
        update(self.cmds, find_cmds(mod))
        self.table[mn] = mod
        return mod

    def load_mod(self, mns):
        mods = []
        for mn in spl(mns):
            mn = getattr(self.pnames, mn, mn)
            mods.append(self.load(mn))
        return mods

    def handler(self):
        self.running = True
        while not self.stopped:
            e = self.queue.get()
            if not e:
                break
            if not e.orig:
                e.orig = repr(self)
            e.thrs.append(launch(self.dispatch, e))

    def put(self, e):
        self.queue.put_nowait(e)

    def register(self, name, callback):
        self.cbs[name] = callback

    def say(self, channel, txt):
        self.direct(txt)

    def scandir(self, path, name=""):
        if not os.path.exists(path):
            return
        if not name:
            name = path.split(os.sep)[-1]
        for mn in [x[:-3] for x in os.listdir(path)
                   if x and x.endswith(".py")
                   and not x.startswith("__")
                   and not x == "setup.py"]:
            fqn = "%s.%s" % (name, mn)
            if not has_mod(fqn):
                continue
            self.load(fqn)

    def start(self):
        launch(self.handler)

    def stop(self):
        self.stopped = True
        self.queue.put(None)

    def walk(self, nms="ok"):
        w = walk(nms)
        update(self, w)
        for c, mn in items(w.modnames):
            if has_mod(mn):
                self.load(mn)

    def wait(self):
        while not self.stopped:
            time.sleep(30.0)

class Core(Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register("cmd", cmd)

class Bused(Core):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Bus.add(self)

# functions

def cmd(handler, obj):
    obj.parse()
    res = None
    f = handler.get_cmd(obj.res.cmd)
    if f:
        res = f(obj)
        obj.show()
    obj.ready()
    return res
