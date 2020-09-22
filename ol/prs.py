# OLIB - object library
#
#

import ol
import sys

class Token(ol.Object):

    def __init__(self, txt):
        super().__init__()
        self.txt = txt

class Option(ol.Default):

    def __init__(self, txt):
        super().__init__()
        if txt.startswith("--"):
            self.opt = txt[2:]
        if txt.startswith("-"):
            self.opt = txt[1:]

class Getter(ol.Object):

    def __init__(self, txt):
        super().__init__()
        try:
            pre, post = txt.split("==")
        except ValueError:
            pre = post = ""
        if pre:
            self[pre] = post

class Setter(ol.Object):

    def __init__(self, txt):
        super().__init__()
        try:
            pre, post = txt.split("=")
        except ValueError:
            pre = post = ""
        if pre:
            self[pre] = post

class Skip(ol.Object):

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

class Timed(ol.Object):

    def __init__(self, txt):
        super().__init__()
        v = 0
        vv = 0
        try:
            pre, post = txt.split("-")
            v = ol.tms.parse_time(pre)
            vv = ol.tms.parse_time(post)
        except ValueError:
            pass
        if not v or not vv:
            try:
                vv = ol.tms.parse_time(txt)
            except ValueError:
                vv = 0
            v = 0
        if v:
            self["from"] = time.time() - v
        if vv:
            self["to"] = time.time() - vv

def parse_cli():
    parsed = ol.Default()
    parse(parsed, " ".join(sys.argv[1:]))
    return parsed

def parse(o, txt):
    args = []
    o.origtxt = txt
    o.gets = ol.Object()
    o.opts = ol.Object()
    o.sets = ol.Object()
    o.skip = ol.Object()
    o.timed = ol.Object()
    o.index = None
    for token in [Token(txt) for txt in txt.split()]:
        s = Skip(token.txt)
        if s:
            ol.update(o.skip, s)
            token.txt = token.txt[:-1]
        t = Timed(token.txt)
        if t:
            ol.update(o.timed, t)
            continue
        g = Getter(token.txt)
        if g:
            ol.update(o.gets, g)
            continue
        s = Setter(token.txt)
        if s:
            ol.update(o.sets, s)
            ol.update(o, s)
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
