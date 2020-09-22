# OLIB - object library
#
#

import importlib
import ol
import pkgutil
import queue
import threading
import _thread

dispatchlock = _thread.allocate_lock()

class Event(ol.Default):

    def __init__(self):
        super().__init__()
        self.args = []
        self.cmd = ""
        self.ready = threading.Event()
        self.rest = ""
        self.result = []
        self.thrs = []
        self.txt = ""

    def parse(self):
        args = self.txt.split()
        if args:
            self.cmd = args[0]
        if len(args) >= 2:
            self.args = args[1:]
            self.rest = " ".join(args[1:])

    def reply(self, txt):
        if not self.result:
            self.result = []
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            try:
                print(txt)
            except:
               pass

    def wait(self):
        self.ready.wait()
        res = []
        for thr in self.thrs:
            res.append(thr.join())
        return res

class Handler(ol.Object):

    def __init__(self):
        super().__init__()
        self.cmds = ol.Object()
        self.packages = []
        self.queue = queue.Queue()
        self.stopped = False

    @ol.locked(dispatchlock)
    def dispatch(self, e):
        e.parse()
        if e.cmd in self.cmds:
            try:
                self.cmds[e.cmd](e)
            except Exception as ex:
                print(ol.utl.get_exception())
        e.show()
        e.ready.set()

    def handler(self):
        while not self.stopped:
            event = self.queue.get()
            if not event:
                break
            if not event.orig:
                event.orig = repr(self)
            if event.txt:
                ol.tsk.launch(self.dispatch, event, name=event.txt.split()[0])
            else:
                event.ready.set()

    def load_mod(self, name):
        mod = ol.utl.direct(name)
        self.scan(mod)
        return mod

    def put(self, e):
        self.queue.put_nowait(e)

    def scan(self, mod):
        cmds = ol.utl.find_cmds(mod)
        ol.update(self.cmds, cmds)

    def start(self):
        ol.tsk.launch(self.handler)

    def stop(self):
        self.stopped = True
        self.queue.put(None)

    def walk(self, names, ignore=""):
        modules = []
        for name in names.split(","):
            if name in ignore.split(","):
                continue
            self.packages.append(name)
            spec = importlib.util.find_spec(name)
            if not spec:
                continue
            pkg = importlib.util.module_from_spec(spec)
            pn = getattr(pkg, "__path__", None)
            if not pn:
                continue
            for mi in pkgutil.iter_modules(pn):
                mn = "%s.%s" % (name, mi.name)
                module = self.load_mod(mn)
                modules.append(module)
        return modules
