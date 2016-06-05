#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

PROJECT = 'uplook'
VERSION = '1.0.0'

try:
    with open('README.rst', 'rt') as f:
        long_description = f.read()
except IOError:
    long_description = ''


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name=PROJECT,
    version=VERSION,

    description='A Python library and syntax to perform external lookups to retrieve argument values.',
    long_description=long_description,

    author='Jelle Smet',
    author_email='development@smetj.net',

    url='https://github.com/smetj/uplook',
    download_url='https://github.com/smetj/uplook/tarball/master',

    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Intended Audience :: Developers',
                 ],
    extras_require={
        'testing': ['pytest'],
    },
    platforms=['Linux'],
    test_suite='tests.uplook',
    cmdclass={'test': PyTest},
    scripts=[],
    provides=[],
    namespace_packages=[],
    packages=find_packages(),
    zip_safe=False,
)
