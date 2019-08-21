""" edit command tests. """

import json
import logging
import ob
import os
import unittest

class Log(ob.Object):

    txt = "bla"

l = Log()

class Test_Edit(unittest.TestCase):

    def setUp(self):
        l.txt = "bla"
        
    def test_ed1(self):
        c = ob.command.Command()
        c.parse("ed log txt==bla txt=mekker")
        ob.generic.edit(l, c.setter)
        self.assertEqual(l.txt, "mekker")

    def test_ed2(self):
        c = ob.command.Command()
        c.parse("ed")
        ob.generic.edit(l, c.setter)
        self.assertTrue(True, True)

    def test_ed3(self):
        c = ob.command.Command()
        c.parse("ed log txt=#bla")
        ob.generic.edit(l, c.setter)
        self.assertEqual(l.txt, "#bla")

    def test_ed4(self):
        c = ob.command.Command()
        c.parse("ed log txt==#bla txt=mekker2")
        ob.generic.edit(l, c.setter)
        self.assertEqual(l.txt, "mekker2")

    def test_ed5(self):
        c = ob.command.Command()
        c.parse("ed log txt==mekker txt=bla1,bla2")
        ob.generic.edit(l, c.setter)
        self.assertEqual(l.txt, ["bla1", "bla2"])

    def test_ed6(self):
        c = ob.command.Command()
        c.parse("ed log txt==bla txt=#mekker")
        ob.generic.edit(l, c.setter)
        self.assertEqual(l.txt, "#mekker")
