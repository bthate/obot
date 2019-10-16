""" object query. """

import json
import ob
import os
import time

from ob.pst import Persist
from ob.typ import get_cls
from ob.tms import days, fntime

def __dir__():
    return ("Db", "hook")

cache = {}

class Db(Persist):

    """ database object providing all, deleted, find, last methods. """

    def all(self, otype, selector=None, index=None, delta=0):
        """ show all objects. """
        if not selector:
            selector = {}
        nr = -1
        for fn in names(otype, delta):
            nr += 1
            o = hook(fn)
            if index is not None and nr != index:
                continue
            if selector and not ob.search(o, selector):
                continue
            if "_deleted" in o and o._deleted:
                continue
            yield o

    def deleted(self, otype, selector=None):
        """ show all deleted objects. """
        if not selector:
            selector = {}
        nr = -1
        for fn in names(otype):
            nr += 1
            o = hook(fn)
            if selector and not ob.search(o, selector):
                continue
            if "_deleted" not in o or not o._deleted:
                continue
            yield o

    def find(self, otype, selector=None, index=None, delta=0):
        """ find objects matching otype and selector. """
        if not selector:
            selector = {}
        nr = -1
        for fn in names(otype, delta):
            o = hook(fn)
            if not o:
                continue
            if ob.search(o, selector):
                nr += 1
                if index is not None and nr != index:
                    continue
                if "_deleted" in o and o._deleted:
                    continue
                yield o

    def last(self, type, index=None, delta=0):
        fns = names(type, delta)
        if fns:
            fn = fns[-1]
            return hook(fn)

    def last_all(self, otype, selector=None, index=None, delta=0):
        """ return last object of type otype. """
        if not selector:
            selector = {}
        res = []
        nr = -1
        for fn in names(otype, delta):
            o = hook(fn)
            if not o:
                continue
            if selector and ob.search(o, selector):
                nr += 1
                if index is not None and nr != index:
                    continue
                res.append((fn, o))
            else:
                res.append((fn, o))
        if res:
            s = sorted(res, key=lambda x: fntime(x[0]))
            if s:
                return s[-1][-1]
        return None

def hook(fn):
    """ read json file from fn and create corresponding object. """
    if fn in cache:
        return cache[fn]
    t = fn.split(os.sep)[0]
    if not t:
        raise ob.err.ENOFILE(fn)
    o = get_cls(t)()
    try:
        o.load(fn)
    except ob.err.EEMPTY:
        return o
    except json.decoder.JSONDecodeError:
        raise ob.err.EJSON(fn)
    cache[fn] = o
    return o

def names(name, delta=None):
    """ show all object filenames on disk. """
    if not name:
        return []
    if not delta:
        delta = 0
    assert ob.k.cfg.workdir
    p = os.path.join(ob.k.cfg.workdir, "store", name) + os.sep
    print(p)
    res = []
    now = time.time()
    past = now + delta
    for rootdir, dirs, files in os.walk(p, topdown=True):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(ob.k.cfg.workdir, "store"))[-1]
            if delta:
                if fntime(fnn) < past:
                    continue
            res.append(fnn[1:])
    return sorted(res, key=fntime)
