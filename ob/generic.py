""" works on all objects. """

import ob

def __dir__():
    return ("edit", "format", "sliced")

def edit(obj, setter=None):
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

def format(obj, keys=None, full=False):
    """ return a string that can be displayed. """
    if keys is None:
        keys = vars(obj).keys()
    res = []
    txt = ""
    for key in keys:
        val = getattr(obj, key, None)
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
        txt += "%s " % val.strip()
    return txt.strip()

def sliced(obj, keys=None):
    """ return a new object with the sliced result. """
    val = ob.Object()
    if not keys:
        keys = obj.keys()
    for key in keys:
        try:
            val[key] = obj[key]
        except KeyError:
            pass
    return val

