""" operator commands. """

import ob
import os

from ob import Object, k

def find(event):
    """ find an object matching to a key==value selector. """
    if "k" in event.options:
        o = k.db.last(event.match)
        if o:
            event.reply("|".join(sorted({x for x in o.keys() if not x.startswith("_")})))
            return
    if not event.args:
        fns = os.listdir(os.path.join(ob.workdir, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        if fns:
            event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        o = k.db.last(event.match)
        if o:
            res = sorted({x.split(".")[-1].lower() for x in o})
            if len(res) > 1:
                event.reply("|".join(res))
            else:
                for a in res:
                    if a not in event.selector:
                        event.selector[a] = None
                    if a not in event.dkeys:
                        event.dkeys.append(a)
    nr = -1
    for o in k.db.find(event.match, event.selector, event.index, event.delta):
        nr += 1
        event.display(o, str(nr))

find.threaded = True
