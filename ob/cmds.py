""" show list of commands. """

from ob.kernel import k
from ob.handler import Handler

def __dir__():
    return ("cmds", "mods")

def cmds(event):
    event.reply("|".join(sorted([x for x in k.handlers])))

def mods(event):
    h = Handler()
    h.walk("mods")
    h.walk("ob")
    h.walk("obot")
    h.walk(k.cfg.name)
    event.reply("|".join([x.split(".")[-1] for x in h.table.keys() if x not in ["mods", "ob", "obot", k.cfg.name]]))
