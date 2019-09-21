""" show list of commands. """

import ob
import os
import time
import threading

from ob import k
from ob.shl import set_completer
from ob.tms import elapsed
from ob.utl import get_name, mods

def __dir__():
    return ("cmds",)

def cmds(event):
    """ show commands. """
    bot = k.fleet.get_bot(event.orig)
    if bot and bot.cmds:
        event.reply("|".join(sorted(bot.cmds)))
    else:
        event.reply("|".join(sorted(k.cmds)))
