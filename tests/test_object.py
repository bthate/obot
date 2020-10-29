# OBOT - 24/7 channel daemon
#
#

import ol
import types
import unittest

from ol.dbs import last
from ol.obj import Object, load, save

class Test_Object(unittest.TestCase):

    def test_empty(self):
        o = Object()
        self.assertTrue(not o) 

    def test_final(self):
        o = Object()
        o.last = "bla"
        last(o)
        self.assertEqual(o.last, "bla")

    def test_stamp(self):
        o = Object()
        stp = save(o)
        self.assertTrue("Object" in stp)

    def test_attribute(self):
        o = Object()
        o.bla = "test"
        p = save(o)
        oo = Object()
        load(oo, p)
        self.assertEqual(oo.bla, "test")

    def test_changeattr(self):
        o = Object()
        o.bla = "test"
        p = save(o)
        oo = Object()
        load(oo, p)
        oo.bla = "mekker"
        pp = save(oo)
        ooo = Object()
        load(ooo, pp)
        self.assertEqual(ooo.bla, "mekker")

    def test_last(self):
        o = Object()
        o.bla = "test"
        save(o)
        oo = Object()
        last(oo)
        self.assertEqual(oo.bla, "test")

    def test_lastest(self):
        o = Object()
        o.bla = "test"
        save(o)
        oo = Object()
        last(oo)
        oo.bla = "mekker"
        save(oo)
        ooo = Object()
        last(ooo)
        self.assertEqual(ooo.bla, "mekker")
