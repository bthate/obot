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
    return ("cfg", "fleet", "ls", "uptime", "version")

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

def ls(event):
    """ show listing of the store directory. """
    event.reply("|".join(os.listdir(os.path.join(k.cfg.workdir, "store"))))

def uptime(event):
    """ show time running. """
    event.reply(elapsed(time.time() - k.state.starttime))

def version(event):
    """ show bot's version. """
    import ob
    for name, mod in k.table.items():
        if not mod:
            continue
        ver = getattr(mod, "__version__", None)
        if ver:
            event.reply("%s %s" % (name.upper(), ver))
    event.reply("%s %s" % (k.cfg.name.upper(), ob.__version__))
    