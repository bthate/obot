""" removed objects. """

import json
import ob
import os
import time

from ob.times import days, fntime
from ob.utils import last

def __dir__():
    return ("rm", "undel")

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
