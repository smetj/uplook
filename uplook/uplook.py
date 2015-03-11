#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uplook.py
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

import sys
import re
from .errors import NoSuchFunction, NoSuchValue


class Undef(object):
    pass


class Container(object):

    def __init__(self, **kwargs):

        self.__kwargs = kwargs
        self.__setattr__ = self.__setattr

    def __setattr(self, key, value):

        raise Exception("This object is read only.")

    def __getattr__(self, key):

        if key in self.__kwargs:
            if hasattr(self.__kwargs[key], '__call__'):
                return self.__kwargs[key]()
            else:
                return self.__kwargs[key]
        else:
            raise NoSuchValue("'%s' is an unknown value." % (key))


class UpLook(object):

    """
    A class which maps user supplied variable lookup definitions to actual functions.

    This class should be initiated with one or more named arguments.  The name of the arguments
    are free to choose.  The argument values can be either regular values or a lookup function.

    Lookup definitions have following format:

        - ~<name>(<variable>, <default_value>)
        - ~~<name>(<variable>, <default_value>)


    """

    def __init__(self, lookup={}, **kwargs):

        self.__lookup = lookup
        self.__functions = []
        self.__processInput(kwargs)

    def __processInput(self, kwargs):

        result = {}

        for entry in self.__deconstructInput(kwargs):
            if entry["type"] == "regular":
                result[entry["key"]] = entry["value"]
            elif self.__checkFunctionExists(entry["function"]):
                if entry["type"] == "~":
                    if isinstance(entry["ref"], Undef):
                        result[entry["key"]] = self.__lookup[entry["function"]]()
                    else:
                        try:
                            result[entry["key"]] = self.__lookup[entry["function"]](entry["ref"])
                        except NoSuchValue:
                            if isinstance(entry["default"], Undef):
                                raise NoSuchValue("'%s' does not return any value." % (entry["ref"]))
                            else:
                                result[entry["key"]] = entry["default"]
                elif entry["type"] == "~~":
                    result[entry["key"]] = self.__generateLookup(entry["function"], entry["ref"], entry["default"])

            if "function" in entry and entry["function"] not in self.__functions:
                self.__functions.append(entry["function"])

        self.value = Container(**result)

    def __generateLookup(self, f, r, d):

        def lookupNoRef():
            return self.__lookup[f]()

        def lookupRef():
            try:
                return self.__lookup[f](r)
            except NoSuchValue:
                if isinstance(d, Undef):
                    raise NoSuchValue("'%s' does not return any value." % (r))
                else:
                    return d

        if isinstance(r, Undef):
            return lookupNoRef
        else:
            return lookupRef

    def __generateLookupNoRef(self, f):

        def lookup():
            return self.__lookup[f]()
        return lookup

    def __checkFunctionExists(self, f):

        if f in self.__lookup:
            return True
        else:
            raise NoSuchFunction("A function with name '%s' has not been registered yet." % (f))

    def __deconstructInput(self, kwargs):

        for key, value in kwargs.iteritems():
            if isinstance(value, str) or isinstance(value, unicode):
                m = re.match('(?P<type>~~?)(?P<function>\w*?)\((?P<ref>.*)?\)', value)
                if m is None:
                    yield {"type": "regular", "key": key, "value": value, "function": Undef(), "ref": Undef(), "default": Undef()}
                elif m.group("ref") == "":
                    yield {"type": m.group("type"), "key": key, "function": m.group("function"), "ref": Undef(), "default": Undef()}
                else:
                    ref, default = self.__processRef(m.group("ref"))
                    yield {"type": m.group("type"), "key": key, "function": m.group("function"), "ref": ref, "default": default}
            else:
                yield ("regular", value)

    def __processRef(self, ref):

        def getString(value):

            if value is None:
                return Undef()
            elif value.endswith('"') and value.endswith('"'):
                return value.replace('"', '')
            elif value == "true":
                return True
            elif value == "false":
                return False
            elif value == "none":
                return None
            elif re.match('^\d+$', value):
                return int(value)
            elif re.match('^\d+\.\d+$', value):
                return float(value)
            else:
                raise Exception("Invalid value '%s'." % (value))

        m = re.match('^((\"?.*?\"?)|false|true|none)(?:,\s*((\"?.*?\"?)|false|true|none))?$', ref)
        if m is not None:
            return (getString(m.group(1)), getString(m.group(3)))
        else:
            raise Exception("Illegal input '%s'." % (ref))

    def __repr__(self):

        return str("UpLook(%s)" % (self.raw()))

    def raw(self, include_none=True):

        """Returns a dictionary of the current values.

        When <include_none> is set to False then None values will be omitted."""

        result = {key: getattr(self.value, key) for key, value in self.value.__dict__["_Container__kwargs"].iteritems()}

        if include_none:
            return result
        else:
            return {key: value for key, value in result.iteritems() if value if not None}

    def registerLookup(self, key, function):

        """Registers <function> with name <key> so it can be referenced when defining a static or dynamic lookup value."""

        self.__lookup[key] = function

    def listDefinedFunctions(self):

        """Returns a list of all user defined functions"""

        return self.__functions
