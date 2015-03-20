#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_uplook.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import unittest
from uuid import uuid4
from uplook import UpLook
from uplook.errors import NoSuchFunction, NoSuchValue
from random import randint
import time


def dictLookup(key):

    values = {"one": "een",
              "two": "twee",
              "three": "drie"
              }

    try:
        return values[key]
    except KeyError:
        raise NoSuchValue("%s does not return any value" % (key))


def getUUID():

    return str(uuid4())


def getHello():

    return "hello"


def randomNumber(min, max):
    return randint(min, max)


def getTime():
    return time.time()


class TestUmiApi(unittest.TestCase):

    def test_getNormalValue(self):

        u = UpLook(one="een")
        self.assertEqual(u.value.one, "een")

    def test_getStaticLookupWithReference(self):

        u = UpLook(one='~lookup("one")')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.one, "een")

    def test_getStaticLookupWithoutReference(self):

        u = UpLook(one='~lookup()')
        u.registerLookup("lookup", getHello)
        self.assertEqual(u.value.one, "hello")

    def test_getDynamicLookupWithReference(self):

        db = {"one": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~lookup("one")')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one"] = "fubar"
        self.assertEqual(u.value.one, "fubar")

    def test_getDynamicLookupWithoutReference(self):

        u = UpLook(one='~~lookup()')
        u.registerLookup("lookup", getTime)
        self.assertNotEqual(u.value.one, u.value.one)

    def test_getNoneExistingValue(self):

        err = False
        u = UpLook(one="een")
        try:
            u.value.two
        except Exception as err:
            pass

        self.assertTrue(err, isinstance(err, NoSuchValue))

    def test_getValueUnregisteredLookup(self):

        u = UpLook(one='~lookup()')
        u.registerLookup("lookupx", getHello)
        self.assertEqual(u.value.one, None)

    def test_getStaticLookupDefault(self):

        u = UpLook(one='~lookup("four", "default")')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.one, "default")

    def test_defaultBoolType(self):

        u = UpLook(true='~lookup("fubar", true)', false='~lookup("fubar", false)')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.true, True)
        self.assertEqual(u.value.false, False)

    def test_defaultNoneType(self):

        u = UpLook(none='~lookup("fubar", none)')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.none, None)

    def test_defaultIntType(self):

        u = UpLook(int='~lookup("fubar", 10)')
        u.registerLookup("lookup", dictLookup)
        self.assertTrue(isinstance(u.value.int, int))

    def test_defaultFloatType(self):

        u = UpLook(float='~lookup("fubar", 10.5)')
        u.registerLookup("lookup", dictLookup)
        self.assertTrue(isinstance(u.value.float, float))

    def test_methodDumpWithNone(self):

        u = UpLook(one="een", two="twee", three=None)
        self.assertEqual(u.dump(), {"one": "een", "two": "twee", "three": None})

    def test_methodDumpWithoutNone(self):

        u = UpLook(one="een", two="twee", three=None)
        self.assertEqual(u.dump(include_none=False), {"one": "een", "two": "twee"})

    def test_methodListFunctions(self):

        u = UpLook(one='~lookup("one")')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(list(u.listFunctions()), ["lookup"])

    def test_methodRegisterLookup(self):

        u = UpLook(one='~lookup("one")')
        u.registerLookup("lookup", dictLookup)
        self.assertTrue("lookup" in list(u.listFunctions()))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
