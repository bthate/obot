# OLIB
#
#

import threading, time

from ol.dft import Default
from ol.krn import get_kernel, starttime, __version__
from ol.obj import Object, format, save, get, keys, update
from ol.prs import parse
from ol.tms import elapsed
from ol.utl import get_name

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
    event.reply("OLIB %s" % __version__)
