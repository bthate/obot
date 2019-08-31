""" show list of commands. """

from ob.kernel import k

def __dir__():
    return ("cmds", )

def cmds(event):
    bot = k.fleet.get_bot(event.orig)
    if bot:
        event.reply("|".join(sorted(bot.handlers)))
    else:
        event.reply("|".join(sorted(k.handlers)))
