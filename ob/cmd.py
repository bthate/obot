# This file is placed in the Public Domain.

"commands"

# imports

import ob

from . import keys, save
from .hdl import Bus
from .ofn import edit, format

# commands

def cfg(event):
    if not event.sets:
        event.reply(format(ob.cfg, skip=["old", "res"]))
        return
    edit(ob.cfg, event.sets)
    save(ob.cfg)
    event.reply("ok")

def cmd(event):
    b = Bus.by_orig(event.orig)
    event.reply(",".join(sorted(b.cmds)))
