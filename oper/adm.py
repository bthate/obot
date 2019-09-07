""" admin commands. """

import ob
import os
import time

from ob.kernel import k
from ob.times import elapsed

def editset(obj, setter):
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

def edit(obj, setter):
    """ edit an objects with the setters key/value. """
    if not setter:
        setter = {}
    count = 0
    for key, value in setter.items():
        if "," in value:
            value = value.split(",")
        if value in ["True", "true"]:
            obj[key] = True
        elif value in ["False", "false"]:
            obj[key] = False
        else:
            obj[key] = value
        count += 1
    return count

def ed(event):
    """ edit an object, select with key==value, set with key=value. """
    if not event.args:
        fns = os.listdir(os.path.join(ob.workdir, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        event.reply("ed <type> key==value")
        return
    nr = 0
    objs = k.db.find(event.match, event.selector, event.index, event.delta)
    for o in objs:
        ok = edit(o, event.setter)
        if ok:
            o.save()
            nr += 1
    event.reply("edit %s" % nr)

def rm(event):
    """ enable the _deleted flag on an object. """
    if not event.args:
        event.reply("rm <selector>")
        return
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
    st = time.time()
    nr = -1
    for o in k.db.all(event.match, event.selector, event.index, event.delta):
        nr += 1
        o._deleted = False
        o.save()
    event.reply("ok %s %s" % (nr+1, elapsed(time.time()-st)))
