""" show list of commands. """

from ob.kernel import k
from ob.loader import load, unload
from ob.handler import Handler, modules

def __dir__():
    return ("cmds", "load", "unload")

def cmds(event):
    event.reply("|".join(sorted([x for x in k.handlers])))
