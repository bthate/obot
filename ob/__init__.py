""" provide persistence through save/load to JSON files. """

__version__ = 27

import datetime
import importlib
import json
import logging
import os
import queue
import readline
import sys
import time
import threading
import _thread

from ob.utils import locked, hd
from ob.errors import ECLASS, ENOFILE
from ob.types import get_cls, get_type

def __dir__():
    iface = ['Cfg', 'Default', 'ECLASS', 'ENOFILE', 'Object', 'WORKDIR', 'all', 'classes', 'default', 'hooked', 'last', 'launch']
    mods = ['all', 'bot', 'clock', 'cmds', 'command', 'db', 'entry', 'errors', 'fleet', 'generic', 'handler', 'kernel', 'loader', 'shell', 'show', 'tasks', 'term', 'times', 'trace', 'types', 'user', 'utils']
    return iface + mods

classes = []
WORKDIR = hd(".ob")

class Object:

    """ JSON object persistence. """

    __slots__ = ("__dict__", "_path", "_ready", "_type")

    def __init__(self):
        super().__init__()
        self._path = ""
        self._ready = threading.Event()
        self._type = get_type(self)

    def __delitem__(self, key):
        del self.__dict__[key]

    def __eq__(self, obj):
        """ check for equality. """
        if isinstance(obj, (Object, dict)):
            return self.__dict__ == obj.__dict__
        return False

    def __getitem__(self, name, default=None):
        """ wrap getattr. """
        return getattr(self, name, default)

    def __hash__(self):
        """ return a hashable version. """
        return hash(self.__dict__)

    def __len__(self):
        """ return number of keys. """
        return len(self.__dict__)

    def __ne__(self, o):
        """ do a not equal test. """
        return self.__dict__ != o.__dict__

    def __iter__(self):
        """ iterate over all elements. """
        return iter(self.__dict__)

    def __setitem__(self, key, val):
        self.__dict__.__setitem__(key, val)

    def __str__(self):
        """ return json string. """
        return json.dumps(self, default=default, indent=4, sort_keys=True)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def load(self, path):
        """ load this object from disk. """
        assert path
        assert WORKDIR
        path = os.path.join(WORKDIR, "store", path)
        if not os.path.exists(path):
            assert ENOFILE(path)
        with open(path, "r") as ofile:
            val = json.load(ofile, object_hook=hooked)
            self.update(val)
        self._path = path
        return self

    @locked
    def save(self, path="", stime=None, timed=False, strict=False):
        """ save this object to disk. """
        assert WORKDIR
        from ob.utils import cdir
        if self._path and not timed:
            path = self._path
        else:
            otype = get_type(self)
            if strict:
                if otype not in classes:
                    raise ECLASS(otype)
            if not stime:
                stime = str(datetime.datetime.now()).replace(" ", os.sep)
            path = os.path.join(otype, stime)
            self._path = path
        logging.debug(self._path)
        opath = os.path.join(WORKDIR, "store", self._path)
        cdir(opath)
        self["_type"] = self._type
        with open(opath, "w") as file:
            json.dump(self, file, default=default, indent=4, sort_keys=True)
        return path

    def typed(self):
        return type(self)().update(self)
                
    def update(self, obj, keys=None, skip=False):
        """ update this object from the data of another. """
        if not obj:
            return self
        for key in obj:
            val = obj[key]
            if keys and key in keys:
                setattr(self, key, val)
                continue
            if skip and not val:
                continue
            setattr(self, key, val)
        return self

class Default(Object):

    """ default empty string value. """

    def __init__(self, cfg=None):
        super().__init__()
        if cfg:
            self.update(cfg)

    def __getattr__(self, key):
        if key not in dir(self):
            setattr(self, key, "")
        return getattr(self, key)


class Cfg(Default):

    """ config with empty string default. """

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

def last(obj):
    """ return the last version of this type. """
    from ob.kernel import k
    val = k.db.last(get_type(obj))
    if val:
        obj.update(val, skip=True)
    return obj

def launch(func, *args):
    """ start a task. """
    from ob.kernel import k
    return k.launch(func, *args)

def hooked(d):
    if "_type" in d:
        t = d["_type"]
        o = get_cls(t)()
    else:
        from ob import Object
        o = Object()
    o.update(d)
    return o

import ob.all
