""" utility functios. """

import atexit
import datetime
import fcntl
import json
import html.parser
import logging
import logging.handlers
import os
import random
import re
import sys
import stat
import string
import termios
import time
import traceback
import types
import urllib
import urllib.error
import urllib.parse
import urllib.request
import _thread

allowedchars = string.ascii_letters + string.digits + '_+/$.-'
resume = {}

from ob.trc import get_exception

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

def consume(elems):
    """ call wait on all elements. """
    fixed = []
    for e in elems:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            elems.remove(f)
        except ValueError:
            continue

def fromfile(f):
    """ read from filedescriptor. """
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return json.load(f, object_hook=ob.types.hook)
    except:
        fcntl.flock(f, fcntl.LOCK_UN)
        raise

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

def get_url(*args):
    """ grab a url. """
    url = urllib.parse.urlunparse(urllib.parse.urlparse(args[0]))
    logging.debug(url)
    req = urllib.request.Request(url, headers={"User-Agent": useragent()})
    resp = urllib.request.urlopen(req)
    resp.data = resp.read()
    return resp

def hd(*args):
    """ create filename below the homedir. """
    homedir = os.path.expanduser("~")
    return os.path.abspath(os.path.join(homedir, *args))

def hook(fn):
    """ read json file from fn and create corresponding object. """
    t = fn.split(os.sep)[0]
    if not t:
        raise ob.err.ENOFILE(fn)
    o = ob.types.get_cls(t)()
    try:
        o.load(fn)
    except json.decoder.JSONDecodeError:
        raise ob.err.EJSON(fn)
    return o

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

def last(otype):
    """ return the fn of the last save object. """
    fns = list(names(otype))
    if fns:
        return fns[-1]

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
    lockedfunc.__doc__ = func.__doc__
    return lockedfunc

def match(a, b):
    """ match in items of b are in string a. """
    for n in b:
        if n in a:
            return True
    return False        

def mods(h, ms):
    """ walk packages and load modules into the handler. """
    modules = []
    for mn in ms.split(","):
        if not mn:
            continue
        m = None
        try:
            m = h.walk(mn)
        except ModuleNotFoundError as ex:
            if mn not in str(ex):
                logging.error(get_exception())
                return modules
            try:
                m = h.walk("ob.%s" % mn)
            except ModuleNotFoundError as ex:
                if mn not in str(ex):
                    logging.error(get_exception())
                    return modules
                try:
                    m = h.walk("obot.%s" % mn)
                except ModuleNotFoundError as ex:
                    if mn not in str(ex):
                        logging.error(get_exception())
                        return modules
                    try:
                        m = h.walk("%s.%s" % (h.cfg.name, mn))
                    except ModuleNotFoundError:
                        try:
                            m = h.walk("obot.cmd.%s" % mn)
                        except ModuleNotFoundError as ex:
                            if mn not in str(ex):
                                 logging.error(get_exception())
                            return modules
            if m:
                modules.extend(m)
    return modules

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

def randomname():
    """ create a random name. """
    s = ""
    for x in range(8):
        s += random.choice(allowedchars)
    return s

def strip_html(text):
    """ strip html codes from text. """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def touch(fname):
    """ create empty file. """
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except TypeError:
        pass

def useragent():
    """ display useragent. """
    return 'Mozilla/5.0 (X11; Linux x86_64) OB +http://bitbucket.org/bthate/ob)'

def unescape(text):
    """ convert characters in text. """
    txt = re.sub(r"\s+", " ", text)
    return html.parser.HTMLParser().unescape(txt)
