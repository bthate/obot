import logging
import os
import unittest

from ob import workdir
from ob.cls import Dict

class ENOTCOMPAT(Exception):
    pass

class Test_Core(unittest.TestCase):

    def test_load2(self):
        o = Dict()
        o.bla = "mekker"
        p = o.save()
        oo = Dict().load(p)
        self.assertEqual(oo.bla, "mekker")

    def test_save(self):
        o = Dict()
        p = o.save()
        self.assertTrue(os.path.exists(os.path.join(workdir, "store", p)))
