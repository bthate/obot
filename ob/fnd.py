# This file is placed in the Public Domain.

"find objects"

# imports

from . import cfg, keys
from .ofn import format
from .dbs import find, list_files
from .hdl import Bus
from .prs import elapsed
from .tbl import tbl
from .utl import fntime, time

# commands

def fnd(event):
    if not event.res.args:
        fls = list_files(cfg.wd)
        if fls:
            event.reply("|".join([x.split(".")[-1].lower() for x in fls]))
        return
    name = event.res.args[0]
    bot = Bus.by_orig(event.orig)
    t = bot.get_names(name)
    nr = -1
    for otype in t:
        for fn, o in find(otype, event.gets, event.index, event.timed):
            nr += 1
            txt = "%s %s" % (str(nr), format(o, keys(o), skip=event.skip))
            if "t" in event.opts:
                txt = txt + " %s" % (elapsed(time.time() - fntime(fn)))
            event.reply(txt)
