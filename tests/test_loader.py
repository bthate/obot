""" loader tests. """

import os
import unittest

from ob.loader import Loader

class Test_Loader(unittest.TestCase):

    def test_names(self):
        l = Loader()
        l.load_mod("ob.loader")
        p = l.save()
        ll = Loader()
        ll.load(p)
        self.assertTrue("ob.loader" in ll.table)
