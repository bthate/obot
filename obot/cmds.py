from ob import k

def cmds(event):
    event.reply("|".join(sorted(k.cmds)))
