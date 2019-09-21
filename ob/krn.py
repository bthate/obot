""" runtime objects and boot code. """

import inspect
import logging
import ob
import sys
import threading
import time
import _thread

from ob.cls import Cfg
from ob.db import Db
from ob.dpt import dispatch
from ob.err import EINIT 
from ob.flt import Fleet
from ob.hdl import Event, Handler
from ob.shl import enable_history, set_completer
from ob.thr import Launcher
from ob.usr import Users
from ob.trc import get_exception
from ob.utl import get_name, mods

def __dir__():
    return ("Cfg", "Kernel",)

class Cfg(Cfg):

    """ kernel config. """

class Kernel(Handler):

    """ contains the basic data structures and exception trap code. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._prompted = threading.Event()
        self._prompted.set()
        self._started = False
        self.cfg = Cfg()
        self.db = Db()
        self.fleet = Fleet()
        self.register(dispatch)
        self.state = ob.Object()
        self.state.started = False
        self.state.starttime = time.time()
        self.users = Users()

    def add(self, cmd, func):
        self.cmds[cmd] = func

    def announce(self, txt):
        print(txt)

    def cmd(self, txt, origin=""):
        """ execute a string as a command. """
        if not txt:
            return
        self.load_mod("ob.dpt")
        self.cfg.prompt = False
        self.cfg.verbose = True
        self.fleet.add(self)
        e = Event()
        e.txt = txt
        e.options = self.cfg.options
        e.origin = origin or "root@shell"
        self.handle(e)
        e.wait()

    def init(self, modstr):
        """ initialize a comma seperated list of modules. """
        if not modstr:
            return
        if modstr == "all":
            modstr = "ob,ob.cmd,obot"
        for mod in mods(self, modstr):
            next = False
            for ex in self.cfg.exclude.split(","):
                if ex and ex in mod.__name__:
                    next = True
                    break
            if next:
                continue
            logging.warn("init %s" % get_name(mod))
            if "init" not in dir(mod):
                continue
            try:
                mod.init()
            except EINIT:
                if not self.cfg.debug:
                    _thread.interrupt_main()
            except Exception as ex:
                logging.error(get_exception())

    def input(self):
        """ start a input loop. """
        while not self._stopped:
            e = self.poll()
            self.put(e)
            e.wait()

    def prompt(self, e):
        """ return a event by prompting for some text. """
        e.txt = input("> ")
        e.txt = e.txt.rstrip()
        return e

    def poll(self):
        e = Event()
        e.options = self.cfg.options
        e.origin = "root@shell"
        self.prompt(e)
        return e

    def raw(self, txt):
        """ write directly to display. """
        if not txt:
            return
        sys.stdout.write(str(txt) + "\n")
        sys.stdout.flush()

    def say(self, orig, channel, txt, type="chat"):
        """ output text on console or relay to fleet. """
        if orig == repr(self):
            self.raw(txt)
        else:
            self.fleet.echo(orig, channel, txt, type)

    def start(self, handler=True, input=True, output=True):
        """ start the kernel. """
        if self._started:
            return
        self._started = True
        if self.cfg.prompting:
            self.cfg.save()
        set_completer(self.cmds)
        enable_history()
        super().start(handler, input, output)

    def wait(self):
        """ sleep in a loop. """
        while not self._stopped:
            time.sleep(1.0)
