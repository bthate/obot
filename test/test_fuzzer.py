# This file is placed in the Public Domain.

"fuzz arguments"

# imports

import inspect
import ob
import ob.hdl
import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

from ob import cfg
from ob.hdl import Event, Handler
from ob.itr import find_mods
from ob.shl import parse
from ob.utl import get_exception, mods

# defines

def cb(event):
    print("yoo")

exclude = ["poll", "handler", "input", "doconnect", "raw", "start"]
exc = []
result = []

values = ob.Object()
values["txt"] = "yoo"
values["key"] = "txt"
values["value"] = ob.Object()
values["d"] = {}
values["hdl"] = Handler()
values["event"] = Event({"txt": "thr", "error": "test"})
values["path"] = cfg.wd
values["channel"] = "#operbot"
values["orig"] = repr(values["hdl"])
values["obj"] = ob.Object()
values["d"] = {}
values["value"] = 1
values["pkgnames"] = "op"
values["name"] = "operbot"
values["callback"] = cb
values["e"] = Event()
values["mod"] = ob.hdl.cmd
values["mns"] = "irc,udp,rss"
values["sleep"] = 60.0
values["func"] = cb
values["origin"] = "test@shell"
values["perm"] = "USER"
values["permission"] = "USER"
values["text"] = "yoo"
values["server"] = "localhost"
values["nick"] = "bot"
values["rssobj"] = ob.Object()
values["o"] = ob.Object()
values["handler"] = Handler()

# classes

class Test_Fuzzer(unittest.TestCase):

    def test_fuzz(self):
        global exc
        m = find_mods("ob,obot")
        for x in range(cfg.index or 1):
            for mod in m:
                fuzz(mod)
        exc = []

# functions

def get_values(vars):
    args = []
    for k in vars:
        res = ob.get(values, k, None)
        if res:
            args.append(res)
    return args

def handle_type(ex):
    if cfg.debug and cfg.verbose:
        print(ex)

def fuzz(mod, *args, **kwargs):
    for name, o in inspect.getmembers(mod, inspect.isclass):
        o.stopped = True
        if "_" in name:
            continue
        try:
            oo = o()
        except TypeError as ex:
            handle_type(ex)
            continue
        for name, meth in inspect.getmembers(oo):
            if "_" in name or name in exclude:
                continue
            try:
                spec = inspect.getfullargspec(meth)
                args = get_values(spec.args[1:])
            except TypeError as ex:
                handle_type(ex)
                continue
            if cfg.debug and cfg.verbose:
                print(meth)
            try:
                res = meth(*args, **kwargs)
                if cfg.debug:
                    print("%s(%s) -> %s" % (name, ",".join([str(x) for x in args]), res))
            except Exception as ex:
                if cfg.debug:
                    print(get_exception())
