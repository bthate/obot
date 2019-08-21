import logging
import os
import unittest

from ob import WORKDIR
from ob import Object
from ob.kernel import  k

class ENOTCOMPAT(Exception):
    pass

class Test_Core(unittest.TestCase):

    def test_load2(self):
        o = Object()
        o.bla = "mekker"
        p = o.save()
        oo = Object().load(p)
        self.assertEqual(oo.bla, "mekker")

    def test_save(self):
        o = Object()
        p = o.save()
        self.assertTrue(os.path.exists(os.path.join(WORKDIR, "store", p)))
