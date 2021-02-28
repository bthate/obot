# This file is placed in the Public Domain.

"system commands"

# imports

import threading
import time

from . import Object, update
from .hdl import Bus
from .prs import elapsed
from .utl import get_name

# defines

starttime = time.time()

# commands

def flt(event):
    try:
        event.reply(str(Bus.objs[event.index]))
        return
    except (TypeError, IndexError):
        pass
    event.reply(" | ".join([get_name(o) for o in Bus.objs]))

def thr(event):
    psformat = "%s %s"
    result = []
    for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thr).startswith("<_"):
            continue
        o = Object()
        update(o, thr)
        if getattr(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = thr.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s %s" % (txt, elapsed(up)))
    if res:
        event.reply(" | ".join(res))

def upt(event):
    event.reply(elapsed(time.time() - starttime))
