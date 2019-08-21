""" module loader. """

import importlib
import importlib.util
import ob
import os
import threading
import time

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
    from ob.utils import get_name
    if event.origin != k.cfg.owner:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        from ob.handler import Handler
        h = Handler()
        h.walk("ob")
        event.reply("|".join(sorted(h.table)))
        return
    name = event.args[0]
    mods = k.walk(name)
    k.init(name)
    event.reply("%s loaded" % ",".join([get_name(x) for x in mods]))

def unload(event):
    """ unload a module from the table. """
    from ob.kernel import k
    if event.origin != k.cfg.owner:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join(sorted(k.table)))
        return
    name = event.args[0]
    try:
        del k.table[name]
    except KeyError:
        event.reply("%s is not loaded." % name)
        return
    event.reply("unload %s" % name)
