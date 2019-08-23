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
    return ("cfg", "fleet", "kernel", "ls", "uptime", "version")

def cfg(event):
    """ show configuration files. """
    if len(event.args) == 1:
        config = k.db.last("%s.%s.Cfg" % ("obot", event.args[0].lower()))
        event.reply(config)
    else:
        event.reply(k.cfg)

def fleet(event):
    """ show list of bots. """
    try:
        index = int(event.args[1])
        event.reply(k.fleet.bots[index])
        return
    except (ValueError, IndexError):
        event.reply([get_type(x) for x in k.fleet.bots])

def kernel(event):
    """ kernel dump. """
    event.reply(k)

def ls(event):
    """ show listing of the store directory. """
    event.reply("|".join(os.listdir(os.path.join(k.cfg.workdir, "store"))))

def uptime(event):
    """ show time running. """
    event.reply(elapsed(time.time() - k.state.starttime))

def version(event):
    """ show bot's version. """
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
        ver = getattr(mod, "__version__", None)
        if ver:
            res.append("%s %s" % (name, ver))
    if res:
        event.reply(" | ".join(res))
