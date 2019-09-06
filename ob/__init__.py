""" save/load JSON files. """

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
from ob.times import fntime
from ob.types import get_cls, get_type

def __dir__():
    return ('Cfg', 'Default', 'ECLASS', 'ENOFILE', 'Object', 'workdir', 'all', 'classes', 'default', 'get', 'hooked', 'last', 'launch', 'set', 'update')

workdir = ""

class Object:

    """ JSON object persistence. """

    __slots__ = ("__dict__", "_path", "_ready", "_type")

    def __init__(self):
        """ sets _path, _ready and _type. """
        super().__init__()
        self._path = ""
        self._ready = threading.Event()
        self._type = get_type(self)

    def __delitem__(self, key):
        """ remove item. """
        del self.__dict__[key]

    def __eq__(self, obj):
        """ check for equality. """
        if isinstance(obj, (Object, dict)):
            return self.__dict__ == obj.__dict__
        return False

    def __getitem__(self, name, default=None):
        """ wrap getattr. """
        return self.get(name, default)

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
        return self.set(key, val)

    def __str__(self):
        """ return json string. """
        return json.dumps(self, default=default, indent=4, sort_keys=True)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()
        
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
            update(self, val)
        self._path = path
        return self

    @locked
    def save(self, path="", stime=None, timed=False, strict=False):
        """ save this object to disk. """
        assert workdir
        from ob.utils import cdir
        if self._path and not timed:
            path = self._path
        else:
            otype = get_type(self)
            if strict:
                import ob.types
                if otype not in ob.types.classes:
                    raise ECLASS(otype)
            if not stime:
                stime = str(datetime.datetime.now()).replace(" ", os.sep)
            path = os.path.join(otype, stime)
            self._path = path
        logging.debug("save %s" % path)
        opath = os.path.join(workdir, "store", path)
        cdir(opath)
        self["_type"] = self._type
        logging.debug("save %s" % self._path)
        with open(opath, "w") as file:
            json.dump(self, file, default=default, indent=4, sort_keys=True)
        return path

    def set(self, key, val):
        setattr(self, key, val)

    def values(self):
        return self.__dict__.values()

    def update(self, val):
        return self.__dict__.update(val)

class Default(Object):

    """ default empty string value. """

    def __init__(self, cfg=None):
        super().__init__()
        if cfg:
            update(self, cfg)

    def __getattr__(self, key):
        if key not in dir(self):
            self.set(key, "")
        return self.get(key)

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

def format(obj, keys=None, full=False):
    """ return a string that can be displayed. """
    if keys is None:
        keys = vars(obj).keys()
    res = []
    txt = ""
    for key in keys:
        val = obj.get(key, None)
        if key == "text":
            val = val.replace("\\n", "\n")
        if not val:
            continue
        val = str(val)
        if full:
            res.append("%s=%s " % (key, val))
        else:
            res.append(val)
    for val in res:
        txt += "%s " % val.strip()
    return txt.strip()


def last_fn(otype):
    val = k.db.last(str(get_type(obj)))
    
def last(obj, skip=True):
    """ return the last version of this type. """
    from ob.kernel import k
    val = k.db.last(str(get_type(obj)))
    if val:
        update(obj, val, skip=skip)

def launch(func, *args):
    """ start a task. """
    from ob.tasks import Launcher
    l = Launcher()
    return l.launch(func, *args)

def hooked(d):
    """ construct obj from _type. """
    if "_type" in d:
        t = d["_type"]
        o = get_cls(t)()
    else:
        from ob import Object
        o = Object()
    update(o, d)
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
                if ime(fnn) < past:
                    continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=fntime)

def search(obj, match: None):
    """ do a strict key,value match. """
    if not match:
        match = {}
    res = False
    for key, value in match.items():
        val = obj.get(key, None)
        if val:
            if value is None:
                res = True
                continue
            if value in str(val):
                res = True
                continue
        else:
            res = False
            break
    return res

def sliced(obj, keys=None):
    """ return a new object with the sliced result. """
    val = ob.Object()
    if not keys:
        keys = obj.keys()
    for key in keys:
        try:
            val[key] = obj[key]
        except KeyError:
            pass
    return val

def typed(obj):
    """ return a types copy of obj. """
    return update(type(obj)(), obj)

def update(obj1, obj2, keys=None, skip=False, orig=False):
    """ update this object from the data of another. """
    if not obj2:
        return obj1
    for key in obj2:
        val = obj2[key]
        if keys and key not in keys:
            continue
        if skip and not val:
            continue
        if orig and obj1.get(key, None):
            continue
        obj1.set(key, val)
    return obj1
