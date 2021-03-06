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
from uplook.errors import NoSuchLookupFunction, NoSuchValue, LookupFunctionError
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


def badLookup():
    raise Exception("I'm a bad lookupfunction")

def badLookup2(param):
    raise Exception("I'm a bad lookupfunction")


class TestUplook(unittest.TestCase):

    def test_getNormalValue(self):

        u = UpLook(one="een")
        self.assertEqual(u.value.one, "een")

    def test_getDictValue(self):

        u = UpLook(data={"one": 1})
        self.assertEqual(u.value.data, {"one": 1})

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

    def test_getNonExistingValue(self):

        err = False
        u = UpLook(one="een")
        try:
            u.value.two
        except Exception as err:
            self.assertTrue(err, isinstance(err, NoSuchValue))

    def test_getValueUnregisteredLookup(self):

        u = UpLook(one='~lookup()')
        try:
            u.registerLookup("lookupx", getHello)
        except Exception as err:
            self.assertTrue(err, isinstance(err, NoSuchLookupFunction))

    def test_getStaticLookupDefault(self):

        u = UpLook(one='~lookup("four", "default")')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.one, "default")

    def test_badDynamicLookupFunction(self):

        u = UpLook(one='~~lookup()')
        u.registerLookup("lookup", badLookup)
        try:
            u.value.one
        except Exception as err:
            self.assertTrue(err, isinstance(err, LookupFunctionError))

    def test_badStaticLookupFunction(self):

        try:
            u = UpLook(one='~lookup()')
            u.registerLookup("lookup", badLookup)
        except Exception as err:
            self.assertTrue(err, isinstance(err, LookupFunctionError))

    def test_badStaticLookupFunctionWithDefaultValue(self):

        u = UpLook(one='~lookup("test", true)')
        u.registerLookup("lookup", badLookup)
        self.assertTrue(u.value.one)

    def test_badDynamicLookupFunctionWithDefaultValue(self):

        u = UpLook(one='~~lookup("test", true)')
        u.registerLookup("lookup", badLookup)
        self.assertTrue(u.value.one)

    def test_setValue(self):

        u = UpLook(one=1, two=2)
        u.value.one = "een"
        self.assertEqual(u.value.one, "een")
        self.assertEqual(u.dump()["one"], "een")

    def test_defaultBoolType(self):

        u = UpLook(true='~lookup("fubar", true)', false='~lookup("fubar", false)')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.true, True)
        self.assertEqual(u.value.false, False)

    def test_defaultNoneType(self):

        u = UpLook(none='~lookup("fubar", null)')
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

    def test_defaultDictType(self):

        u = UpLook(true='~lookup("fubar", {"one": 1})', false='~lookup("fubar", {"two": 2})')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(u.value.true, {"one": 1})
        self.assertEqual(u.value.false, {"two": 2})

    def test_emptyDict(self):

        u = UpLook(one={})
        for key, value in u.get():
            self.assertTrue(isinstance(value, dict))

    def test_methodDumpWithNone(self):

        u = UpLook(one="een", two="twee", three=None)
        self.assertEqual(u.dump(), {"one": "een", "two": "twee", "three": None})

    def test_methodDumpWithoutNone(self):

        u = UpLook(one="een", two="twee", three=None)
        self.assertEqual(u.dump(include_none=False), {"one": "een", "two": "twee"})

    def test_methodGet(self):

        u = UpLook(one="een")
        value = u.get()
        self.assertEqual(value.one, "een")

    def test_methodListFunctions(self):

        u = UpLook(one='~lookup("one")')
        u.registerLookup("lookup", dictLookup)
        self.assertEqual(list(u.listFunctions()), ["lookup"])

    def test_methodRegisterLookup(self):

        u = UpLook(one='~lookup("one")')
        u.registerLookup("lookup", dictLookup)
        self.assertTrue("lookup" in list(u.listFunctions()))

    def test_methodIteritems(self):

        u = UpLook(one=1)

        for key, value in u.iteritems():
            self.assertTrue(key == "one")
            self.assertTrue(value == 1)

    def test_iterateOverKeyValue(self):

        u = UpLook(one=1)
        for key, value in u.get():
            self.assertTrue(key == "one")
            self.assertTrue(value == 1)

    def test_iterateOverKeyValueWithLookup(self):

        u = UpLook(data={"one": '~lookup("one")'})
        u.registerLookup("lookup", dictLookup)
        for key, value in u.value.data.items():
            self.assertEqual(value, "een")

    def test_slightlyMalformedExpression_1(self):

        db = {"one": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~lookup( "one" )')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one"] = "fubar"
        self.assertEqual(u.value.one, "fubar")

    def test_slightlyMalformedExpression_2(self):

        db = {"one": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~lookup ("one")')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one"] = "fubar"
        self.assertEqual(u.value.one, "fubar")

    def test_slightlyMalformedExpression_3(self):

        db = {"one": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~ lookup("one")')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one"] = "fubar"
        self.assertEqual(u.value.one, "fubar")

    def test_slightlyMalformedExpression_4(self):

        db = {"one": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~ lookup ( "one")')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one"] = "fubar"
        self.assertEqual(u.value.one, "fubar")

    def test_oddReferenceValue_1(self):

        db = {"one)": "een"}

        def getLookup(key):
            return db[key]

        u = UpLook(one='~~lookup("one)")')
        u.registerLookup("lookup", getLookup)
        self.assertEqual(u.value.one, "een")
        db["one)"] = "fubar"
        self.assertEqual(u.value.one, "fubar")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
