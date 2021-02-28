# This file is placed in the Public Domain.

"introspection"

# imports

import inspect
import pkgutil

from . import Object, ObjectList, update
from .utl import direct, mods, spl, os

# functions

def find_cmds(mod):
    cmds = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in cmds:
                    cmds[key] = o
    return cmds

def find_funcs(mod):
    funcs = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in funcs:
                    funcs[key] = "%s.%s" % (o.__module__, o.__name__)
    return funcs

def find_mods(mod):
    mods = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in mods:
                    mods[key] = o.__module__
    return mods

def find_classes(mod):
    nms = ObjectList()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            nms.append(o.__name__, t)
    return nms

def find_class(mod):
    mds = ObjectList()
    for key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            mds.append(o.__name__, o.__module__)
    return mds

def find_names(mod):
    tps = Object()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            if t not in tps:
                tps[o.__name__.lower()] = t
    return tps

def find_all(names):
    for pn in spl(names):
        mod = direct(pn)
        if "__file__" in dir(mod) and mod.__file__:
            pths = [os.path.dirname(mod.__file__),]
            for m, n, p in pkgutil.iter_modules(pths):
                fqn = "%s.%s" % (pn, n)
                yield fqn
        else:
            p = list(mod.__path__)[0]
            if not os.path.exists(p):
                continue
            for mn in [x[:-3] for x in os.listdir(p) if x.endswith(".py")]:
                fqn = "%s.%s" % (pn, mn)
                yield fqn

def get_names(pkgs):
    res = Object()
    for pkg in spl(pkgs):
        for mod in mods(pkg):
            n = find_names(mod)
            update(res, n)
    return res

def walk(names):
    oo = Object()
    oo.pnames = Object()
    oo.names = ObjectList()
    oo.modnames = Object()
    for mn in find_all(names):
        mod = direct(mn)
        oo.pnames[mn.split(".")[-1]] = mn
        update(oo.modnames, find_mods(mod))
        oo.names.update(find_names(mod))
    return oo
