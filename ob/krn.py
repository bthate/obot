# OBOT - 24/7 channel daemon
#
#

"kernel (krn)"

__version__ = 21

import importlib, os, pkgutil, sys, time, threading

booted = False
starttime = time.time()
wd = ""

from ob.bus import bus
from ob.cfg import Cfg
from ob.evt import Event
from ob.ldr import Loader
from ob.hdl import Handler
from ob.int import *
from ob.obj import Object, get, update
from ob.prs import parse, parse_cli
from ob.trm import termreset, termsave
from ob.tsk import start
from ob.utl import cdir, direct, get_exception, get_name, spl

class Cfg(Cfg):

    pass

class Kernel(Loader, Handler):

    "kernel class"

    classes = Object()
    cmds = Object()
    funcs = Object()
    mods = Object()
    names = Object()

    def __init__(self):
        super().__init__()
        self.ready = threading.Event()
        self.stopped = False
        self.cfg = Cfg()
        self.packages = []
        kernels.append(self)

    def announce(self, txt):
        "silence announcing"

    def cmd(self, txt):
        "execute single command"
        if not txt:
            return None
        e = Event()
        e.txt = txt
        bus.add(self)
        sys.path.insert(0, os.path.join(self.cfg.wd, "mods"))
        self.dispatch(e)
        return e

    def direct(self, txt):
        "print text"
        print(txt.rstrip())

    def dispatch(self, e):
        "dispatch event"
        e.parse()
        if not e.orig:
            e.orig = repr(self)
        func = self.get_cmd(e.cmd)
        if not func:
            mn = get(self.mods, e.cmd, None)
            if mn:
                spec = importlib.util.find_spec(mn)
                if spec:
                    self.load(mn)
                    func = self.get_cmd(e.cmd)
        if func:
            func(e)
            e.show()
        e.ready.set()

    def get_cmd(self, cmd):
        "return command"
        if cmd in self.cmds:
             return self.cmds[cmd]
        mn = get(self.mods, cmd, None)
        if not mn:
            return
        mod = None
        if mn in sys.modules:
            mod = sys.modules[mn]
        else:
            spec = importlib.util.find_spec(mn)
            if spec:
                mod = direct(mn)
        if mod:
            return getattr(mod, cmd, None)

    def init(self, mns, name=None, exc=""):
        "call init() of modules"
        if not mns:
            return
        exclude = exc.split(",")
        thrs = []
        for mn in spl(mns):
            if mn in exclude:
                continue
            spec = None
            if "." in mn:
                try:
                    spec = importlib.util.find_spec(mn)
                except ModuleNotFoundError:
                    continue
            if not spec:
                try:
                    mod = importlib.import_module(mn)
                    for key, o in inspect.getmembers(mod, inspect.ismodule):
                        mnn = "%s.%s" % (mod.__name__, o.__name)
                        modd = self.load(mnn)
                        self.scan(modd)
                except ModuleNotFound:
                    for pn in self.packages:
                        mnn = "%s.%s" % (pn, mn)
                        try:
                            spec = importlib.util.find_spec(mnn)
                            mn = mnn
                            break
                        except ModuleNotFoundError:
                            continue
            if not spec:
                continue
            if mn not in self.table:
                mod = self.load(mn)
            self.scan(self.table[mn])
            if mn in self.table:
                func = getattr(self.table[mn], "init", None)
                if func:
                    thrs.append(start(func, self, name=get_name(func)))
        return thrs

    def say(self, channel, txt):
        "echo to screen"
        self.direct(txt)

    def scan(self, mod):
        "update tables"
        update(self.cmds, find_cmds(mod))
        update(self.funcs, find_funcs(mod))
        update(self.mods, find_mods(mod))
        update(self.names, find_names(mod))
        update(self.classes, find_class(mod))

    def stop(self):
        "stop kernel"
        self.stopped = True
        self.queue.put(None)

    def tabled(self, tbl):
        "initialise with a table"
        update(Kernel.classes, tbl.classes)
        update(Kernel.funcs, tbl.funcs)
        update(Kernel.mods, tbl.mods)
        update(Kernel.names, tbl.names)

    def wait(self):
        "loop forever"
        while not self.stopped:
            time.sleep(60.0)

    def walk(self, names):
        "walk over packages and load their modules"
        for name in names.split(","):
            self.packages.append(name)
            spec = importlib.util.find_spec(name)
            if not spec:
                continue
            pn = spec.submodule_search_locations
            if not pn:
                continue
            for mi in pkgutil.iter_modules(pn):
                mn = "%s.%s" % (name, mi.name)
                mod = direct(mn)
                self.scan(mod)


#:
kernels = []

def boot(name, wd="", root=False):
    "set basic paths, read cli options and return kernel"
    if root:
        wd = "/var/lib/%s/" % name
    else:
        wd = os.path.expanduser("~/.%s/" % name)
    cfg = parse_cli()
    k = get_kernel()
    update(k.cfg, cfg)
    import ob.krn
    ob.krn.wd = k.cfg.wd or wd
    sys.path.insert(0, k.cfg.wd)
    return k

def cmd(txt):
    "execute single command"
    k = get_kernel()
    return k.cmd(txt)

def execute(main):
    "provide context for funcion"
    termsave()
    try:
        main()
    except KeyboardInterrupt:
        print("")
    except PermissionError:
        print("you need root permission.")
    except Exception as ex:
        print(get_exception())
    finally:
        termreset()



def get_kernel():
    "return kernel"
    if kernels:
        return kernels[0]
    return Kernel()

def scandir(path):
    "scan a modules directory"
    mods = []
    if not os.path.exists(os.path.join(path, "mods")):
        return mods
    k = get_kernel()
    mods = []
    cdir(path + os.sep + "")
    for fn in os.listdir(os.path.join(path, "mods")):
        if fn.startswith("_") or not fn.endswith(".py"):
            continue
        mn = "mods.%s" % fn[:-3]
        spec = importlib.util.find_spec(mn)
        if spec:
            module = k.load(mn)
            k.scan(module)
            mods.append(module)
    return mods
