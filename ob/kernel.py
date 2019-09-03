""" runtime objects and boot code. """

import inspect
import logging
import ob
import threading
import time
import _thread

from ob import Cfg, Object
from ob.db import Db
from ob.errors import EINIT 
from ob.fleet import Fleet
from ob.handler import Event, Handler
from ob.shell import enable_history, set_completer
from ob.tasks import Launcher
from ob.trace import get_exception
from ob.user import Users
from ob.utils import get_name

def __dir__():
    return ("cfg", "Kernel", "k")

class Cfg(Cfg):

    """ kernel config. """

class Kernel(Handler, Launcher):

    """ contains the basic data structures and exception trap code. """

    def __init__(self):
        super().__init__()
        self._outputed = False
        self._prompted = threading.Event()
        self._prompted.set()
        self.cfg = Cfg()
        self.db = Db()
        self.fleet = Fleet()
        self.state = Object()
        self.state.started = False
        self.state.starttime = time.time()
        self.users = Users()

    def add(self, cmd, func):
        self.cmds[cmd] = func

    def cmd(self, txt, origin=""):
        """ execute a string as a command. """
        if not txt:
            return
        self.cfg.verbose = True
        self.start()
        e = Event()
        e.txt = txt
        e.options = self.cfg.options
        e.origin = origin or "root@shell"
        self.event(e)
        e.wait()

    def init(self, modstr):
        """ initialize a comma seperated list of modules. """
        if not modstr:
            return
        for mn in modstr.split(","):
            if not mn:
                continue
            mod = None
            ex = None
            try:
               mod = self.load_mod(mn)
            except ModuleNotFoundError:
                try:
                    mod = self.load_mod("ob.%s" % mn)
                except ModuleNotFoundError:
                   try:
                       mod = self.load_mod("obot.%s" % mn)
                   except ModuleNotFoundError:
                       try:
                           mod = self.load_mod("%s.%s" % (self.cfg.name, mn))
                       except ModuleNotFoundError:
                           logging.error("not found %s" % mn)
            self.scan(mod)
            logging.warn("init %s" % get_name(mod))
            if mod:
                try:
                    mod.init()
                except AttributeError:
                    pass
                except EINIT:
                    _thread.interrupt_main()
                except Exception as ex:
                     logging.error(get_exception())

    def prompt(self, e):
        """ return a event by prompting for some text. """
        if self.cfg.args:
            e.txt = " ".join(self.cfg.args)
        else:
            e.txt = input("> ")
            e.txt = e.txt.rstrip()
        return e

    def input(self):
        """ start a input loop. """
        while not self._stopped:
            e = Event()
            e.options = k.cfg.options
            e.origin = "root@shell"
            self.put(self.prompt(e))
            e.wait()

    def raw(self, txt):
        """ print to console. """
        print(txt)

    def say(self, orig, channel, txt, type="chat"):
        """ output text on console or relay to fleet. """
        if orig == repr(self):
            self.raw(txt)
        else:
            self.fleet.echo(orig, channel, txt, type)

    def start(self):
        """ start the kernel. """
        super().start()
        if self.cfg.prompting:
            self.cfg.prompting = False
            self.cfg.save()
        set_completer(k.cmds)
        enable_history()

    def wait(self):
        """ sleep in a loop. """
        while not self._stopped:
            time.sleep(1.0)

#:
k = Kernel()
