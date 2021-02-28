# This file is placed in the Public Domain.

"runtime"

# imports

import ob

from ob.hdl import Bused, Command

from test.prm import param

# classes

class Test(Bused):

    def direct(self, txt):
        if ob.cfg.verbose:
            print(txt)

# functions

def consume(elems):
    fixed = []
    res = []
    for e in elems:
        r = e.wait()
        res.append(r)
        fixed.append(e)
    for f in fixed:
        try:
            elems.remove(f)
        except ValueError:
            continue
    return res

def exec(cmd):
    exs = getattr(param, cmd, [""])
    e = list(exs)
    events = []
    nr = 0
    for ex in e:
        nr += 1
        txt = cmd + " " + ex
        e = Command(txt)
        h.put(e)
        events.append(e)
    return events

# runtime

events = []

h = Test()
h.walk("ob")
h.start()

for e in exec("rss https://www.reddit.com/r/python/.rss"):
    e.wait()
