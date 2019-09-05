""" test commands. """

import logging
import ob
import obot
import os
import random
import string
import sys
import time
import unittest

from ob.kernel import k
from ob.handler import Event, Handler
from ob.utils import cdir, consume, randomname

class Param(ob.Object):

    pass

param = Param()
e = Event()

def init():
    cdir(os.path.join("testdata", "store", ""))
    ob.workdir = "testdata"
    k.cfg.prompt = False
    k.walk("ob")
    k.walk("obot")
    k.walk("oper")
    k.start()
    k.users.oper("test@shell")
    global param
    global e
    param.ed = ["%s txt==yo channel=#mekker" % x for x in k.names]
    param.ed.extend(["%s txt==yo test=a,b,c,d" % x for x in k.names])
    param.find = ["%s txt==yo" % x for x in k.names]
    param.load = k.table.keys()
    param.log = ["yo!",]
    param.rm = ["%s txt==yo" % x for x in k.names]
    param.show = ["config", "cmds", "fleet", "kernel", "tasks", "version"]
    param.mbox = ["~/evidence/25-1-2013",]
    if k.cfg.args:
        e.parse(" ".join(k.cfg.args))
    try:
        e.index = int(k.cfg.options)
    except ValueError:
        pass

def exceptions(event):
    from ob.trace import exceptions
    for ex in exceptions:
        event.reply(ex)

def tinder(event):
    try:
        nr = int(event.args[0])
    except (IndexError, ValueError):
        nr = 1
    e = Event()
    e.origin = "test@shell"
    thrs = []
    thrs = []
    for x in range(nr):
        for fn in k.cmds:
            logging.debug(fn)
            e.txt = fn + " " + randomname()
            func = k.cmds[fn]
            time.sleep(0.001)
            thrs.append(ob.launch(func, e))
    for thr in thrs:
        thr.join()
    exs = param.get(cmd, [randomname(), randomname()])
    e = list(exs)
    random.shuffle(e)
    events = []
    for ex in e:
        e = Event()
        e.origin = "test@shell"
        e.txt = cmd + " " + ex
        b.put(e)
        events.append(e)
    consume(events)
