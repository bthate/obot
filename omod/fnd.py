# OLIB - object library
#
#

import ol
import os
import time

def fnd(event):
    if not event.args:
        wd = os.path.join(ol.wd, "store", "")
        ol.cdir(wd)
        fns = os.listdir(wd)
        fns = sorted({x.split(os.sep)[0].split(".")[-1].lower() for x in fns})
        if fns:
            event.reply(",".join(fns))
        return
    ol.prs.parse(event, event.txt)
    otype = event.args[0]
    shorts = ol.utl.find_shorts("ol,omod")
    otypes = ol.get(shorts, otype, [otype,])
    args = list(ol.keys(event.gets))
    try:
        arg = event.args[1:]
    except ValueError:
        arg = []
    args.extend(arg)
    nr = -1
    for otype in otypes:
        for o in ol.dbs.find(otype, event.gets, event.index, event.timed):
            nr += 1
            if "f" in event.opts:
                pure = False
            else:
                pure = True
            txt = "%s %s" % (str(nr), ol.format(o, args, pure))
            if "t" in event.opts:
                txt += " %s" % (ol.tms.elapsed(time.time() - ol.tms.fntime(o.__stamp__)))
            event.reply(txt)
