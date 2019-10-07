""" list of commands. """

from ob import k

def cmds(event):
    """ show commands. """
    bot = k.fleet.get_bot(event.orig)
    if bot and bot.cmds:
        event.reply("|".join(sorted(bot.cmds)))
    else:
        event.reply("|".join(sorted(k.cmds)))
