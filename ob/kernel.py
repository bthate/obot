""" provide persistence through save/load to JSON files. """

import logging
import ob
import time
import _thread

from ob import Cfg, Object
from ob.db import Db
from ob.errors import EINIT 
from ob.fleet import Fleet
from ob.handler import Event, Handler
from ob.tasks import Launcher
from ob.trace import get_exception
from ob.user import Users
from ob.utils import get_name

def __dir__():
    return ("Kernel", "k")

class Kernel(Handler, Launcher):

    """ contains the basic data structures and exception trap code. """

    def __init__(self):
        super().__init__()
        self.cfg = Cfg()
        self.db = Db()
        self.fleet = Fleet()
        self.state = Object()
        self.state.started = False
        self.state.starttime = time.time()
        self.users = Users()

    def cmd(self, txt, origin=""):
        """ execute a string as a command. """
        event = Event()
        event.batch = True
        event.txt = txt
        event.options = self.cfg.options
        event.origin = origin or "root@shell"
        self.dispatch(event)
        event.wait()
        return event.result

    def init(self, modstr):
        """ initialize a comaa seperated list of modules. """
        if not modstr:
            return
        for mn in modstr.split(","):
            if not mn:
                continue
            mod = None
            try:
                mod = self.load_mod(mn)
            except:
                try:
                    mod = self.load_mod("ob.%s" % mn)
                except:
                    try:
                        mod = self.load_mod("obot.%s" % mn)
                    except:
                        try:
                            mod = self.load_mod("%s.%s" % (self.cfg.name, mn))
                        except Exception as ex:
                            pass
            logging.warn("init %s" % get_name(mod))
            if mod:
                try:
                    mod.init()
                except EINIT:
                    _thread.interrupt_main()
                except Exception as ex:
                     logging.error(get_exception())
                     
#:
k = Kernel()
