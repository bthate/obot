""" object query. """

import json
import ob
import os
import time

from ob.times import days, fntime
from ob.utils import last

def __dir__():
    return ("Db", "hook", "find")

class Db(ob.Object):

    """ database object providing all, deleted, find, last methods. """

    def all(self, otype, selector=None, index=None, delta=0):
        """ show all objects. """
        if not selector:
            selector = {}
        nr = -1
        for fn in ob.names(otype, delta):
            nr += 1
            o = cached(fn)
            if index is not None and nr != index:
                continue
            if selector and not ob.search(o, selector):
                continue
            yield o

    def deleted(self, otype, selector=None):
        """ show all deleted objects. """
        if not selector:
            selector = {}
        nr = -1
        for fn in ob.names(otype):
            nr += 1
            o = cached(fn)
            if "_deleted" not in dir(o):
                continue
            if not o._deleted:
                continue
            if selector and not ob.search(o, selector):
                continue
            yield o

    def find(self, otype, selector=None, index=None, delta=0):
        """ find objects matching otype and selector. """
        if not selector:
            selector = {}
        nr = -1
        for fn in ob.names(otype, delta):
            o = cached(fn)
            if not o:
                continue
            if ob.search(o, selector):
                nr += 1
                if index is not None and nr != index:
                    continue
                yield o

    def last(self, otype, selector=None, index=None, delta=0):
        """ return last object of type otype. """
        if not selector:
            selector = {}
        res = []
        nr = -1
        for fn in ob.names(otype, delta):
            o = cached(fn)
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

cache = {}

def cached(fn):
    global cache
    if fn not in cache:
        cache[fn] = hook(fn)
    return cache[fn]


def hook(fn):
    """ read json file from fn and create corresponding object. """
    t = fn.split(os.sep)[0]
    if not t:
        raise ob.errors.ENOFILE(fn)
    o = ob.types.get_cls(t)()
    try:
        o.load(fn)
    except json.decoder.JSONDecodeError:
        raise ob.errors.EJSON(fn)
    return o

def find(event):
    """ find an object matching to a key==value selector. """
    from ob.generic import format
    from ob.kernel import k
    if "k" in event.options:
        o = k.db.last(event.match)
        if o:
            event.reply("|".join(sorted({x for x in o.keys() if not x.startswith("_")})))
            return
    if not event.args:
        fns = os.listdir(os.path.join(ob.WORKDIR, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        if fns:
            event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        fn = k.db.last(event.match)
        if fn:
            o = ob.Object().load(fn)
            res = sorted({x.split(".")[-1].lower() for x in o})
            if len(res) > 1:
                event.reply("|".join(res))
            else:
                for a in res:
                    if a not in event.selector:
                        event.selector[a] = None
                    if a not in event.dkeys:
                        event.dkeys.append(a)
    nr = -1
    for o in k.db.find(event.match, event.selector, event.index, event.delta):
        nr += 1
        txt = ""
        if "k" in event.options:
            event.reply("|".join(o))
            return
        if "d" in event.options:
            event.reply(str(o))
            continue
        full = False
        if "f" in event.options:
            full = True
        if event.dkeys:
            txt = "%s %s" % (event.index or nr, ob.format(o, event.dkeys, full))
        else:
            txt = "%s %s" % (event.index or nr, ob.format(o, full=full))
        if "t" in event.options:
            txt += " " + days(o._path)
        txt = txt.rstrip()
        if txt:
            event.reply(txt)
