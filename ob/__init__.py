# This file is placed in the Public Domain.

"object class"

# imports

import datetime
import json
import os
import random
import uuid

# exceptions

class ENOFILENAME(Exception):

    pass

# classes

class O:

    __slots__ = ("__dict__",)

    def __delitem__(self, k):
        try:
            del self.__dict__[k]
        except KeyError:
            pass

    def __getitem__(self, k):
        return self.__dict__[k]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __lt__(self, o):
        return len(self) < len(o)

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __str__(self):
        return json.dumps(self, default=default, sort_keys=True)

class Object(O):

    __slots__ = ("__id__", "__type__", "__stp__")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__id__ = str(uuid.uuid4())
        self.__type__ = get_type(self)
        if args:
            try:
                v = vars(args[0])
            except TypeError:
                v = args[0]
            self.__dict__.update(v)

class ObjectList(Object):

    def append(self, key, value):
        if key not in self:
            self[key] = []
        if value in self[key]:
            return
        if isinstance(value, list):
            self[key].extend(value)
        else:
            self[key].append(value)

    def update(self, d):
        for k, v in items(d):
            self.append(k, v)

class Default(Object):

    default = ""

    def __getattr__(self, k):
        try:
            return super().__getattribute__(k)
        except AttributeError:
            try:
                return super().__getitem__(k)
            except KeyError:
                return self.default

class Cfg(Default):

    pass

# object functions

def get(o, k, d=None):
    if isinstance(o, dict):
        return o.get(k, d)
    return o.__dict__.get(k, d)

def items(o):
    try:
        return o.items()
    except AttributeError:
        return o.__dict__.items()

def keys(o):
    return o.__dict__.keys()

def load(o, opath):
    assert opath
    assert cfg.wd
    if opath.count(os.sep) != 3:
        raise ENOFILENAME(opath)
    spl = opath.split(os.sep)
    stp = os.sep.join(spl[-4:])
    lpath = os.path.join(cfg.wd, "store", stp)
    typ = spl[0]
    oid = spl[1]
    with open(lpath, "r") as ofile:
        try:
            v = json.load(ofile, object_hook=Object)
        except json.decoder.JSONDecodeError as ex:
            return
        if v:
            update(o, v)
    o.__id__ = oid
    o.__type__ = typ
    o.__stp__ = stp
    return stp

def register(o, k, v):
    o[k] = v

def save(o, stime=None):
    assert cfg.wd
    if stime:
        stp = os.path.join(o.__type__, o.__id__,
                           stime + "." + str(random.randint(0, 100000)))
    else:
        timestamp = str(datetime.datetime.now()).split()
        stp = os.path.join(o.__type__, o.__id__, os.sep.join(timestamp))
    opath = os.path.join(cfg.wd, "store", stp)
    cdir(opath)
    with open(opath, "w") as ofile:
        json.dump(o, ofile, default=default)
    os.chmod(opath, 0o444)
    o.__stp__ = stp
    return stp

def set(o, k, v):
    setattr(o, k, v)

def update(o, d):
    try:
        return o.__dict__.update(vars(d))
    except TypeError:
        return o.__dict__.update(d)

def values(o):
    return o.__dict__.values()

# functions

def cdir(path):
    if os.path.exists(path):
        return
    res = ""
    path2, _fn = os.path.split(path)
    for p in path2.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
            os.chmod(padje, 0o700)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass

def get_type(o):
    t = type(o)
    if t == type:
        try:
            return "%s.%s" % (o.__module__, o.__name__)
        except AttributeError:
            pass
    return str(type(o)).split()[-1][1:-2]

def default(o):
    if isinstance(o, Object):
        return vars(o)
    if isinstance(o, dict):
        return o.items()
    if isinstance(o, list):
        return iter(o)
    if isinstance(o, (type(str), type(True), type(False), type(int), type(float))):
        return o
    return repr(o)

# runtime

cfg = Cfg()
cfg.debug = False
cfg.mods = ""
cfg.verbose = False
cfg.wd = ""
