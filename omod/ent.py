# OLIB - object library
#
#

import ol

class Log(ol.Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

class Todo(ol.Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for o in ol.dbs.find("omod.ent.Todo", selector):
        o._deleted = True
        ol.save(o)
        event.reply("ok")
        break

def log(event):
    if not event.rest:
        return
    l = Log()
    l.txt = event.rest
    ol.save(l)
    event.reply("ok")

def tdo(event):
    if not event.rest:
        return
    o = Todo()
    o.txt = event.rest
    ol.save(o)
    event.reply("ok")
