# OBOT - 24/7 channel daemon
#
#

"object base class (obj)"

from ob.obj import get, items

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

def mkstamp(o):
    timestamp = str(datetime.datetime.now()).split()
    return os.path.join(ol.utl.get_type(self), str(uuid.uuid4()), os.sep.join(timestamp))

def ojson(o, *args, **kwargs):
    "return jsonified string"
    return json.dumps(o, default=default, *args, **kwargs)

def scan(o):
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
 