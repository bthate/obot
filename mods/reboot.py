import logging
import os
import sys

from ob.kernel import k

def reboot(event):
    if not k.cfg.owner:
        event.reply("owner is not set. use --owner")
        return
    logging.error("reboot")
    for bot in k.fleet:
        bot.save()
    reset()
    os.execl(sys.argv[0], *(sys.argv + ["-r"]))
