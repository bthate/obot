# OLIB
#
#

"object base class (obj)"

import datetime, json, os, uuid
import ol.utl

class Object:

    "basic object"

    __slots__ = ("__dict__",)

    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            self.__dict__.update(args[0])

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

def register(o, k, v):
    "register key/value"
    o[k] = v

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


def edit(o, setter, skip=False):
    "update an object from a dict"
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, value in setter.items():
        if skip and value == "":
            continue
        count += 1
        if value in ["True", "true"]:
            o[key] = True
        elif value in ["False", "false"]:
            o[key] = False
        else:
            o[key] = value
    return count

def format(o, keylist=None, pure=False, skip=None, txt="", sep="\n"):
    "return 1 line output string"
    if not keylist:
        keylist = vars(o).keys()
    res = []
    for key in keylist:
        if skip and key in skip:
            continue
        try:
            val = o[key]
        except KeyError:
            continue
        if not val:
            continue
        val = str(val).strip()
        val = val.replace("\n", sep)
        res.append((key, val))
    result = []
    for k, v in res:
        if pure:
            result.append("%s%s" % (v, " "))
        else:
            result.append("%s=%s%s" % (k, v, " "))
    txt += " ".join([x.strip() for x in result])
    return txt

def load(o, path):
    "load from disk into an object"
    assert path
    import ol.krn
    stp = os.sep.join(path.split(os.sep)[-4:])
    lpath = os.path.join(ol.krn.wd, "store", stp)
    ol.utl.cdir(lpath)
    with open(lpath, "r") as ofile:
        try:
            v = json.load(ofile)
        except json.decoder.JSONDecodeError as ex:
            print(path, ex)
            return
        if v:
            o.__dict__.update(v)

def mkstamp(o):
    timestamp = str(datetime.datetime.now()).split()
    return os.path.join(ol.utl.get_type(self), str(uuid.uuid4()), os.sep.join(timestamp))

def ojson(o, *args, **kwargs):
    "return jsonified string"
    return json.dumps(o, default=default, *args, **kwargs)

def save(o, stime=None):
    "save object to disk"
    import ol.krn
    assert ol.krn.wd
    if stime:
        stp = os.path.join(o.utl.get_type(o), str(uuid.uuid4()),
                             stime + "." + str(random.randint(0, 100000)))
    else:
        timestamp = str(datetime.datetime.now()).split()
        if getattr(o, "stp", None):
            try:
                spl = o.stp.split(os.sep)
                spl[-2] = timestamp[0]
                spl[-1] = timestamp[1]
                o.stp = os.sep.join(spl)
            except AttributeError:
                pass
        stp = os.path.join(ol.utl.get_type(o), str(uuid.uuid4()), os.sep.join(timestamp))
    opath = os.path.join(ol.krn.wd, "store", stp)
    ol.utl.cdir(opath)
    with open(opath, "w") as ofile:
        json.dump(o, ofile, default=default)
    os.chmod(opath, 0o444)
    return stp

def scan(o, txt):
    "scan object values for txt"
    for _k, v in items(o):
        if txt in str(v):
            return True
    return False

def search(o, s):
    "search object for a key,value to match dict"
    ok = False
    for k, v in items(s):
        vv = get(o, k)
        if v not in str(vv):
            ok = False
            break
        ok = True
    return ok

def xdir(o, skip=None):
    "return a dir(o) with keys skipped"
    res = []
    for k in dir(o):
        if skip is not None and skip in k:
            continue
        res.append(k)
    return res
 