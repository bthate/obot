""" edit command tests. """

import json
import logging
import oper
import os
import unittest

from ob import Object
from ob.command import Command
from ob.obj import edit

class Log(Object):

    """ check class attribute edit as well. """

    def __init__(self):
        self.txt = "bla"

l = Log()

class Test_Edit(unittest.TestCase):

    def setUp(self):
        l.txt = "bla"
        
    def test_edit1(self):
        c = Command()
        c.parse("ed log txt==bla txt=mekker")
        edit(l, c.setter)
        self.assertEqual(l.txt, "mekker")

    def test_edit2(self):
        c = Command()
        c.parse("ed")
        edit(l, c.setter)
        self.assertTrue(True, True)

    def test_edit3(self):
        c = Command()
        c.parse("ed log txt=#bla")
        edit(l, c.setter)
        self.assertEqual(l.txt, "#bla")

    def test_edit4(self):
        c = Command()
        c.parse("ed log txt==#bla txt=mekker2")
        edit(l, c.setter)
        self.assertEqual(l.txt, "mekker2")

    def test_edit5(self):
        c = Command()
        c.parse("ed log txt==mekker txt=bla1,bla2")
        edit(l, c.setter)
        self.assertEqual(l.txt, ["bla1", "bla2"])

    def test_edit(self):
        c = Command()
        c.parse("ed log txt==bla txt=#mekker")
        edit(l, c.setter)
        self.assertEqual(l.txt, "#mekker")
