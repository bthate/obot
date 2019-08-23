""" admin commands. """

import json
import ob
import os
import time

from ob.times import days, fntime
from ob.utils import last

from ob import __version__
from ob.kernel import k
from ob.shell import execute, hd, parse_cli

def ed(event):
    """ edit an object, select with key==value, set with key=value. """
    from ob.kernel import k
    from ob.generic import edit
    if not event.args:
        fns = os.listdir(os.path.join(ob.WORKDIR, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        event.options += ",f"
        find(event)
        return
    nr = 0
    objs = k.db.find(event.match, event.selector, event.index, event.delta)
    for o in objs:
        got = edit(o, event.setter)
        if got:
            o.save()
            nr += 1
    event.reply("edit %s" % nr)

def rm(event):
    """ enable the _deleted flag on an object. """
    if not event.args:
        event.reply("rm <selector>")
        return
    from ob.kernel import k
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
    from ob.kernel import k
    from ob.times import elapsed
    st = time.time()
    nr = -1
    for o in k.db.all(event.match, event.selector, event.index, event.delta):
        nr += 1
        o._deleted = False
        o.save()
    event.reply("ok %s %s" % (nr+1, elapsed(time.time()-st)))

