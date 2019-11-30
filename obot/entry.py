""" log and todo commands. """

from ob import k
from ob.pst import Persist

def __dir__():
    return ("Log", "Todo", "log", "todo")

class Log(Persist):

    def __init__(self):
        super().__init__()
        self.txt = ""

class Todo(Persist):

    def __init__(self):
        super().__init__()
        self.txt = ""

def log(event):
    if not event.rest:
        nr = 0
        event.options += "t"
        if not event.dkeys:
            event.dkeys.append("txt")
        for o in k.db.find("obot.cmd.ent.Log", event.selector or {"txt": ""}):
            event.display(o, "%-2s" % str(nr))
            nr += 1
        return
    obj = Log()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")

def todo(event):
    if not event.rest:
        nr = 0
        event.options += "t"
        if "txt" not in event.dkeys:
            event.dkeys.append("txt")
        for o in k.db.find("obot.cmd.ent.Todo", event.selector or {"txt": ""}):
            event.display(o, "%-2s" % str(nr))
            nr += 1
        return
    obj = Todo()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")
