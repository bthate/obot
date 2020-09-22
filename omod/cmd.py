# OLIB - object library
#
#

import ol
import threading
import time

def cmd(event):
    k = ol.krn.get_kernel()
    c = sorted(k.cmds)
    if c:
        event.reply(",".join(c))

def mds(event):
    mm = ol.utl.find_modules("omod")
    if mm:
        event.reply(",".join([m.__name__.split(".")[-1] for m in mm]))

def tsk(event):
    psformat = "%s %s"
    result = []
    for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thr).startswith("<_"):
            continue
        d = vars(thr)
        o = ol.Object()
        ol.update(o, d)
        if ol.get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - ol.krn.starttime)
        thrname = thr.getName()
        result.append((up, psformat % (thrname, ol.tms.elapsed(up))))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append(txt)
    event.reply(" | ".join(res))

def ver(event):
    k = ol.krn.get_kernel()
    mods = k.walk("ol,omod")
    event.reply(",".join(["%s %s" % (mod.__name__, mod.__version__) for mod in mods if ol.get(mod, "__version__")]))
