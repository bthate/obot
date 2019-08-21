""" log and todo commands. """

import ob

from ob.kernel import k

def __dir__():
    return ("Log", "Todo", "log", "todo")

class Log(ob.Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

class Todo(ob.Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def log(event):
    if not event.rest:
        nr = 0
        for o in k.db.find("obot.entry.Log", {"rss": ""}):
            event.reply("%s %s" % (nr, o.rss))
        return
    obj = Log()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")

def todo(event):
    if not event.rest:
        nr = 0
        for o in k.db.find("obot.entry.Todo", {"rss": ""}):
            event.reply("%s %s" % (nr, o.rss))
        return
    obj = Todo()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")
