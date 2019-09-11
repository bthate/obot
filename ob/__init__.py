""" save/load JSON files. """

__version__ = 29

workdir = ""

from ob.obj import update
from ob.typ import get_type
from ob.krn import Kernel

def last(obj, skip=True):
    """ return the last version of this type. """
    val = k.db.last(str(get_type(obj)))
    if val:
        update(obj, val)

#:
k = Kernel()
