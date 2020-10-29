# OBOT - 24/7 channel daemon
#
#

"introspection (int)"

import importlib
import inspect
import pkgutil

from ob.obj import Object
from ob.obl import Ol

def find_cmds(mod):
    "find commands"
    cmds = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                cmds[key] = o
    return cmds

def find_funcs(mod):
    "find full qualifed names of commands"
    funcs = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                funcs[key] = "%s.%s" % (o.__module__, o.__name__)
    return funcs

def find_mods(mod):
    "find modules of commands"
    mods = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                mods[key] = o.__module__
    return mods

def find_classes(mod):
    "find classes and their full qualified names"
    nms = Ol()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, ol.Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            nms.append(o.__name__, t)
    return nms

def find_class(mod):
    "find module of classes"
    mds = Ol()
    for key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            mds.append(o.__name__, o.__module__)
    return mds

def find_names(mod):
    "find modules of commands"
    tps = Ol()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            tps.append(o.__name__.lower(), t)
    return tps

def walk(names):
    "walk over packages and scan their modules"
    k = ol.krn.get_kernel()
    for name in names.split(","):
        spec = importlib.util.find_spec(name)
        if not spec:
            continue
        pkg = importlib.util.module_from_spec(spec)
        pn = getattr(pkg, "__path__", None)
        if not pn:
            continue
        for mi in pkgutil.iter_modules(pn):
            mn = "%s.%s" % (name, mi.name)
            mod = ol.utl.direct(mn)
            update(k.cmds, find_cmds(mod))
            update(k.funcs, find_funcs(mod))
            update(k.mods, find_mods(mod))
            update(k.names, find_names(mod))
            update(k.classes, find_class(mod))
