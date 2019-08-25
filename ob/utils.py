""" file related utility. """

import datetime
import fcntl
import json
import html.parser
import logging
import logging.handlers
import ob
import os
import re
import stat
import time
import types
import urllib
import urllib.error
import urllib.parse
import urllib.request
import _thread

def __dir__():
    return ('cdir', 'check_permissions', 'fntime', 'fromfile', 'get_name', 'get_url', 'hd', 'hook', 'kill', 'last', 'level', 'locked', 'strip_html', 'touch', 'unescape', 'urllib', 'useragent')

class DumpHandler(logging.StreamHandler):

    """ handles nothing. """

    propagate = False

    def emit(self, record):
        pass

def cdir(path):
    """ create directory. """
    if os.path.exists(path):
        return
    res = ""
    path = os.path.dirname(path)
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
    return True

def check_permissions(path, dirmask=0o700, filemask=0o600):
    """ set permissions of a dir/file. """
    uid = os.getuid()
    gid = os.getgid()
    try:
        stats = os.stat(path)
    except FileNotFoundError:
        return
    except OSError:
        dname = os.path.dirname(path)
        stats = os.stat(dname)
    if stats.st_uid != uid:
        os.chown(path, uid, gid)
    if os.path.isfile(path):
        mask = filemask
    else:
        mask = dirmask
    mode = oct(stat.S_IMODE(stats.st_mode))
    if mode != oct(mask):
        os.chmod(path, mask)

def fromfile(f):
    """ read from filedescriptor. """
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return json.load(f, object_hook=ob.types.hook)
    except:
        fcntl.flock(f, fcntl.LOCK_UN)
        raise

def last(otype):
    """ return the fn of the last save object. """
    fns = list(names(otype))
    if fns:
        return fns[-1]

def hook(fn):
    """ read json file from fn and create corresponding object. """
    t = fn.split(os.sep)[0]
    if not t:
        raise ob.errors.ENOFILE(fn)
    o = ob.types.get_cls(t)()
    try:
        o.load(fn)
    except json.decoder.JSONDecodeError:
        raise ob.errors.EJSON(fn)
    return o

def names(name, delta=None):
    """ show all object filenames on disk. """
    if not name:
        return []
    if not delta:
        delta = 0
    assert ob.workdir
    p = os.path.join(ob.workdir, "store", name) + os.sep
    res = []
    now = time.time()
    past = now + delta
    for rootdir, dirs, files in os.walk(p, topdown=True):
        for fn in files:
            fnn = os.path.join(rootdir, fn).split(os.path.join(ob.workdir, "store"))[-1]
            if delta:
                if ime(fnn) < past:
                    continue
            res.append(os.sep.join(fnn.split(os.sep)[1:]))
    return sorted(res, key=fntime)

def hd(*args):
    """ create filename below the homedir. """
    homedir = os.path.expanduser("~")
    return os.path.abspath(os.path.join(homedir, *args))

def fntime(daystr):
    """ convert filename into a timestamp. """
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    try:
        datestr, rest = datestr.rsplit(".", 1)
    except ValueError:
        rest = ""
    try:
        t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
        if rest:
            t += float("." + rest)
    except ValueError:
        t = 0
    return t

def touch(fname):
    """ create empty file. """
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except TypeError:
        pass

def locked(func):
    """ lock a function. """
    lock = _thread.allocate_lock()
    def lockedfunc(*args, **kwargs):
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            lock.release()
        return res
    return lockedfunc


def level(loglevel="error", logdir="", logfile="ob.log", nostream=False):
    """ initiate logging. """
    from ob.kernel import k
    if not logdir:
        logdir = os.path.join(hd(".obot", "logs"))
    logfile = os.path.join(logdir, logfile)
    if not os.path.exists(logfile):
        cdir(logfile)
    datefmt = '%H:%M:%S'
    format_time = "%(asctime)-8s %(message)-70s"
    format_plain = "%(message)-0s"
    loglevel = loglevel.upper()
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    try:
        logger.setLevel(loglevel)
    except ValueError:
        pass
    formatter = logging.Formatter(format_plain, datefmt)
    if nostream:
        dhandler = DumpHandler()
        dhandler.propagate = False
        dhandler.setLevel(loglevel)
        logger.addHandler(dhandler)
    else:
        handler = logging.StreamHandler()
        handler.propagate = False
        handler.setFormatter(formatter)
        handler.setLevel(loglevel)
        logger.addHandler(handler)
    formatter2 = logging.Formatter(format_time, datefmt)
    filehandler = logging.handlers.TimedRotatingFileHandler(logfile, 'midnight')
    filehandler.propagate = False
    filehandler.setFormatter(formatter2)
    filehandler.setLevel(loglevel)
    logger.addHandler(filehandler)
    return logger

def get_name(o):
    """ return name of object. """
    t = type(o)
    if t == types.ModuleType:
        return o.__name__
    try:
        n = "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    except AttributeError:
        try:
            n = "%s.%s" % (o.__class__.__name__, o.__name__)
        except AttributeError:
            try:
                n = o.__class__.__name__
            except AttributeError:
                n = o.__name__
    return n

def kill(thrname):
    """ kill a task. """
    for task in threading.enumerate():
        if thrname not in str(task):
            continue
        if "cancel" in dir(task):
            task.cancel()
        if "exit" in dir(task):
            task.exit()
        if "stop" in dir(task):
            task.stop()

def get_url(*args):
    """ grab a url. """
    url = urllib.parse.urlunparse(urllib.parse.urlparse(args[0]))
    logging.debug(url)
    req = urllib.request.Request(url, headers={"User-Agent": useragent()})
    resp = urllib.request.urlopen(req)
    resp.data = resp.read()
    return resp

def strip_html(text):
    """ strip html codes from text. """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def useragent():
    """ display useragent. """
    return 'Mozilla/5.0 (X11; Linux x86_64) OB +http://bitbucket.org/bthate/ob)'

def unescape(text):
    """ convert characters in text. """
    txt = re.sub(r"\s+", " ", text)
    return html.parser.HTMLParser().unescape(txt)
