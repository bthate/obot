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
        event.reply("log <txt>")
        return
    obj = Log()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")

def todo(event):
    if not event.rest:
        event.reply("todo <txt>")
        return
    obj = Todo()
    obj.txt = event.rest
    obj.save()
    event.reply("ok")
