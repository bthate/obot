"""

OB is a event handler library, uses a timestamped JSON file backend to 
provide persistence, no copyright or LICENSE.

"""

__version__ = 31

import datetime
import json
import os
import types
import uuid

workdir = ""

from ob.typ import get_cls, get_type
from ob.trc import get_from
from ob.utl import locked

class Object:

    __slots__ = ("__dict__", "__cfrom__", "__path__", "__type__")

    def __init__(self):
        super().__init__()
        self.__cfrom__ = get_from(3)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        """ return number of keys. """
        return len(self.__dict__)

    def __str__(self):
        """ return json string. """
        return json.dumps(self, default=default, indent=4, sort_keys=True)

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

def edit(obj, setter):
    """ edit an objects with the setters key/value. """
    if not setter:
        setter = {}
    count = 0
    for key, value in items(setter):
        count += 1
        if "," in value:
            value = value.split(",")
        if value in ["True", "true"]:
            set(obj, key, True)
        elif value in ["False", "false"]:
            set(obj, key, False)
        else:
            set(obj, key, value)
    return count

def eq(obj1, obj2):
    """ check for equality. """
    if isinstance(obj2, (Dict, dict)):
        return obj1.__dict__ == obj2.__dict__
    return False

def format(obj, keys=None, full=False):
    """ return a string that can be displayed. """
    if keys is None:
        keys = vars(obj).keys()
    res = []
    txt = ""
    for key in keys:
        if "ignore" in dir(obj) and key in obj.ignore:
            continue
        val = get(obj, key, None)
        if not val:
            continue
        val = str(val)
        if key == "text":
            val = val.replace("\\n", "\n")
        if full:
            res.append("%s=%s " % (key, val))
        else:
            res.append(val)
    for val in res:
         txt += "%s%s" % (val.strip(), " ")
    return txt.strip()

def get(obj, key, default=None):
    """ get attribute of obj. """
    try:
        return obj[key]
    except (TypeError, KeyError):
        try:
            return obj.__dict__[key]
        except (AttributeError, KeyError):
            return getattr(obj, key, default)

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

def items(obj):
    """ return items of obj. """
    try:
       return obj.__dict__.items()
    except AttributeError:
       return obj.items()
 
def keys(obj):
    """ return keys of object. """
    return obj.__dict__.keys()

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

def ne(obj1, obj2):
    """ do a not equal test. """
    return obj1.__dict__ != obj2.__dict__

def search(obj, match: None):
    """ do a strict key,value match. """
    if not match:
        match = {}
    res = False
    for key, value in items(match):
        val = get(obj, key, None)
        if val:
            if not value:
                res = True
                continue
            if value in str(val):
                res = True
                continue
            else:
                res = False
                break
        else:
            res = False
            break
    return res

def set(obj, key, val):
    """ set attribute on obj. """
    setattr(obj, key, val)

def setter(obj, d):
    """ edit an objects with the setters key/value. """
    if not d:
        d = {}
    count = 0
    for key, value in d.items():
        if "," in value:
            value = value.split(",")
        otype = type(value)
        if value in ["True", "true"]:
            set(obj, key, True)
        elif value in ["False", "false"]:
            set(obj, key, False)
        elif otype == list:
            set(obj, key, value)
        elif otype == str:
            set(obj, key, value)
        else:
            setattr(obj, key, value)
        count += 1
    return count

def sliced(obj, keys=None):
    """ return a new object with the sliced result. """
    import ob
    t = type(obj)
    val = t()
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

def update(obj1, obj2, keys=None, skip=False):
    """ update this object from the data of another. """
    if not obj2:
        return obj1
    for key in obj2:
        val = get(obj2, key)
        if keys and key not in keys:
            continue
        if skip and not val:
            continue
        set(obj1, key, val)

def update2(obj1, obj2):
    obj1.__dict__.update(obj2)

def values(obj):
    """ return values of obj. """
    return obj.__dict__.values()

from ob.krn import Kernel

#:
k = Kernel()

def last(obj, skip=True):
    """ return the last version of this type. """
    val = k.db.last(str(get_type(obj)))
    if val:
        update(obj, val)
        obj.__path__ = val.__path__

