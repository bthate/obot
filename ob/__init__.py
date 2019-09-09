""" save/load JSON files. """

__version__ = 27

import datetime
import importlib
import json
import logging
import ob
import os
import queue
import readline
import sys
import time
import threading
import _thread

from types import MethodType, FunctionType

from ob.utils import locked, hd
from ob.errors import ECLASS, ENOFILE
from ob.times import fntime
from ob.types import get_cls, get_type

def __dir__():
    return ('ECLASS', 'ENOFILE', 'Cfg', 'Default', "Object", "Register", 'workdir', 'all', 'classes', 'default', 'get', 'hooked', 'last', 'launch', 'set', 'update')

workdir = ""

class Persist:

    """ JSON object persistence. """

    def load(self, path):
        """ load this object from disk. """
        assert path
        assert workdir
        logging.debug("load %s" % path)
        path = os.path.join(workdir, "store", path)
        if not os.path.exists(path):
            assert ENOFILE(path)
        with open(path, "r") as ofile:
            val = json.load(ofile, object_hook=hooked)
            self.update(val)
        return self

    @locked
    def save(self, path="", stime=None, timed=False, strict=False):
        """ save(path="",stime=None, timed=False, strict=False)
        
            save this object to disk.
        """
        assert workdir
        from ob.utils import cdir
        otype = get_type(self)
        if strict:
            import ob.types
            if otype not in ob.types.classes:
                raise ECLASS(otype)
        if not path and "_path" in dir(self):
            path = self._path
        if not path:
            if not stime:
                stime = str(datetime.datetime.now()).replace(" ", os.sep)
            path = os.path.join(otype, stime)
        logging.debug("save %s" % path)
        opath = os.path.join(workdir, "store", path)
        cdir(opath)
        logging.debug("save %s" % path)
        self._type = get_type(self)
        self._path = path
        with open(opath, "w") as file:
            json.dump(self, file, default=default, indent=4, sort_keys=True)
        return path

class Object(Persist, dict):

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

class Default(Object):

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

def default(obj):
    """ default an object to JSON. """
    if isinstance(obj, Object):
        return vars(obj)
    if isinstance(obj, dict):
        return obj.items()
    if isinstance(obj, list):
        return iter(obj)
    otype = type(obj)
    if otype in [str, True, False, int, float]:
        return obj
    return repr(obj)

def hooked(d):
    """ construct obj from _type. """
    if "_type" in d:
        t = d["_type"]
        o = get_cls(t)()
        del d["_type"]
    else:
        from ob import Object
        o = Object()
    o.update(d)
    return o

def names(name, delta=None):
    """ show all object filenames on disk. """
    if not name:
        return []
    if not delta:
        delta = 0
    assert workdir
    p = os.path.join(workdir, "store", name) + os.sep
    res = []
    now = time.time()
    past = now + delta
    for rootdir, dirs, files in os.walk(p, topdown=True):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(workdir, "store"))[-1]
            if delta:
                if fntime(fnn) < past:
                    continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=fntime)
