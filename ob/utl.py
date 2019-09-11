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

timestrings = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S",
    "%a, %d %b %Y %H:%M:%S",
    "%d %b %a %H:%M:%S %Y %Z",
    "%d %b %a %H:%M:%S %Y %z",
    "%a %d %b %H:%M:%S %Y %z",
    "%a %b %d %H:%M:%S %Y",
    "%d %b %Y %H:%M:%S",
    "%a %b %d %H:%M:%S %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dt%H:%M:%S+00:00",
    "%a, %d %b %Y %H:%M:%S +0000",
    "%d %b %Y %H:%M:%S +0000",
]

year_formats = [
    "%b %H:%M",
    "%b %H:%M:%S",
    "%a %H:%M %Y",
    "%a %H:%M",
    "%a %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m %H:%M:%S",
    "%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d-%m-%Y %H:%M",
    "%d-%m %H:%M",
    "%m-%d %H:%M",
    "%H:%M:%S",
    "%H:%M"
]

allowedchars = string.ascii_letters + string.digits + '_+/$.-'
resume = {}

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
        raise ob.errors.ENOFILE(fn)
    o = ob.types.get_cls(t)()
    try:
        o.load(fn)
    except json.decoder.JSONDecodeError:
        raise ob.errors.EJSON(fn)
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
        m = None
        try:
            m = h.walk(mn)
        except ModuleNotFoundError:
            try:
                m = h.walk("ob.%s" % mn)
            except ModuleNotFoundError:
                try:
                    m = h.walk("obot.%s" % mn)
                except ModuleNotFoundError:
                    try:
                        m = h.walk("%s.%s" % (h.cfg.name, mn))
                    except ModuleNotFoundError:
                        logging.error("not found %s" % mn)
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


def reset():
    if "old" in resume:
        termios.tcsetattr(resume["fd"], termios.TCSADRAIN, resume["old"])

def save():
    resume["fd"] = sys.stdin.fileno()
    resume["old"] = setup(sys.stdin.fileno())
    atexit.register(reset)

def setup(fd):
    old = termios.tcgetattr(fd)
    return old

def get_exception(txt="", sep=""):
    from ob import k
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for elem in trace:
        fname = elem[0]
        linenr = elem[1]
        func = elem[2]
        plugfile = fname[:-3].split(os.sep)
        mod = []
        for elememt in plugfile[::-1]:
            mod.append(elememt)
            if elememt == "ob":
                break
        ownname = '.'.join(mod[::-1])
        result += "%s:%s %s %s " % (ownname, linenr, func, sep)
    res = "%s%s: %s %s" % (result, exctype, excvalue, str(txt))
    del trace
    if k.cfg.bork:
        _thread.interrupt_main()
    return res

def get_from(nr=2):
    frame = sys._getframe(nr)
    if not frame:
        return frame
    if not frame.f_back:
        return frame
    filename = frame.f_back.f_code.co_filename
    linenr = frame.f_back.f_lineno
    plugfile = filename.split(os.sep)
    del frame
    return ".".join(plugfile[-2:]) + ":" + str(linenr)

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

def day():
    return str(datetime.datetime.today()).split()[0]

def days(path):
    return elapsed(time.time() - fntime(path))

def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if nrdays and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    elif sec < 1 or not short:
        txt += "%.3fs" % sec
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def get_time(daystr):
    for f in year_formats:
        try:
            t = time.mktime(time.strptime(daystr, f))
            return t
        except Exception:
            pass

def now():
    return str(datetime.datetime.now()).split()[0]

def parse_date(daystr):
    val = 0
    total = 0
    for c in daystr:
        if c not in ["s", "m", "h", "d", "w", "y"]:
            val += c
            continue
        if c == "y":
            total += val * 3600*24*365
        if c == "w":
            total += val * 3600*24*7
        elif c == "d":
            total += val * 3600*24
        elif c == "h":
            total += val * 3600
        elif c == "m":
            total += val * 60
        else:
            total += val
        val = 0
    return total

def rtime():
    res = str(datetime.datetime.now()).replace(" ", os.sep)
    return res

def today():
    return datetime.datetime.today().timestamp()

def to_day(daystring):
    line = ""
    daystr = str(daystring)
    for word in daystr.split():
        if "-" in word:
            line += word + " "
        elif ":" in word:
            line += word
    if "-" not in line:
        line = day() + " " + line
    try:
        return get_time(line.strip())
    except ValueError:
        pass

def to_time(daystr):
    daystr = daystr.strip()
    if "," in daystr:
        daystr = " ".join(daystr.split(None)[1:7])
    elif "(" in daystr:
        daystr = " ".join(daystr.split(None)[:-1])
    else:
        try:
            d, h = daystr.split("T")
            h = h[:7]
            daystr = " ".join([d, h])
        except (ValueError, IndexError):
            pass
    res = 0
    for tstring in timestrings:
        try:
            res = time.mktime(time.strptime(daystr, tstring))
        except ValueError:
            try:
                res = time.mktime(time.strptime(" ".join(daystr.split()[:-1]), tstring))
            except ValueError:
                pass
        if res:
            break
    return res
