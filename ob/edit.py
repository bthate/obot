""" object query. """

import json
import ob
import os
import time

from ob.times import days, fntime
from ob.utils import last

def __dir__():
    return ("ed")

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
