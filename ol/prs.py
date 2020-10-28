# OLIB
#
#

"parse (prs)"

import sys
import time

from ol.dft import Default
from ol.obj import Object, update
from ol.tms import parse_time

class Token(Object):

    "basic token"

    def __init__(self, txt):
        super().__init__()
        self.txt = txt

class Option(Default):

    "token that starts with -- or -"

    def __init__(self, txt):
        super().__init__()
        if txt.startswith("--"):
            self.opt = txt[2:]
        if txt.startswith("-"):
            self.opt = txt[1:]

class Getter(Object):

    "token that contains =="

    def __init__(self, txt):
        super().__init__()
        try:
            pre, post = txt.split("==")
        except ValueError:
            pre = post = ""
        if pre:
            self[pre] = post

class Setter(Object):

    "token that contains ="

    def __init__(self, txt):
        super().__init__()
        try:
            pre, post = txt.split("=")
        except ValueError:
            pre = post = ""
        if pre:
            self[pre] = post

class Skip(Object):

    "token that endswith -"

    def __init__(self, txt):
        super().__init__()
        pre = ""
        if txt.endswith("-"):
            try:
                pre, _post = txt.split("=")
            except ValueError:
                try:
                    pre, _post = txt.split("==")
                except ValueError:
                    pre = txt
        if pre:
            self[pre] = True

class Timed(Object):

    "token that is a time"

    def __init__(self, txt):
        super().__init__()
        v = 0
        vv = 0
        try:
            pre, post = txt.split("-")
            v = parse_time(pre)
            vv = parse_time(post)
        except ValueError:
            pass
        if not v or not vv:
            try:
                vv = parse_time(txt)
            except ValueError:
                vv = 0
            v = 0
        if v:
            self["from"] = time.time() - v
        if vv:
            self["to"] = time.time() - vv

def parse_cli():
    "parse commandline"
    cfg = Default()
    parse(cfg, " ".join(sys.argv[1:]))
    return cfg

def parse(o, txt):
    "parse an object"
    args = []
    o.otxt = txt
    o.gets = Object()
    o.opts = Object()
    o.sets = Object()
    o.skip = Object()
    o.timed = ()
    o.txt = ""
    o.index = None
    for token in [Token(txt) for txt in txt.split()]:
        s = Skip(token.txt)
        if s:
            update(o.skip, s)
            token.txt = token.txt[:-1]
        t = Timed(token.txt)
        if t:
            update(o.timed, t)
            continue
        g = Getter(token.txt)
        if g:
            update(o.gets, g)
            continue
        s = Setter(token.txt)
        if s:
            update(o.sets, s)
            update(o, s)
            continue
        opt = Option(token.txt)
        if opt.opt:
            try:
                o.index = int(opt.opt)
                continue
            except ValueError:
                pass
            o.opts[opt.opt] = True
            continue
        args.append(token.txt)
    if not args:
        o.args = []
        o.cmd = ""
        o.rest = ""
        o.txt = ""
        return o
    o.cmd = args[0]
    o.args = args[1:]
    o.txt = " ".join(args)
    o.rest = " ".join(args[1:])
    return o
