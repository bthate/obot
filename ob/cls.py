""" class definitions. """

import ob
import os
import importlib
import json

from types import MethodType, FunctionType

from ob import default, get, set, update
from ob.pst import Persist
from ob.err import ENOFILE, EJSON
from ob.trc import get_from

def __dir__():
    return ("Default", "Cfg", "Register", "get_cls", "get_type")

class Default(Persist):

    def __init__(self, cfg=None):
        super().__init__()
        if cfg:
            update(self, cfg)

    def __getattr__(self, k):
        if not k in self:
            set(self, k, "")
        return get(self, k)

class Cfg(Default):

    pass

class Register(Persist):

    def get(self, k, d=None):
        return ob.get(self, k, d)

    def register(self, k, v):
        ob.set(self, k, v)

def get_cls(name):
    modname, clsname = name.rsplit(".", 1)
    mod = importlib.import_module(modname)
    return getattr(mod, clsname)

def get_type(o):
    t = type(o)
    if t == type:
        return get_vartype(o)
    return str(type(o)).split()[-1][1:-2]

def get_clstype(o):
    try:
        return "%s.%s" % (o.__class__.__module__, o.__class__.__name__)
    except AttributeError:
        pass

def get_objtype(o):
    try:
        return "%s.%s" % (o.__self__.__module__, o.__self__.__name__)
    except AttributeError:
        pass

def get_vartype(o):
    try:
        return "%s.%s" % (o.__module__, o.__name__)
    except AttributeError:
        pass
