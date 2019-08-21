""" OB types. """

import os
import importlib
import json

def __dir__():
    return ("get_cls", "get_type")

from ob.errors import ENOFILE, EJSON

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
