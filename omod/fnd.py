# OBOT - 24/7 channel daemon
#
#

"find objects (fnd)"

import os, time

from ol.dbs import find
from ol.tms import elapsed, fntime
from ol.krn import get_kernel, wd
from ol.obj import get, keys
from ol.ofn import format
from ol.utl import cdir

def fnd(event):
    "locate and show objects on disk"
    if not event.args:
        import ol.krn
        assert ol.krn.wd
        wd = os.path.join(ol.krn.wd, "store", "")
        cdir(wd)
        fns = os.listdir(wd)
        fns = sorted({x.split(os.sep)[0].split(".")[-1].lower() for x in fns})
        if fns:
            event.reply(",".join(fns))
        return
    nr = -1
    args = []
    try:
        args = event.args[1:]
    except IndexError:
        pass
    k = get_kernel()
    types = get(k.names, event.args[0], [event.cmd,])
    for otype in types:
        for fn, o in find(otype, event.prs.gets, event.prs.index, event.prs.timed):
            nr += 1
            pure = True
            if not args:
                args = keys(o)
            if "f" in event.prs.opts:
                pure = False
            txt = "%s %s" % (str(nr), format(o, args, pure, event.prs.skip))
            if "t" in event.prs.opts:
                txt = txt + " %s" % (elapsed(time.time() - fntime(fn)))
            event.reply(txt)
