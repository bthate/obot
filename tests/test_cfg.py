""" configuration tests """

import unittest
import ob

class O(object):

    def bla(self):
        return "yo!"

class Test_Cfg(unittest.TestCase):

    def test_normal(self):
        o = O()
        o.bla = "bla"
        with self.assertRaises(TypeError) as x:
            res = o.bla()

    def test_last1(self):
        cfg = ob.Cfg()
        cfg.last = "bla"
        self.assertEqual(cfg.last, "bla")

    def test_last3(self):
        cfg = ob.Cfg()
        cfg.last = "bla"
        with self.assertRaises(TypeError) as x:
            l = cfg.last()
