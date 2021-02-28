# This file is placed in the Public Domain.

"object functions"

import ob

# functions

def edit(o, setter, skip=False):
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, v in ob.items(setter):
        if skip and v == "":
            continue
        count += 1
        if v in ["True", "true"]:
            o[key] = True
        elif v in ["False", "false"]:
            o[key] = False
        else:
            o[key] = v
    return count

def format(o, keys=None, skip=None, empty=True):
    if keys is None:
        keys = vars(o).keys()
    if skip is None:
        skip = []
    res = []
    txt = ""
    for key in keys:
        if key in skip:
            continue
        try:
            val = o[key]
        except KeyError:
            continue
        if empty and not val:
            continue
        val = str(val).strip()
        res.append((key, val))
    result = []
    for k, v in res:
        result.append("%s=%s%s" % (k, v, " "))
    txt += " ".join([x.strip() for x in result])
    return txt.strip()
