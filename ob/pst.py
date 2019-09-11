""" save/load JSON files. """

import datetime
import json
import logging
import ob
import os

from ob.utl import cdir, locked
from ob.typ import get_cls

class Persist:

    """ JSON object persistence. """

    def load(self, path):
        """ load this object from disk. """
        assert path
        assert ob.workdir
        logging.debug("load %s" % path)
        path = os.path.join(ob.workdir, "store", path)
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
        assert ob.workdir
        from ob.cls import get_type
        otype = get_type(self)
        if strict:
            import ob.types
            if otype not in ob.types.classes:
                raise ECLASS(otype)
        if not path:
            try:
                path = self._path
            except AttributeError:
                pass
        if not path:
            if not stime:
                stime = str(datetime.datetime.now()).replace(" ", os.sep)
            path = os.path.join(otype, stime)
        logging.debug("save %s" % path)
        opath = os.path.join(ob.workdir, "store", path)
        cdir(opath)
        logging.debug("save %s" % path)
        self._type = get_type(self)
        self._path = path
        with open(opath, "w") as file:
            json.dump(self, file, default=default, indent=4, sort_keys=True)
        return path

def default(obj):
    """ default an object to JSON. """
    from ob.cls import Dict
    if isinstance(obj, Dict):
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
        from ob.cls import Dict
        o = Dict()
    o.update(d)
    return o

def names(name, delta=None):
    """ show all object filenames on disk. """
    if not name:
        return []
    if not delta:
        delta = 0
    assert ob.workdir
    p = os.path.join(ob.workdir, "store", name) + os.sep
    res = []
    now = time.time()
    past = now + delta
    for rootdir, dirs, files in os.walk(p, topdown=True):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(ob.workdir, "store"))[-1]
            if delta:
                if fntime(fnn) < past:
                    continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=fntime)

