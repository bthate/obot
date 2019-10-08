""" show runtime status. """

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
    return ("show",)

def show(event):
    """ display runtime information. """
    if not event.args:
        event.reply("cfg|cmds|fleet|kernel|ls|pid|tasks|version")
        return
    bot = k.fleet.get_bot(event.orig)
    cmd = event.args[0]
    if cmd == "cfg":
        if len(event.args) == 2:
            config = k.db.last("%s.%s.Cfg" % ("obot", event.args[1].lower()))
            event.reply(config)
        else:
            event.reply(k.cfg)
    elif cmd == "cmds":
        event.reply("|".join(sorted(k.cmds)))
    elif cmd == "fleet":
        try:
            index = int(event.args[1])
            event.reply(k.fleet.bots[index])
            return
        except (ValueError, IndexError):
            event.reply([get_type(x) for x in k.fleet.bots])
    elif cmd == "kernel":
        event.reply(str(k))
    elif cmd == "ls":
        event.reply("|".join(os.listdir(os.path.join(k.cfg.workdir, "store"))))
    elif cmd == "pid":
        event.reply(str(os.getpid()))
    elif cmd == "tasks":
        psformat = "%-8s %-60s"
        result = []
        for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
            if str(thr).startswith("<_"):
                continue
            d = vars(thr)
            o = Object()
            ob.update(o, d)
            if getattr(o, "sleep", None):
                up = o.sleep - int(time.time() - o.state.latest)
            else:
                up = int(time.time() - k.state.starttime)
            result.append((up, thr.getName(), o))
        nr = -1
        for up, thrname, o in sorted(result, key=lambda x: x[0]):
            nr += 1
            res = "%s %s" % (nr, psformat % (elapsed(up), thrname[:60]))
            if res.strip():
                event.reply(res)
    elif cmd == "uptime":
        event.reply(elapsed(time.time() - k.state.starttime))
    elif cmd == "version":
        res = []
        res.append("OB %s" % ob.__version__)
        res.append("OBOT %s" % obot.__version__)
        for name, mod in k.table.items():
            if name in ["ob", "obot"]:
                continue
            if not mod:
                continue
            ver = getattr(mod, "__version__", None)
            if ver:
                txt = "%s %s" % (name, ver)
                res.append(txt.upper())
        if res:
            event.reply(" | ".join(res))