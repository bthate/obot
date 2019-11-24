import logging
import ob
import os
import random
import sys
import time
import unittest

import obot

from ob import Object, k
from ob.evt import Event
from ob.utl import consume, randomname

class Param(Object):

    pass

e = Event()
if k.cfg.options:
    e.parse("-o %s" % k.cfg.options)

events = []

param = Param()
param.ed = ["%s txt==yo channel=#mekker" % x for x in k.names]
param.ed.extend(["%s txt==yo test=a,b,c,d" % x for x in k.names])
param.find = ["%s txt==yo -f" % x for x in k.names] + ["email txt==gif", ]
param.load = k.table.keys()
param.log = ["yo!",]
param.rm = ["%s txt==yo" % x for x in k.names]
param.show = ["config", "cmds", "fleet", "kernel", "tasks", "version"]
param.unload = [k.modules.get(v) for v in k.modules]

#param.mbox = ["~/evidence/25-1-2013",]

class Test_Tinder(unittest.TestCase):

    def tearDown(self):
        print(events)

    def test_tinder(self):
        thrs = []
        for x in range(e.index or 1):
            thrs.append(k.launch(tests, ob.k))
        for thr in thrs:
            thr.join()

    def test_tinder2(self):
        for x in range(e.index or 1):
            tests(k)
        
def tests(b):
    keys = list(b.cmds)
    random.shuffle(keys)
    for cmd in keys:
        if cmd in ["fetch", "exit", "reboot", "reconnect", "tests", "test"]:
            continue
        events.extend(do_cmd(b, cmd))
    consume(events)

def do_cmd(b, cmd):
    exs = ob.get(param, cmd, [randomname(), randomname()])
    e = list(exs)
    random.shuffle(e)
    events = []
    for ex in e:
        e = Event()
        e.origin = "test@shell"
        e.txt = cmd + " " + ex
        b.put(e)
        events.append(e)
    return events
