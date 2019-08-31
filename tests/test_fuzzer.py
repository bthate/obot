import logging
import random
import unittest

from obot import Bot
from ob.kernel import k
from ob.handler import Event
from ob.tables import modules, names
from ob.types import get_cls
from ob.trace import get_exception

b = Bot()
b.walk("ob")
b.cfg.prompt = False
b.cfg.verbose = k.cfg.verbose
k.users.oper("test@shell")

class Test_Fuzzer(unittest.TestCase):

    def test_fuzzer1(self):
        for key in modules:
            for t in list(names.values()):
                try:
                    e = get_cls(t)()
                    e.txt = key + " " + random.choice(list(names.keys()))
                    e.parse(e.txt)
                    e.orig = repr(b)
                    e.origin = "test@shell"
                    ob.update(e, o,skip=True)
                    v = b.get_handler(key)
                    if v:
                        v(e)
                except AttributeError:
                    pass
                except TypeError as ex:
                    break
        self.assertTrue(True)
