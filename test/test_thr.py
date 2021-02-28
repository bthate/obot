# This file is placed in the Public Domain.

"test threads"

# imports

import unittest

from ob import cfg
from ob.thr import launch

from test.run import exec, consume, h

# classes

class Test_Threaded(unittest.TestCase):

    def test_thrs(self):
        thrs = []
        for x in range(cfg.index or 1):
            launch(tests, h)
        consume(events)

# functions

def tests(b):
    for cmd in h.cmds:
        events.extend(exec(cmd))

# runtime

events = []
