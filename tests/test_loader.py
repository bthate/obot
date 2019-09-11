""" loader tests. """

import os
import unittest

from ob.ldr import Loader

class Test_Loader(unittest.TestCase):

    def test_names(self):
        l = Loader()
        l.load_mod("ob.ldr")
        p = l.save()
        ll = Loader()
        ll.load(p)
        self.assertTrue("ob.ldr" in ll.table)
