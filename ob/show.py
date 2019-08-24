""" show runtime data. """

import os
import threading
import time

from ob import Object
from ob.kernel import k
from ob.handler import Handler
from ob.types import get_type
from ob.times import elapsed
from ob.utils import get_name

def __dir__():
    return ("show",)


def show(event):
    """ display runtime information. """
    if not event.args:
        event.reply("config|cmds|fleet|kernel|tasks|version")
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
        event.reply("|".join(sorted(bot.handlers.keys())))
    elif cmd == "fleet":
        try:
            index = int(event.args[2])
            event.reply(k.fleet.bots[index])
            return
        except (ValueError, IndexError):
            event.reply([get_type(x) for x in k.fleet.bots])
    elif cmd == "kernel":
        event.reply(k)
    elif cmd == "ls":
        event.reply("|".join(os.listdir(os.path.join(k.cfg.workdir, "store"))))
    elif cmd == "tasks":
        psformat = "%-8s %-60s"
        result = []
        for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
            if str(thr).startswith("<_"):
                continue
            d = vars(thr)
            o = Object()
            o.update(d)
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
        import ob
        import obot
        res = []
        event.reply("OBOT %s" % obot.__version__)
        event.reply("OB %s" % ob.__version__)
        for name, mod in k.table.items():
            if name in ["ob", "obot"]:
                continue
            if not mod:
                continue
            ver = ob.get(mod, "__version__", None)
            if ver:
                res.append("%s %s" % (name, ver))
        if res:
            event.reply(" | ".join(res))
