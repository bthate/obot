""" module commands. """

from ob import Object, k
from ob.shl import set_completer
from ob.utl import get_name, mods

def load(event):
    """ load a module into the kernel. """
    if event.origin != k.cfg.owner and not k.cfg.debug:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    m = []
    for name in event.args[0].split(","):
        name = event.args[0]
        m.extend(mods(k, name))
        k.init(name)
    set_completer(k.cmds)
    event.reply("%s loaded" % ",".join([get_name(x) for x in m]))

def unload(event):
    """ unload a module from the table. """
    if event.origin != k.cfg.owner and not k.cfg.debug:
        event.reply("EOWNER, use the --owner option")
        return
    if not event.args:
        event.reply("|".join({x.split(".")[-1] for x in k.modules.values()}))
        return
    bot = k.fleet.get_bot(event.orig)
    name = event.args[0]
    for key in k.modules:
        mn = k.modules[key]
        if name in mn:
            try:
                k.handlers.remove(key)
                del k.cmds[key]
            except (RuntimeError, KeyError, ValueError):
                continue
    todo = []
    for key in k.table:
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
