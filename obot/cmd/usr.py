""" operator commands. """

import ob
import obot
import os
import time
import threading

from ob import Object, k
from ob.utl import get_name

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
