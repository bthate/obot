""" object unittests. """

import os
import time
import unittest

from ob.cls import Dict

class Test_Dict(unittest.TestCase):

    def test_checkattribute(self):
        o = Dict()
        with self.failUnlessRaises(AttributeError):
            o.blabla

    def test_construct(self):
        o = Dict()
        self.assertEqual(type(o), Dict)

    def test_cleanpath(self):
        o = Dict()
        self.assertEqual(str(o), '{}')

    def test_cleanload(self):
        o = Dict()
        o.test = "blamek"
        p = o.save()
        oo = Dict().load(p)
        self.assertEqual(o.test, oo.test)

    def test_depth(self):
        o = Dict()
        o.state = Dict()
        o.state.starttime = time.time()
        self.assertTrue(isinstance(o.state.starttime, float)) 

    def test_settingattribute(self):
        o = Dict()
        o.bla = "mekker"
        self.assertEqual(o.bla, "mekker")

    def test_typed(self):
        o = Dict()
        self.assertEqual(o.__class__.__name__, "Dict")
        
    def test_underscore(self):
        o = Dict()
        o._bla = "mekker"
        self.assertEqual(o._bla, "mekker")
