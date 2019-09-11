""" show list of commands. """

import ob
import obot
import time
import threading

from ob import k
from ob.cls import Dict
from ob.shl import set_completer
from ob.utl import elapsed, get_name, mods

def __dir__():
    return ("cmds","load", "unload", "show", "find")

def cmds(event):
    """ show commands. """
    bot = k.fleet.get_bot(event.orig)
    if bot and bot.cmds:
        event.reply("|".join(sorted(bot.cmds)))
    else:
        event.reply("|".join(sorted(k.cmds)))

def find(event):
    """ find an object matching to a key==value selector. """
    if "k" in event.options:
        o = k.db.last(event.match)
        if o:
            event.reply("|".join(sorted({x for x in o.keys() if not x.startswith("_")})))
            return
    if not event.args:
        fns = os.listdir(os.path.join(ob.workdir, "store"))
        fns = sorted({x.split(".")[-1].lower() for x in fns})
        if fns:
            event.reply("|".join(fns))
        return
    if len(event.args) == 1 and not event.selector:
        fn, o = k.db.last_fn(event.match)
        if fn:
            res = sorted({x.split(".")[-1].lower() for x in o})
            if len(res) > 1:
                event.reply("|".join(res))
            else:
                for a in res:
                    if a not in event.selector:
                        event.selector[a] = None
                    if a not in event.dkeys:
                        event.dkeys.append(a)
    nr = -1
    for o in k.db.find(event.match, event.selector, event.index, event.delta):
        nr += 1
        event.display(o, str(nr))

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

def meet(event):
    if not event.args:
        event.reply("meet origin [permissions]")
        return
    try:
        origin, *perms = event.args[:]
    except ValueError:
        event.reply("|".join(sorted(k.users.userhosts)))
        return
    origin = k.users.userhosts.get(origin, origin)
    u = k.users.meet(origin, perms)
    event.reply("added %s" % u.user)

def show(event):
    """ display runtime information. """
    if not event.args:
        event.reply("cfg|cmds|fleet|kernel|ls|pid|tasks|version")
        return
    bot = k.fleet.get_bot(event.orig)
    cmd = event.args[0]
    if cmd == "cfg":
        if len(event.args) == 2:
            config = k.db.last("%s.%s.Cfg" % ("obot", event.args[1].lower()))
            event.reply(config)
        else:
            event.reply(k.cfg)
    elif cmd == "cmds":
        event.reply("|".join(sorted(k.cmds)))
    elif cmd == "fleet":
        try:
            index = int(event.args[1])
            event.reply(k.fleet.bots[index])
            return
        except (ValueError, IndexError):
            event.reply([get_type(x) for x in k.fleet.bots])
    elif cmd == "kernel":
        event.reply(str(k))
    elif cmd == "ls":
        event.reply("|".join(os.listdir(os.path.join(k.cfg.workdir, "store"))))
    elif cmd == "pid":
        event.reply(str(os.getpid()))
    elif cmd == "tasks":
        psformat = "%-8s %-60s"
        result = []
        for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
            if str(thr).startswith("<_"):
                continue
            d = vars(thr)
            o = Dict()
            o.update(d)
            if getattr(o, "sleep", None):
                up = o.sleep - int(time.time() - o.state.latest)
            else:
                up = int(time.time() - k.state.starttime)
            result.append((up, thr.getName(), o))
        nr = -1
        for up, thrname, o in sorted(result, key=lambda x: x[0]):
            nr += 1
            res = "%s %s" % (nr, psformat % (elapsed(up), thrname[:60]))
            if res.strip():
                event.reply(res)
    elif cmd == "uptime":
        event.reply(elapsed(time.time() - k.state.starttime))
    elif cmd == "version":
        res = []
        res.append("OB %s" % ob.__version__)
        res.append("OBOT %s" % obot.__version__)
        for name, mod in k.table.items():
            if name in ["ob", "obot"]:
                continue
            if not mod:
                continue
            ver = getattr(mod, "__version__", None)
            if ver:
                txt = "%s %s" % (name, ver)
                res.append(txt.upper())
        if res:
            event.reply(" | ".join(res))

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
