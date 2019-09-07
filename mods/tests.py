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

import ob.trace

from ob.kernel import k
from ob.handler import Event, Handler
from ob.utils import cdir, consume, match, randomname

outtxt = u"Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"

class Param(ob.Object):

    pass

class Event(Event):

    def reply(self, txt):
        k.raw(txt)

skip = ["reboot", "tinder", "tests", "unload"]

param = Param()
e = Event()

def init():
    cdir(os.path.join("testdata", "store", ""))
    ob.workdir = "testdata"
    k.cfg.workdir = "testdata"
    k.cfg.prompt = False
    k.users.oper("test@shell")
    global param
    global e
    param.ed = ["%s txt==yo channel=#mekker" % x for x in k.names]
    param.ed.extend(["%s txt==yo test=a,b,c,d" % x for x in k.names])
    param.find = ["%s txt==yo" % x for x in k.names]
    
    param.load = {x.split(".")[-1] for x in k.modules.values() if not match(x, skip)}
    param.log = ["yo!",]
    param.mbox = ["~/evidence/25-1-2013",]
    param.rm = ["%s txt==yo" % x for x in k.names]
    param.show = ["cfg", "cmds", "fleet", "kernel", "ls", "pid", "tasks", "version"]
    param.unload = {x.split(".")[-1] for x in k.modules.values() if not match(x, skip)}
    if k.cfg.args:
        e.parse(" ".join(k.cfg.args))
    try:
        e.index = int(k.cfg.options)
    except ValueError:
        pass

def exceptions(event):
    for ex in ob.trace.exceptions:
        event.reply(ex)

def reconnect(event):
    bot = k.fleet.get_bot(event.orig)
    if bot:
        bot.announce("reconnect")
        if "_sock" in dir(bot):
            bot._sock.shutdown(2)
            bot._sock.close()

def tinder(event):
    try:
        nr = int(event.args[0])
    except (IndexError, ValueError):
        nr = 10
    events = []
    for x in range(nr):
        for cn in k.cmds:
            if match(cn, skip):
                continue
            for ex in param.get(cn, [randomname(),]):
                e = Event()
                e.origin = "test@shell"
                e.txt = cn + " " + ex
                e.parse()
                logging.debug(e.txt)
                func = k.cmds[cn]
                e._thrs.append(k.launch(func, e))
                events.append(e)
    for e in events:
        e.ready()
    consume(events)

def tinder2(event):
    events = []
    for cn in k.cmds:
        if match(cn, skip):
            continue
        exs = param.get(cn, [randomname(), randomname()])
        for ex in exs:
            e = Event()
            e.origin = "test@shell"
            e.txt = cn + " " + ex
            k.put(e)
        events.append(e)
    for e in events:
        e.ready()
    consume(events)
    
def unicode(event):
    event.reply(outtxt)
    