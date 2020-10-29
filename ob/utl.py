# OBOT - 24/7 channel daemon
#
#

"utilities (utl)"

import importlib
import inspect
import os
import pwd
import sys
import traceback
import types

class ENOCLASS(Exception):

    "is not a class"

def cdir(path):
    "create directory"
    if os.path.exists(path):
        return
    res = ""
    path2, _fn = os.path.split(path)
    for p in path2.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
            os.chmod(padje, 0o700)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass

def direct(name):
    "load a module"
    return importlib.import_module(name)

def get_cls(name):
    "return a class"
    try:
        modname, clsname = name.rsplit(".", 1)
    except:
        raise ENOCLASS(name)
    if modname in sys.modules:
        mod = sys.modules[modname]
    else:
        mod = importlib.import_module(modname)
    return getattr(mod, clsname)

def find_modules(pkgs, skip=None):
    "locate modules"
    modules = []
    for pkg in pkgs.split(","):
        if skip is not None and skip not in pkg:
            continue
        try:
            p = direct(pkg)
        except ModuleNotFoundError:
            continue
        for _key, m in inspect.getmembers(p, inspect.ismodule):
            if m not in modules:
                modules.append(m)
    return modules

def get_cls(name):
    "return class from full qualified name"
    try:
        modname, clsname = name.rsplit(".", 1)
    except:
        raise ENOCLASS(name)
    if modname in sys.modules:
        mod = sys.modules[modname]
    else:
        mod = importlib.import_module(modname)
    return getattr(mod, clsname)

def get_exception(txt="", sep=" "):
    "print exception trace"
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = []
    for elem in trace:
        if elem[0].endswith(".py"):
            plugfile = elem[0][:-3].split(os.sep)
        else:
            plugfile = elem[0].split(os.sep)
        mod = []
        for element in plugfile[::-1]:
            mod.append(element)
            if "ol" in element or "mods" in element or "python3" in element:
                break
        ownname = ".".join(mod[::-1])
        result.append("%s:%s" % (ownname, elem[1]))
    res = "%s %s: %s %s" % (sep.join(result), exctype, excvalue, str(txt))
    del trace
    return res

def get_name(o):
    "return fully qualified name of an object"
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

def get_type(o):
    "return type of an object"
    t = type(o)
    if t == type:
        try:
            return "%s.%s" % (o.__module__, o.__name__)
        except AttributeError:
            pass
    return str(type(o)).split()[-1][1:-2]

def hook(fn):
    "construct object from filename"
    if fn.count(os.sep) > 3:
        oname = fn.split(os.sep)[-4:]
    else:
        oname = fn.split(os.sep)
    t = oname[0]
    if not t:
        raise ENOFILENAME(fn)
    import ob.obj
    o = get_cls(t)()
    ob.obj.load(o, fn)
    return o

def list_files(wd):
    "list files in directory"
    path = os.path.join(wd, "store")
    if not os.path.exists(path):
        return ""
    return " ".join(os.listdir(path))

def locked(l):
    "lock descriptor"
    def lockeddec(func, *args, **kwargs):
        def lockedfunc(*args, **kwargs):
            l.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                l.release()
            return res
        lockeddec.__doc__ = func.__doc__
        return lockedfunc
    return lockeddec

def privileges(name):
    "lower privileges"
    if os.getuid() != 0:
        return
    pwnam = pwd.getpwnam(name)
    os.setgroups([])
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)
    old_umask = os.umask(0o22)

def root():
    "check if root"
    if os.geteuid() != 0:
        return False
    return True

def spl(txt):
    "return comma splitted values"
    return iter([x for x in txt.split(",") if x])

def touch(fname):
    "touch a file"
    try:
        fd = os.open(fname, os.O_RDWR | os.O_CREAT)
        os.close(fd)
    except (IsADirectoryError, TypeError):
        pass
