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
            if hasattr(self.__kwargs[key], "__call__"):
                return self.__kwargs[key]()
            else:
                return self.__kwargs[key]
        else:
            raise NoSuchValue("'%s' is an unknown value." % (key))

    def __str__(self):

        return "Container(%s)" % (self.__kwargs)

    def __repr__(self):

        return "Container(%s)" % (self.__kwargs)


class UpLook(object):

    """
    A class which maps user supplied variable lookup definitions to actual
    functions.

    This class should be initiated with one or more named arguments. The name
    of the arguments are free to choose.  The argument values can be either
    regular values or a lookup function.

    Lookup definitions have following format:

        ~<name>(<variable>, <default_value>)
        ~~<name>(<variable>, <default_value>)

    Default values are returned when executing the function raises an
    uplook.errors.NoSuchValue Exception.

    Values are accessible under <self.value>.

    """

    def __init__(self, **kwargs):

        self.__kwargs = kwargs
        self.__lookup = {}
        self.__user_defined_functions = []

        self.value = self.__processKwargs(kwargs)

    def __processKwargs(self, kwargs):

        """
        Replaces any keyword arguments lookup definition value with the value.

        :param kwargs: dict
        :rtype: dict
        """

        result = {}
        for key, value in kwargs.iteritems():
            if isinstance(value, dict):
                value = self.__processKwargs(value)
            elif isinstance(value, str) or isinstance(value, unicode):
                value = self.__replaceLookup(value)

            result[key] = value

        return Container(**result)

    def __replaceLookup(self, value):

        """
        Takes a string/unicode and if it matches a lookup definition, return its value

        :param value: string or unicode
        :rtype: string
        """

        m = re.match('(?P<type>~~?)(?P<function>\w*?)\((?P<ref>.*)?\)', value)

        if m is None:
            return value
        else:
            m = m.groupdict()

        if m["function"] not in self.__user_defined_functions:
            self.__user_defined_functions.append(m["function"])

        if self.__checkFunctionExists(m["function"]):
            if m["ref"] is None or m["ref"] == "":
                ref = Undef()
                default = Undef()
            else:
                ref, default = self.__processRef(m["ref"])

            if m["type"] == "~":
                return self.__generateStaticLookup(m["function"], ref, default)
            elif m["type"] == "~~":
                return self.__generateDynamicLookup(m["function"], ref, default)
        else:
            return None

    def __checkFunctionExists(self, function):

        """
        Verifies whether a function with name <function> has already been defined.

        :param function: The reference name of the function.
        :type function: str or unicode
        :rtype: bool
        """

        if function in self.__lookup:
            return True
        else:
            return False

    def __generateDynamicLookup(self, function, reference, default):

        """
        Returns a function which executes the registered lookup function.

        :param functions: The function's reference name.
        :type functions: str or unicode
        :param reference: The variable name for which a lookup needs to be done.
        :type reference: str or unicode
        :param default: The default value to return when the lookup returns NoSuchValue
        :rtype: function
        """

        def lookupNoRef():
            return self.__lookup[function]()

        def lookupRef():
            try:
                return self.__lookup[function](reference)
            except NoSuchValue:
                if isinstance(default, Undef):
                    raise NoSuchValue("'%s' does not return any value." % (reference))
                else:
                    return default

        if isinstance(reference, Undef):
            return lookupNoRef
        else:
            return lookupRef

    def __generateStaticLookup(self, function, reference, default):
        """
        Executes the lookup function and returns its value

        :param functions: The function's reference name.
        :type functions: str or unicode
        :param reference: The variable name for which a lookup needs to be done.
        :type reference: str or unicode
        :param default: The default value to return when the lookup returns NoSuchValue
        :rtype: str or unicode or int, float, ...
        """

        if isinstance(reference, Undef):
            return self.__lookup[function]()
        else:
            try:
                return self.__lookup[function](reference)
            except NoSuchValue:
                if isinstance(default, Undef):
                    raise NoSuchValue("'%s' does not return any value." % (reference))
                else:
                    return default

    def __processRef(self, ref):

        """
        Converts the reference value to a proper Python value.

        :param ref: The lookup reference value.
        :type ref: str or unicode
        :rtype: None, str, unicode, bool, int, float
        """

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

        return str("UpLook(%s)" % (self.dump()))

    def __str__(self):

        return str("UpLook(%s)" % (self.dump()))

    def __iter__(self):

        for item in self.value.__dict__["_Container__kwargs"]:
            yield item

    def dump(self, include_none=True):

        """
        Returns a dictionary of the current values.

        :param include_none: If <True> includes <None> values.
        :type include_none: bool
        :rtype: dict
        """

        def buildDict(result, data):

            for key, value in data.iteritems():
                if value is None and not include_none:
                    continue
                elif isinstance(value, Container):
                    result[key] = buildDict({}, value.__dict__["_Container__kwargs"])
                else:
                    result[key] = value
            return result

        return buildDict({}, self.value.__dict__["_Container__kwargs"])

    def get(self):

        """
        Returns self.value
        """

        return self.value

    def listFunctions(self):

        """
        Returns a generator returning all user registered functions.
        """

        for item in self.__user_defined_functions:
            yield item

    def iteritems(self):

        for key in self:
            yield (key, getattr(self.value, key))

    def registerLookup(self, key, function):

        """
        Registers <function> with name <key> so it can be used to perform static or dynamic lookups.

        :param key: The reference name of the function.
        :type key: str or unicode
        :param function: The function to register.
        :type function: function
        """

        self.__lookup[key] = function
        self.value = self.__processKwargs(self.__kwargs)
