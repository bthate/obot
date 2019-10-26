import logging
import random
import unittest

from obot import Bot
from ob import k
from ob.evt import Event
from ob.typ import get_cls
from ob.trc import get_exception

k.cfg.prompt = False
k.walk("obot")
k.walk("ob")
k.users.oper("test@shell")

class Test_Fuzzer(unittest.TestCase):

    def test_fuzzer1(self):
        for key in k.modules:
            print(key)
            for n in k.names:
                print(n)
                t = k.names[n]
                try:
                    e = get_cls(t)()
                    e.txt = key + " " + random.choice(list(k.names))
                    e.parse(e.txt)
                    e.orig = repr(b)
                    e.origin = "test@shell"
                    e.update(o)
                    v = k.get_cmd(key)
                    if v:
                        v(e)
                except AttributeError:
                    pass
                except TypeError as ex:
                    break
        self.assertTrue(True)
