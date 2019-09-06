""" runtime objects and boot code. """

import inspect
import logging
import ob
import sys
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
from ob.utils import get_name, mods

def __dir__():
    return ("cfg", "Kernel", "k")

class Cfg(Cfg):

    """ kernel config. """

class Kernel(Handler):

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

    def announce(self, txt):
        print(txt)

    def cmd(self, txt, origin=""):
        """ execute a string as a command. """
        if not txt:
            return
        self.load_mod("ob.dispatch")
        self.cfg.prompt = False
        self.cfg.verbose = True
        k.fleet.add(self)
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
        for mod in mods(self, modstr):
            logging.warn("init %s" % get_name(mod))
            try:
                mod.init()
            except AttributeError:
                pass
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
        e.options = k.cfg.options
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

    def start(self, handler=None, input=True, output=True):
        """ start the kernel. """
        super().start(handler or self.handler, input, output)
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
