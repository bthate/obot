# OLIB
#
#

"data entry"

from ol.dbs import find
from ol.obj import Object, save

class Log(Object):

    "log items"

    def __init__(self):
        super().__init__()
        self.txt = ""

class Todo(Object):

    "todo items"

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(event):
    "flag a todo item as done (dne)"
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for o in find("mymods.ent.Todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break

def log(event):
    "log some text (log)"
    if not event.rest:
        return
    l = Log()
    l.txt = event.rest
    save(l)
    event.reply("ok")

def tdo(event):
    "add a todo item (tdo)"
    if not event.rest:
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")
