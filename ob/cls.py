""" class definitions. """

import os
import importlib
import json

from types import MethodType, FunctionType

from ob.pst import Persist, default
from ob.err import ENOFILE, EJSON

def __dir__():
    return ("Dict", "Default", "Cfg", "Register", "get_cls", "get_type")

class Dict(Persist, dict):

    """ persistent dict. """

    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def __str__(self):
        """ return json string. """
        return json.dumps(self, default=default, indent=4, sort_keys=True)

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            super().__getattribute__(k)

    def __setattr__(self, k, v):
        if type(v) in [MethodType, FunctionType]:
            super().__setattr__(k, v)
        else:
            self[k] = v

class Default(Dict):

    """ default empty string value. """

    def __init__(self, cfg=None):
        super().__init__()
        if cfg:
            self.update(cfg)

    def __getattr__(self, k):
        try:
            super().__getattr__(k)
        except AttributeError:
            self[k] = ""
        return self[k]

class Cfg(Default):

    """ config with empty string default. """

class Register(Default):

    """ register key/values on a Default. """

    def register(self, k, v):
        self[k] = v

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
