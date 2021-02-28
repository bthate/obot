# This file is placed in the Public Domain.

"shell code"

# imports

import readline
import sys

from . import cfg
from .hdl import Bused
from .prs import parse as p

# defines

def init(h):
    shl = Shell()
    shl.clone(h)
    shl.start()
    return shl

# classes

class Shell(Bused):

    def direct(self, txt):
        pass

# functions

def op(ops):
    for opt in ops:
        if opt in cfg.opts:
            return True
    return False

def parse():
    p(cfg, " ".join(sys.argv[1:]))
    return cfg
