""" timestamped JSON file based object backend. """

import json
import ob
import os
import time

from ob.times import days, fntime
from ob.utils import last

def __dir__():
    return ("Db", "names", "hook", "search", "ed", "find", "rm", "undel")

class Db(ob.Object):

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
            if selector and not search(o, selector):
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
            if "_deleted" not in dir(o):
                continue
            if not o._deleted:
                continue
            if selector and not search(o, selector):
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
            if search(o, selector):
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
        for fn in names(otype, delta):
            o = hook(fn)
            if not o:
                continue
            if selector and search(o, selector):
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

def names(name, delta=None):
    """ show all object filenames on disk. """
    if not name:
        return []
    if not delta:
        delta = 0
    assert ob.WORKDIR
    p = os.path.join(ob.WORKDIR, "store", name) + os.sep
    res = []
    now = time.time()
    past = now + delta
    for rootdir, dirs, files in os.walk(p, topdown=True):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(ob.WORKDIR, "store"))[-1]
            if delta:
                if ime(fnn) < past:
                    continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=fntime)

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

def search(obj, match: None):
    """ do a strict key,value match. """
    if not match:
        match = {}
    res = False
    for key, value in match.items():
        val = getattr(obj, key, None)
        if val:
            if value is None:
                res = True
            elif value in str(val):
                res = True
            else:
                res = False
                break
        else:
            res = False
            break
    return res

def ed(event):
    """ edit an object, select with key==value, set with key=value. """
    from ob.kernel import k
    from ob.generic import edit
    if not event.args:
        fns = os.listdir(os.path.join(ob.WORKDIR, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        event.options += ",f"
        find(event)
        return
    nr = 0
    objs = k.db.find(event.match, event.selector, event.index, event.delta)
    for o in objs:
        got = edit(o, event.setter)
        if got:
            o.save()
            nr += 1
    event.reply("edit %s" % nr)

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
        fn = last(event.match)
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
            txt = "%s %s" % (event.index or nr, format(o, event.dkeys, full))
        else:
            txt = "%s %s" % (event.index or nr, format(o, full=full))
        if "t" in event.options:
            txt += " " + days(o._path)
        txt = txt.rstrip()
        if txt:
            event.reply(txt)

def rm(event):
    """ enable the _deleted flag on an object. """
    if not event.args:
        event.reply("rm <selector>")
        return
    from ob.kernel import k
    nr = -1
    for o in k.db.find(event.match, event.selector, event.index, event.delta):
        if not o:
            continue
        nr += 1
        o._deleted = True
        o.save()
    event.reply("ok %s" % (nr+1))

def undel(event):
    """ remove the _deleted flag from an object. """
    if not event.args:
        event.reply("undel <selector>")
        return
    from ob.kernel import k
    from ob.times import elapsed
    st = time.time()
    nr = -1
    for o in k.db.all(event.match, event.selector, event.index, event.delta):
        nr += 1
        o._deleted = False
        o.save()
    event.reply("ok %s %s" % (nr+1, elapsed(time.time()-st)))
