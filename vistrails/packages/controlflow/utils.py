###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
from __future__ import division

from vistrails.core.modules.vistrails_module import ModuleError

from .fold import Fold, FoldWithModule

#################################################################################
## Some useful loop structures

class Map(FoldWithModule):
    """A Map module, that just appends the results in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        self.partialResult.append(self.elementResult)


class Filter(FoldWithModule):
    """A Filter module, that returns in a list only the results that satisfy a
    condition."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        if not isinstance(self.elementResult, bool):
            raise ModuleError(self,'The function applied to the elements of the\
list must return a boolean result.')

        if self.elementResult:
            self.partialResult.append(self.element)


class Sum(Fold):
    """A Sum module, that computes the sum of the elements in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = 0

    def operation(self):
        """Defining the operation..."""

        self.partialResult += self.element


class And(Fold):
    """An And module, that computes the And result among the elements
    in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = True

    def operation(self):
        """Defining the operation..."""

        self.partialResult = self.partialResult and bool(self.element)


class Or(Fold):
    """An Or module, that computes the Or result among the elements
    in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = False

    def operation(self):
        """Defining the operation..."""

        self.partialResult = self.partialResult or self.element


###############################################################################

import unittest
import urllib2

from vistrails.tests.utils import intercept_result, execute


class TestMap(unittest.TestCase):
    def test_simple(self):
        src = urllib2.quote('o = i + 1')
        with intercept_result(Map, 'Result') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', src)]),
                    ]),
                    ('Map', 'org.vistrails.vistrails.control_flow', [
                        ('InputPort', [('List', "['i']")]),
                        ('OutputPort', [('String', 'o')]),
                        ('InputList', [('List', '[1, 2, 8, 9.1]')]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'FunctionPort'),
                ],
                add_port_specs=[
                    (0, 'input', 'i',
                     'org.vistrails.vistrails.basic:Float'),
                    (0, 'output', 'o',
                     'org.vistrails.vistrails.basic:Float'),
                ]))
        self.assertEqual(results, [[2, 3, 9, 10.1]])

    def test_tuple(self):
        src = urllib2.quote('o = len(i[0]) + i[1]')
        with intercept_result(Map, 'Result') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', src)]),
                    ]),
                    ('Map', 'org.vistrails.vistrails.control_flow', [
                        ('InputPort', [('List', "['i']")]),
                        ('OutputPort', [('String', 'o')]),
                        ('InputList', [('List',
                            '[("aa", 1), ("", 8), ("a", 4)]')]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'FunctionPort'),
                ],
                add_port_specs=[
                    (0, 'input', 'i',
                     'org.vistrails.vistrails.basic:String,org.vistrails.vistrails.basic:Integer'),
                    (0, 'output', 'o',
                     'org.vistrails.vistrails.basic:Float'),
                ]))
        self.assertEqual(results, [[3, 8, 5]])

    def test_multiple(self):
        src = urllib2.quote('o = i + j')
        with intercept_result(Map, 'Result') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', src)]),
                    ]),
                    ('Map', 'org.vistrails.vistrails.control_flow', [
                        ('InputPort', [('List', "['i', 'j']")]),
                        ('OutputPort', [('String', 'o')]),
                        ('InputList', [('List',
                            '[(1, 2), (3, 8), (-2, 3)]')]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'FunctionPort'),
                ],
                add_port_specs=[
                    (0, 'input', 'i',
                     'org.vistrails.vistrails.basic:Integer'),
                    (0, 'input', 'j',
                     'org.vistrails.vistrails.basic:Integer'),
                    (0, 'output', 'o',
                     'org.vistrails.vistrails.basic:Integer'),
                ]))
        self.assertEqual(results, [[3, 11, 1]])


class TestUtils(unittest.TestCase):
    def test_filter(self):
        src = urllib2.quote('o = bool(i)')
        with intercept_result(Filter, 'Result') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', src)]),
                    ]),
                    ('Filter', 'org.vistrails.vistrails.control_flow', [
                        ('InputPort', [('List', "['i']")]),
                        ('OutputPort', [('String', 'o')]),
                        ('InputList', [('List',
                            "[0, 1, 2, 3, '', 'foo', True, False]")]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'FunctionPort'),
                ],
                add_port_specs=[
                    (0, 'input', 'i',
                     'org.vistrails.vistrails.basic:Module'),
                    (0, 'output', 'o',
                     'org.vistrails.vistrails.basic:Boolean'),
                ]))
        self.assertEqual(results, [[1, 2, 3, 'foo', True]])

    def test_sum(self):
        with intercept_result(Sum, 'Result') as results:
            self.assertFalse(execute([
                    ('Sum', 'org.vistrails.vistrails.control_flow', [
                        ('InputList', [('List', "[1, 2, 3, 8, 14.7]")]),
                    ]),
                ]))
        self.assertEqual(results, [28.7])

    def do_andor(self, l):
        with intercept_result(And, 'Result') as and_results:
            with intercept_result(Or, 'Result') as or_results:
                self.assertFalse(execute([
                        ('List', 'org.vistrails.vistrails.basic', [
                            ('value', [('List', str(l))]),
                        ]),
                        ('And', 'org.vistrails.vistrails.control_flow', []),
                        ('Or', 'org.vistrails.vistrails.control_flow', []),
                    ],
                    [
                        (0, 'value', 1, 'InputList'),
                        (0, 'value', 2, 'InputList'),
                    ]))
        self.assertEqual(len(and_results), 1)
        self.assertEqual(len(or_results), 1)
        return and_results[0], or_results[0]

    def test_andor(self):
        self.assertEqual(self.do_andor([False, False]), (False, False))
        self.assertEqual(self.do_andor([True, False]), (False, True))
        self.assertEqual(self.do_andor([True, True]), (True, True))
        self.assertEqual(self.do_andor([False, True]), (False, True))

        # This is kind of random
        self.assertEqual(self.do_andor([]), (True, False))
