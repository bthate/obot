from ob import k
from ob.shl import set_completer

def load(event):
    if not event.args:
        event.reply("|".join({modules[x].split(".")[-1] for x in k.modules}))
        return
    m = []
    for name in event.args[0].split(","):
        name = event.args[0]
        m.extend(mods(k, name))
        k.init(name)
    set_completer(k.cmds)
    if m:
        event.reply("%s loaded" % ",".join([get_name(x) for x in m]))

def unload(event):
    if not event.args:
        event.reply("|".join({modules[x].split(".")[-1] for x in k.modules}))
        return
    bot = k.fleet.get_bot(event.orig)
    name = event.args[0]
    for key in k.modules:
        mn = k.modules.get(key)
        if name in mn:
            try:
                k.handlers.remove(key)
                k.cmds.remove(key)
            except (RuntimeError, KeyError, ValueError):
                continue
    todo = []
    for key in k.table:
        if "mdl" in key:
            continue
        if name in key:
           todo.append(key)
    for key in todo:
        try:
            del k.table[key]
        except (KeyError, ValueError):
            event.reply("%s is not loaded." % name)
            return
    set_completer(k.cmds)
    event.reply("unload %s" % name)