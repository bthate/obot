""" save/load JSON files. """

from ob.types import get_type

def edit(obj, setter):
    """ edit an objects with the setters key/value. """
    if not setter:
        setter = {}
    count = 0
    for key, value in setter.items():
        count += 1
        if "," in value:
            value = value.split(",")
        if value in ["True", "true"]:
            obj[key] = True
        elif value in ["False", "false"]:
            obj[key] = False
        else:
            obj[key] = value
    return count

def eq(obj1, obj2):
    """ check for equality. """
    if isinstance(obj2, (Object, dict)):
        return obj1.__dict__ == obj2.__dict__
    return False

def format(obj, keys=None, full=False):
    """ return a string that can be displayed. """
    if keys is None:
        keys = vars(obj).keys()
    res = []
    txt = ""
    for key in keys:
        val = obj.get(key, None)
        if key == "text":
            val = val.replace("\\n", "\n")
        if not val:
            continue
        val = str(val)
        if full:
            res.append("%s=%s " % (key, val))
        else:
            res.append(val)
    for val in res:
        if "sep" in obj:
            txt += "*%s%s" % (val.strip(), obj.sep)
        else:
            txt += "*%s%s" % (val.strip(), " ")
    return txt.strip()


def get(obj, key, default=None):
    """ get attribute of obj. """
    return getattr(obj, key, default)

def items(obj):
    """ return items of obj. """
    return obj.__dict__.items()

def keys(obj):
    """ return keys of object. """
    try:
        return obj.__dict__.keys()
    except:
        return obj.keys()

def last(obj, skip=True):
    """ return the last version of this type. """
    from ob.kernel import k
    val = k.db.last(str(get_type(obj)))
    if val:
        update(obj, val)

def ne(obj1, obj2):
    """ do a not equal test. """
    return obj1.__dict__ != obj2.__dict__


def search(obj, match: None):
    """ do a strict key,value match. """
    if not match:
        match = {}
    res = False
    for key, value in match.items():
        val = get(obj, key, None)
        if val:
            if value is None:
                res = True
                continue
            if value in str(val):
                res = True
                continue
        else:
            res = False
            break
    return res

def set(obj, key, val):
    """ set attribute on obj. """
    setattr(obj, key, val)

def setobj(obj, setter):
    """ edit an objects with the setters key/value. """
    if not setter:
        setter = {}
    count = 0
    for key, value in setter.items():
        if "," in value:
            value = value.split(",")
        otype = type(value)
        if value in ["True", "true"]:
            setattr(obj, key, True)
        elif value in ["False", "false"]:
            setattr(obj, key, False)
        elif otype == list:
            setattr(obj, key, value)
        elif otype == str:
            setattr(obj, key, value)
        else:
            setattr(obj, key, value)
        count += 1
    return count

def sliced(obj, keys=None):
    """ return a new object with the sliced result. """
    import ob
    val = ob.Object()
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
        return 
    for key in obj2:
        val = obj2[key]
        if keys and key not in keys:
            continue
        if skip and not val:
            continue
        setattr(obj1, key, val)

def values(obj):
    """ return values of obj. """
    return obj.__dict__.values()

