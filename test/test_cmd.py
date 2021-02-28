# This file is placed in the Public Domain.

"run all commands"

# imports

import unittest

from ob import cfg

from test.run import exec, h

# classes

class Test_Cmd(unittest.TestCase):

    def test_cmds(self):
        for x in range(cfg.index or 1):
            for cmd in h.cmds:
                exec(cmd)
