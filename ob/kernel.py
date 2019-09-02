""" runtime objects and boot code. """

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

    def _raw(self, txt):
        """ print to console. """
        if self.cfg.verbose:
            print(txt)

    def cmd(self, txt, origin=""):
        """ execute a string as a command. """
        if not txt:
            return
        event = Event()
        event.txt = txt
        event.options = self.cfg.options
        event.origin = origin or "root@shell"
        event.parse(event.txt)
        self.dispatch(event)
        event.wait()

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
        self._prompted.wait()
        e.txt = input("> ")
        e.txt = e.txt.rstrip()
        self._prompted.set()
        return e

    def say(self, orig, channel, txt, type="chat"):
        if orig == repr(self):
            self._raw(txt)
        else:
            self.fleet.echo(orig, channel, txt, type)

    def input(self):
        logging.warn("starting shell")
        while not self._stopped:
            e = Event()
            e.options = k.cfg.options
            e.origin = "root@shell"
            self.put(self.prompt(e))
            e.wait()

    def start(self):
        """ start the kernel. """
        super().start()
        if self.cfg.prompting:
            self.cfg.prompting = False
            self.cfg.save()
        set_completer(k.handlers)
        enable_history()

#:
k = Kernel()
