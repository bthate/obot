""" edit command tests. """

import json
import logging
import os
import unittest

from ob import k
from ob.cmd import Command

class Test_Ed(unittest.TestCase):

    def setUp(self):
        k.start()
        
    def test_ed1(self):
        c = Command()
        c.parse("ed log txt==bla txt=mekker")
        k.put(c)
        c.wait()
        self.assertEqual(c.result, [])
