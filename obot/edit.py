import ob
import os

from ob import k

def ed(event):
    if not event.args:
        fns = os.listdir(os.path.join(ob.workdir, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        event.reply("ed <type> key==value")
        return
    objs = k.db.find(event.match, event.selector, event.index, event.delta)
    nr = 0
    for o in objs:
        ob.edit(o, event.setter)
        o.save()
        nr += 1
    event.reply("edit %s" % nr)
