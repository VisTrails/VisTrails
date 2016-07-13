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

import itertools

from vistrails.core.modules.vistrails_module import Module, ModuleError

#################################################################################
## Products

class ElementwiseProduct(Module):
    """This module does the product of two lists.

    If NumericalProduct is True, this will effectively compute the product of
    each element, eg:
        [1, 2, 3] x [3, -3, 1] = [3, -6, 3]
    Else, it will make tuples, eg:
        [1, 2, 3] x [3, -3, 1] = [(1, 3), (2, -3), (3, 1)]
    """

    def compute(self):
        list1 = self.get_input('List1')
        list2 = self.get_input('List2')
        if len(list1) != len(list2):
            raise ModuleError(self, "Both lists must have the same size.")

        numerical = self.get_input('NumericalProduct')
        if numerical:
            result = [a*b for a, b in itertools.izip(list1, list2)]
        else:
            result = zip(list1, list2)

        self.set_output('Result', result)


class Dot(Module):
    """This module produces a Dot product between two lists."""

    def compute(self):
        list1 = self.get_input("List1")
        list2 = self.get_input("List2")
        if len(list1) != len(list2):
            raise ModuleError(self, 'Both lists must have the same size.')

        result = sum(a*b for a, b in itertools.izip(list1, list2))

        self.set_output("Result", result)


class Cross(Module):
    """This module produces a Cross product between two 3-D vectors."""

    def compute(self):
        list1 = self.get_input("List1")
        list2 = self.get_input("List2")
        if not (len(list1) == len(list2) == 3):
            raise ModuleError(self, 'Both lists must have size 3.')

        x1, y1, z1 = list1
        x2, y2, z2 = list2

        result = [y1*z2 - y2*z1,
                  z1*x2 - z2*x1,
                  x1*y2 - x2*y1]

        self.set_output("Result", result)


class CartesianProduct(Module):
    """This module does the cartesian product of two lists.
    """

    def compute(self):
        list1 = self.get_input("List1")
        list2 = self.get_input("List2")
        result = []
        # If CombineTuple is not set or True, existing tuples will be
        # concatenated instead of put inside a new tuple, eg:
        #   with CombineTuple (default):
        #     [(1, 2)], [3, 4] -> [(1, 2, 3), (1, 2, 4)]
        #   without:
        #     [(1, 2)], [3, 4] -> [((1, 2), 3), ((1, 2), 4)]
        if not self.get_input('CombineTuple'):
            for i in list1:
                for j in list2:
                    tuple_ = (i, j)
                    result.append(tuple_)
        else:
            for i in list1:
                for j in list2:
                    if isinstance(i, tuple) and isinstance(j, tuple):
                        tuple_ = i + j
                        result.append(tuple_)
                    elif isinstance(i, tuple) and not isinstance(j, tuple):
                        tuple_ = i + (j,)
                        result.append(tuple_)
                    elif not isinstance(i, tuple) and isinstance(j, tuple):
                        tuple_ = (i,) + j
                        result.append(tuple_)
                    else:
                        tuple_ = (i, j)
                        result.append(tuple_)

        self.set_output("Result", result)


###############################################################################

import unittest

from vistrails.tests.utils import intercept_result, execute


class TestProducts(unittest.TestCase):
    def test_elementwise(self):
        with intercept_result(ElementwiseProduct, 'Result') as results:
            self.assertFalse(execute([
                    ('ElementwiseProduct', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[1, 2, 0]")]),
                        ('List2', [('List', "[4, -3, 7]")]),
                    ]),
                ]))
        self.assertEqual(results, [[4, -6, 0]])

    def test_elementwise_tuples(self):
        with intercept_result(ElementwiseProduct, 'Result') as results:
            self.assertFalse(execute([
                    ('ElementwiseProduct', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[1, 2, 0]")]),
                        ('List2', [('List', "[4, -3, 7]")]),
                        ('NumericalProduct', [('Boolean', "False")]),
                    ]),
                ]))
        self.assertEqual(results, [[(1, 4), (2, -3), (0, 7)]])

    def test_dot(self):
        with intercept_result(Dot, 'Result') as results:
            self.assertFalse(execute([
                    ('Dot', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[1, 2, 0]")]),
                        ('List2', [('List', "[4, -3, 7]")]),
                    ]),
                ]))
        self.assertEqual(results, [-2])

    def test_cross(self):
        with intercept_result(Cross, 'Result') as results:
            self.assertFalse(execute([
                    ('Cross', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[1, 2, 0]")]),
                        ('List2', [('List', "[4, -3, 7]")]),
                    ]),
                ]))
        # ( | 2 -3 |, | 0  7 |, | 1  4 | )
        #   | 0  7 |  | 1  4 |  | 2 -3 |
        self.assertEqual(results, [[14, -7, -11]])

    def test_cartesian_combine(self):
        with intercept_result(CartesianProduct, 'Result') as results:
            self.assertFalse(execute([
                    ('CartesianProduct', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[(1, 2)]")]),
                        ('List2', [('List', "[3, 4]")]),
                    ]),
                ]))
        self.assertEqual(results, [[(1, 2, 3), (1, 2, 4)]])

    def test_cartesian_nocombine(self):
        with intercept_result(CartesianProduct, 'Result') as results:
            self.assertFalse(execute([
                    ('CartesianProduct', 'org.vistrails.vistrails.control_flow', [
                        ('List1', [('List', "[(1, 2)]")]),
                        ('List2', [('List', "[3, 4]")]),
                        ('CombineTuple', [('Boolean', "False")]),
                    ]),
                ]))
        self.assertEqual(results, [[((1, 2), 3), ((1, 2), 4)]])
