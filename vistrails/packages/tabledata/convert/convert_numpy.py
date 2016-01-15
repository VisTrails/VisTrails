###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

from vistrails.core.modules.vistrails_module import Module

from ..common import get_numpy


class Reshape(Module):
    """Reshapes an array using Numpy.
    """
    _input_ports = [
            ('array', '(org.vistrails.vistrails.basic:List)'),
            ('shape', '(org.vistrails.vistrails.basic:List)')]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        numpy = get_numpy()

        array = self.get_input('array')
        shape = self.get_input('shape')

        array = numpy.array(array).reshape(shape)
        self.set_output('value', array)


_modules = [Reshape]


###############################################################################

import unittest


class ReshapeTestCase(unittest.TestCase):
    def test_reshape(self):
        """Uses Reshape to reshape arrays and lists.
        """
        from vistrails.tests.utils import execute, intercept_result
        from ..identifiers import identifier
        with intercept_result(Reshape, 'value') as results:
            self.assertFalse(execute([
                    ('convert|Reshape', identifier, [
                        ('array', [('List', '[0, 1, 2, 3, 4, 5]')]),
                        ('shape', [('List', '[2, 3]')]),
                    ]),
                ]))
            self.assertFalse(execute([
                    ('convert|Reshape', identifier, [
                        ('array', [('List', '[[1, 2], [3, 4], [5, 6]]')]),
                        ('shape', [('List', '[6]')]),
                    ]),
                ]))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].shape, (2, 3))
        self.assertTrue((results[0] == [[0, 1, 2], [3, 4, 5]]).all())
        self.assertEqual(results[1].shape, (6,))
        self.assertTrue((results[1] == [1, 2, 3, 4, 5, 6]).all())

    def test_noreshape(self):
        """Uses Reshape with a wrong shape.
        """
        from vistrails.tests.utils import execute
        from ..identifiers import identifier
        error = execute([
                ('convert|Reshape', identifier, [
                    ('array', [('List', '[0, 1, 2, 3, 4, 5]')]),
                    ('shape', [('List', '[9]')]),
                ]),
            ])
        self.assertEqual(error.keys(), [0])
        self.assertIn("total size of new array must be unchanged",
                      error[0].args[0])
