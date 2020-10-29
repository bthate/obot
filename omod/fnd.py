# OBOT - 24/7 channel daemon
#
#

"find objects (fnd)"

import os, time
import ob.obj

from ob.dbs import find
from ob.tms import elapsed, fntime
from ob.krn import get_kernel
from ob.obj import get, keys
from ob.ofn import format
from ob.utl import cdir

def fnd(event):
    "locate and show objects on disk"
    if not event.args:
        assert ob.obj.wd
        wd = os.path.join(ob.obj.wd, "store", "")
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
