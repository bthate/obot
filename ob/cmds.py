""" show list of commands. """

from ob.kernel import k

def __dir__():
    return ("cmds", )

def cmds(event):
    event.reply("|".join(sorted([x for x in k.handlers])))

