# OBOT - 24/7 channel daemon
#
#

__version__ = 21

import threading, time

from ob.dft import Default
from ob.krn import get_kernel, starttime
from ob.obj import Object, get, keys, save, update
from ob.ofn import format
from ob.prs import parse
from ob.tms import elapsed
from ob.utl import get_name

def cmd(event):
    "list commands (cmd)"
    k = get_kernel()
    c = sorted(keys(k.cmds))
    if c:
        event.reply(",".join(c))

def cfg(event):
    "configure irc."
    k = get_kernel()
    o = Default()
    parse(o, event.prs.otxt)
    if o.sets:
        update(k.cfg, o.sets)
        save(k.cfg)
    event.reply(format(k.cfg))

def tsk(event):
    "list tasks (tsk)"
    psformat = "%s %s"
    result = []
    for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thr).startswith("<_"):
            continue
        o = Object()
        update(o, thr)
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = thr.getName()
        result.append((up, psformat % (thrname, elapsed(up))))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append(txt)
    if res:
        event.reply(" | ".join(res))

def ver(event):
    "show version (ver)"
    import ob.krn
    event.reply("OBOT %s" % __version__)
