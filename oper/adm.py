""" admin commands. """

import ob
import os
import time

from ob.kernel import k
from ob.obj import edit
from ob.times import elapsed

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
    objs = k.db.find(event.match, event.selector, event.index, event.delta)
    nr = 0
    for o in objs:
        edit(o, event.setter)
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
