""" show list of commands. """

from ob.kernel import k
from ob.loader import load, unload
from ob.handler import Handler, modules

def __dir__():
    return ("cmds", "help", "load", "mods", "unload")

def cmds(event):
    event.reply("|".join(sorted([x for x in k.handlers])))

def help(event):
    h = Handler()
    h.walk("ob")
    h.walk("obot")
    h.walk(k.cfg.name)
    res = []
    for key, mod in h.table.items():
        res.append("%s - %s" % (key.split(".")[-1], mod.__doc__.strip()))
    event.reply(event.sep.join(res))

def mods(event):
    h = Handler()
    h.walk("ob")
    h.walk("obot")
    h.walk(k.cfg.name)
    event.reply("|".join({x.split(".")[-1] for x in modules.values()}))
