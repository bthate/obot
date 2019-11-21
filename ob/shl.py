""" shell functions. """

import atexit
import logging
import optparse
import ob
import os
import readline
import sys
import time

cmds = []

from ob.cls import Cfg
from ob.utl import cdir, hd, touch
from ob.trc import get_exception 
from ob.trm import reset, save

HISTFILE = ""

def __dir__():
    return ("daemon", "execute", "parse_cli", "set_completer")

def close_history():
    global HISTFILE
    if not HISTFILE:
        HISTFILE = os.path.join(ob.workdir, "history")
    if not os.path.isfile(HISTFILE):
        cdir(HISTFILE)
        touch(HISTFILE)
    readline.write_history_file(HISTFILE)

def complete(text, state):
    matches = []
    if text:
        matches = [s for s in cmds if s and s.startswith(text)]
    else:
        matches = cmds[:]
    try:
        return matches[state]
    except IndexError:
        return None

def daemon():
    pid = os.fork()
    if pid != 0:
        reset()
        os._exit(0)
    os.setsid()
    os.umask(0)
    si = open("/dev/null", 'r')
    so = open("/dev/null", 'a+')
    se = open("/dev/null", 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def enable_history():
    global HISTFILE
    HISTFILE = os.path.abspath(os.path.join(ob.workdir, "history"))
    if not os.path.exists(HISTFILE):
        touch(HISTFILE)
    else:
        readline.read_history_file(HISTFILE)
    atexit.register(close_history)

def execute(main):
    """ wrap in terminal save/reset. """
    save()
    try:
        main()
    except KeyboardInterrupt:
        print("")
    except Exception:
        logging.error(get_exception())
    reset()
    close_history()

def get_completer():
    return readline.get_completer()

def make_opts(options, usage, version):
    parser = optparse.OptionParser(usage=usage, version=version)
    for opt in options:
        if not opt:
            continue
        otype, deft, dest, htype = opt[2:]
        if "store" in otype:
            parser.add_option(opt[0], opt[1], action=otype, default=deft, dest=dest, help=htype)
        else:
            parser.add_option(opt[0], opt[1], type=otype, default=deft, dest=dest, help=htype)
    return parser.parse_args()

def parse_cli(name="obot", version=None, opts=[], wd=None, usage=None, level="error"):
    import ob
    import ob.krn
    import ob.log
    ver = "%s %s" % (name.upper(), version)
    usage = usage or "%s [options] cmd"  % name
    opt, arguments = make_opts(opts, usage, ver)
    cfg = Cfg()
    ob.update(cfg, vars(opt))
    cfg.args = arguments
    cfg.debug = False
    cfg.name = name
    cfg.version = version
    cfg.workdir = cfg.workdir or wd or hd(".%s" % cfg.name)
    cfg.txt = " ".join(cfg.args)
    sp = os.path.join(cfg.workdir, "store") + os.sep
    if not os.path.exists(sp):
        cdir(sp)
    ob.workdir = cfg.workdir
    ob.update(ob.k.cfg, cfg)
    ob.log.level(cfg.level or level)
    st = time.ctime(time.time())
    txt = "%s started (%s) at %s" % (cfg.name.upper(), cfg.level, st)
    logging.warning(txt)
    txt = "logging at %s" % ob.log.logfiled
    logging.warning(txt)
    return cfg

def set_completer(commands):
    global cmds
    cmds = commands
    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")
    atexit.register(lambda: readline.set_completer(None))

def writepid():
    from ob import k
    path = os.path.join(k.cfg.workdir, "obot.pid")
    f = open(path, 'w')
    f.write(str(os.getpid()))
    f.flush()
    f.close()
