# OBOT - 24/7 channel daemon
#
#

"object base class (obj)"

import datetime, json, os, uuid, _thread
import ob.utl

sl = _thread.allocate_lock()
wd = ""

class Object:

    "basic object"

    __slots__ = ("__dict__", "__id__")

    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            self.__dict__.update(args[0])
        self.__id__ = str(uuid.uuid4())        

    def __delitem__(self, k):
        del self.__dict__[k]

    def __getitem__(self, k, d=None):
        return self.__dict__.get(k, d)

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

def default(o):
    "return strinfified version of an object"
    if isinstance(o, Object):
        return vars(o)
    if isinstance(o, dict):
        return o.items()
    if isinstance(o, list):
        return iter(o)
    if isinstance(o, (type(str), type(True), type(False), type(int), type(float))):
        return o
    return repr(o)

def get(o, k, d=None):
    "return o[k]"
    try:
        res = o.get(k, d)
    except (TypeError, AttributeError):
        res = o.__dict__.get(k, d)
    return res

def items(o):
    "return items (k,v) of an object"
    try:
        return o.items()
    except (TypeError, AttributeError):
        return o.__dict__.items()

def keys(o):
    "return keys of an object"
    try:
        return o.keys()
    except (TypeError, AttributeError):
        return o.__dict__.keys()

def load(o, path):
    "load from disk into an object"
    assert path
    import ob.krn
    stp = os.sep.join(path.split(os.sep)[-4:])
    lpath = os.path.join(wd, "store", stp)
    ob.utl.cdir(lpath)
    id = stp[1]
    with open(lpath, "r") as ofile:
        try:
            v = json.load(ofile)
        except json.decoder.JSONDecodeError as ex:
            print(path, ex)
            return
        if v:
            o.__dict__.update(v)
    o.__id__ = id

def register(o, k, v):
    "register key/value"
    o[k] = v

def save(o, stime=None):
    "save object to disk"
    import ob.krn
    assert wd
    if stime:
        stp = os.path.join(o.utl.get_type(o), o.__id__,
                             stime + "." + str(random.randint(0, 100000)))
    else:
        timestamp = str(datetime.datetime.now()).split()
        stp = os.path.join(ob.utl.get_type(o), o.__id__, os.sep.join(timestamp))
    opath = os.path.join(wd, "store", stp)
    ob.utl.cdir(opath)
    with open(opath, "w") as ofile:
        json.dump(o, ofile, default=default)
    os.chmod(opath, 0o444)
    return stp

def set(o, k, v):
    "set o[k]=v"
    setattr(o, k, v)

def update(o, d):
    "update object with other object"
    return o.__dict__.update(vars(d))

def values(o):
    "return values of an object"
    try:
        return o.values()
    except (TypeError, AttributeError):
        return o.__dict__.values()
