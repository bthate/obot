import logging
import ob
import os
import random
import sys
import time
import unittest

from ob.kernel import k
from ob.handler import Event

def consume(elems):
    fixed = []
    for e in elems:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            elems.remove(f)
        except ValueError:
            continue

class Param(ob.Object):

    pass

bot = ob.bot.Bot()
bot.cfg.prompt = False
bot.cfg.verbose = k.cfg.verbose
bot.walk("ob")
bot.walk("oper")
bot.walk("obot")
bot.start()

e = Event()
if k.cfg.args:
    e.parse(" ".join(k.cfg.args))
try:
    e.index = int(k.cfg.options)
except ValueError:
    pass
k.users.oper("test@shell")

param = Param()
param.ed = ["%s txt==yo channel=#mekker" % x for x in ob.handler.names]
param.ed.extend(["%s txt==yo test=a,b,c,d" % x for x in ob.handler.names])
param.find = ["%s txt==yo" % x for x in ob.handler.names]
param.load = bot.table.keys()
param.log = ["yo!",]
param.rm = ["%s txt==yo" % x for x in ob.handler.names]
param.show = ["config", "cmds", "fleet", "kernel", "tasks", "version"]
#param.mbox = ["~/evidence/25-1-2013",]

class Test_Tinder(unittest.TestCase):

    def test_tinder(self):
        thrs = []
        for x in range(e.index or 1):
            thrs.append(ob.launch(tests, bot))
        for thr in thrs:
            thr.join()

    def test_tinder2(self):
        for x in range(e.index or 1):
            tests(bot)
        
def tests(b):
    keys = list(b.handlers.keys())
    random.shuffle(keys)
    for cmd in keys:
        if cmd in ["fetch", "exit", "reboot", "reconnect", "test"]:
            continue
        do_cmd(b, cmd)

def do_cmd(b, cmd):
    exs = ob.get(param, cmd, ["mekker",])
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
