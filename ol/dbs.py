# OLIB - object library
#
#

import ol
import os

def all(otype, selector=None, index=None, timed=None):
    nr = -1
    if selector is None:
        selector = {}
    for fn in objs(otype, timed):
        o = ol.hook(fn)
        if selector and not ol.search(o, selector):
            continue
        if "_deleted" in o and o._deleted:
            continue
        nr += 1
        if index is not None and nr != index:
            continue
        yield o

def deleted(otype):
    for fn in objs(otype):
        o = ol.hook(fn)
        if "_deleted" not in o or not o._deleted:
            continue
        yield o

def find(otype, selector=None, index=None, timed=None):
    nr = -1
    if selector is None:
        selector = {}
    for fn in objs(otype, timed):
        o = ol.hook(fn)
        if selector and not ol.search(o, selector):
            continue
        if "_deleted" in o and o._deleted:
            continue
        nr += 1
        if index is not None and nr != index:
            continue
        yield o

def find_event(e):
    nr = -1
    for fn in objs(e.otype, e.timed):
        o = ol.hook(fn)
        if e.gets and not ol.search(o, e.gets):
            continue
        if "_deleted" in o and o._deleted:
            continue
        nr += 1
        if e.index is not None and nr != e.index:
            continue
        yield o

def last(o):
    path, l = lastfn(str(ol.get_type(o)))
    if  l:
        ol.update(o, l)
        o.__stamp__ = path

def lasttype(otype):
    fns = objs(otype)
    if fns:
        return ol.hook(fns[-1])

def lastfn(otype):
    fns = objs(otype)
    if fns:
        fn = fns[-1]
        return (fn, ol.hook(fn))
    return (None, None)

def names(name, timed=None):
    if not name:
        return []
    assert ol.wd
    p = os.path.join(ol.wd, "store", name) + os.sep
    res = []
    for rootdir, _dirs, files in os.walk(p, topdown=False):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(ol.wd, "store"))[-1]
            ftime = ol.tms.fntime(fnn)
            if timed and "from" in timed and timed["from"] and ftime < timed["from"]:
                continue
            if timed and timed.to and ftime > timed.to:
                continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=olib.tms.fntime)

def objs(name, timed=None):
    if not name:
        return []
    assert ol.wd
    p = os.path.join(ol.wd, "store", name) + os.sep
    res = []
    d = ""
    for rootdir, dirs, _files in os.walk(p, topdown=False):
        if dirs:
            d = sorted(dirs)[-1]
            if d.count("-") == 2:
                dd = os.path.join(rootdir, d)
                fls = sorted(os.listdir(dd))
                if fls:
                    p = os.path.join(dd, fls[-1])
                    if timed and "from" in timed and timed["from"] and ol.tms.fntime(p) < timed["from"]:
                        continue
                    if timed and timed.to and ol.tms.fntime(p) > timed.to:
                        continue
                    res.append(p)
    return sorted(res, key=ol.tms.fntime)
