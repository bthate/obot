""" module loader. """

import importlib
import importlib.util
import logging
import ob
import os
import threading
import time

from ob.shell import set_completer
from ob.trace import get_exception
from ob.utils import get_name

def __dir__():
    return ("Loader", "load", "unload")

class Loader(ob.Object):

    """ load modules into Loader.table. """

    def __init__(self):
        super().__init__()
        self.table = {}

    def direct(self, name):
        """ do a direct import. """
        return importlib.import_module(name)

    def load_mod(self, name, mod=None):
        """ load a module into the table. """
        self.table[name] = mod or self.direct(name)
        return self.table[name]

    def unload(self, modname):
        """ unload a module from the table. """
        if modname in self.table:
            del self.table[modname]

def load(event):
    """ load a module into the kernel. """
    from ob.kernel import k
    if event.origin != k.cfg.owner:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    mods = []
    for name in event.args[0].split(","):
        name = event.args[0]
        mods.extend(k.walk(name))
        k.init(name)
    set_completer(k.cmds)
    event.reply("%s loaded" % ",".join([get_name(x) for x in mods]))

def unload(event):
    """ unload a module from the table. """
    from ob.kernel import k
    if event.origin != k.cfg.owner:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    bot = k.fleet.get_bot(event.orig)
    name = event.args[0]
    for key in k.modules:
        mn = k.modules[key]
        if name in mn:
            k.handlers.remove(key)
            del k.cmds[key]
    todo = []
    for key in k.table:
        if name in key:
           todo.append(key)
    for key in todo:
        try:
            del k.table[key]
        except KeyError:
            event.reply("%s is not loaded." % name)
            return
    set_completer(k.cmds)
    event.reply("unload %s" % name)
