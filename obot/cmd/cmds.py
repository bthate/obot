""" list of commands. """

from ob import k

def cmds(event):
    """ show commands. """
    event.reply("|".join(sorted(k.cmds)))

