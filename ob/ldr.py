""" module loader. """

import importlib
import importlib.util
import logging
import ob
import os
import threading
import time

from ob.pst import Persist
from ob.shl import set_completer
from ob.trc import get_exception
from ob.utl import get_name, mods

def __dir__():
    return ("Loader",)

class Loader(Persist):

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
