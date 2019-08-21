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
HISTFILE = ""

from ob.utils import cdir, hd, level
from ob.term import save, reset 
from ob.trace import get_exception

def __dir__():
    return ("daemon", "execute", "parse_cli")

opts = [
    ('-b', '', 'store_true', False, 'daemon', 'enable daemon mode.'),
    ('-d', '', 'string', "", 'workdir', 'set working directory.'),
    ('-l', '', 'string', 'error', 'level', 'loglevel.'),
    ('-m', '', 'string', '', 'modules', 'modules to load.'),
    ('-o', '', "string", "", 'options', "options to use."),
    ('-p', '', 'store_true', False, 'prompting', 'prompt for initial values.'),
    ('-v', '', 'store_true', False, 'verbose', 'enable verbose mode.'),
    ('', '--owner', "string", "", 'owner', "owner's userhost or JID.")
]

def close_history():
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
    writepid()
    os.setsid()
    os.umask(0)
    si = open("/dev/null", 'r')
    so = open("/dev/null", 'a+')
    se = open("/dev/null", 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def enable_history():
    from ob.kernel import k
    global HISTFILE
    HISTFILE = os.path.abspath(os.path.join(k.cfg.workdir, "history"))
    if os.path.exists(HISTFILE):
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

def parse_cli(name="ob", version=None, wd=None, usage=None):
    import ob
    import ob.kernel
    ver = "%s %s" % (name.upper(), version)
    usage = usage or "%s -m [mod1,mod2] cmd"  % name
    opt, arguments = make_opts(opts, usage, ver)
    cfg = ob.Cfg()
    cfg.update(vars(opt))
    cfg.args = arguments
    cfg.debug = False
    cfg.name = name
    cfg.version = version
    cfg.workdir = wd or cfg.workdir or hd(".%s" % name)
    sp = os.path.join(cfg.workdir, "store") + os.sep
    if not os.path.exists(sp):
        cdir(sp)
    ob.WORKDIR = cfg.workdir
    ob.kernel.k.cfg.update(cfg)
    level(cfg.level or "error")
    st = time.ctime(time.time())
    txt = "%s started (%s) at %s" % (cfg.name.upper(), cfg.level, st)
    logging.warning(txt)
    return cfg

def set_completer(commands):
    global cmds
    cmds = commands
    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")
    atexit.register(lambda: readline.set_completer(None))

def writepid():
    from ob.kernel import k
    path = os.path.join(k.cfg.workdir, "pidfile")
    f = open(path, 'w')
    f.write(str(os.getpid()))
    f.flush()
    f.close()
