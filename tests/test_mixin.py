""" configuration tests """

import unittest

from ob.cls import Dict

class TestObject(Dict):

    def __init__(self):
        self.bla = "test"

class TestTestDict(TestObject, Dict):

    pass

class Test_Mixin(unittest.TestCase):

    def test_mixin1(self):
        d = TestTestDict()
        self.assertEqual(d.bla, "test")

    def test_mixin2(self):
        d = TestTestDict()
        d.bla = "mekker"
        p = d.save()
        e = Dict().load(p)
        self.assertEqual(e.bla, "mekker")
