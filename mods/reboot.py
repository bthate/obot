import logging
import os
import sys

from ob import k
from ob.trm import reset

def reboot(event):
    if not k.cfg.owner:
        event.reply("owner is not set. use --owner")
        return
    logging.error("reboot")
    for bot in k.fleet:
        bot.save()
    reset()
    os.execl(sys.argv[0], *(sys.argv + ["-r"]))
