""" operator commands. """

import ob
import obot
import os
import time
import threading

from ob import Object, k
from ob.shl import set_completer
from ob.tms import elapsed
from ob.utl import get_name, mods

def __dir__():
    return ("load", "find", "meet", "unload")

def find(event):
    """ find an object matching to a key==value selector. """
    print(event)
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
        fn, o = k.db.last_fn(event.match)
        if fn:
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

def load(event):
    """ load a module into the kernel. """
    if event.origin != k.cfg.owner and not k.cfg.debug:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    m = []
    for name in event.args[0].split(","):
        name = event.args[0]
        m.extend(mods(k, name))
        k.init(name)
    set_completer(k.cmds)
    event.reply("%s loaded" % ",".join([get_name(x) for x in m]))

def meet(event):
    if not event.args:
        event.reply("meet origin [permissions]")
        return
    try:
        origin, *perms = event.args[:]
    except ValueError:
        event.reply("|".join(sorted(k.users.userhosts)))
        return
    origin = ob.get(k.users.userhosts, origin, origin)
    u = k.users.meet(origin, perms)
    event.reply("added %s" % u.user)

def unload(event):
    """ unload a module from the table. """
    if event.origin != k.cfg.owner and not k.cfg.debug:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    bot = k.fleet.get_bot(event.orig)
    name = event.args[0]
    for key in k.modules:
        mn = k.modules[key]
        if name in mn:
            try:
                k.handlers.remove(key)
                del k.cmds[key]
            except (RuntimeError, KeyError, ValueError):
                continue
    todo = []
    for key in k.table:
        if name in key:
           todo.append(key)
    for key in todo:
        try:
            del k.table[key]
        except (KeyError, ValueError):
            event.reply("%s is not loaded." % name)
            return
    set_completer(k.cmds)
    event.reply("unload %s" % name)
