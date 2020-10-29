# OLIB
#
#

"module loader (ldr)"

import importlib

from ol.obj import Object

class Loader(Object):

    "holds modules table"

    #:
    table = Object()

    def load(self, name):
        "load module"
        if name not in self.table:
            self.table[name] = importlib.import_module(name)
        return self.table[name]