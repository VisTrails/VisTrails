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


class NumPyArray(Module):
    """Reads a Numpy Array that has been written to a file.

    Declared as returning a List, but returns a Numpy array instead!

    NumPy can use one of two schemes: either 'plain' binary arrays, i.e. just
    the binary representation of the data format (in this case you must specify
    the exact format to get the original data back), or the NPY format, i.e.
    .npy files that know what the actual structure of the array is.

    If the array you are reading is not a simple one-dimensional array, you can
    use the shape port to indicate its expected structure.
    """
    NPY_FMT = object()

    FORMATS = [
        'int8',
        'uint8',
        'int16',
        'uint16',
        'int32',
        'uint32',
        'int64',
        'uint64',
        'float32',
        'float64',
        'complex64',
        'complex128',
    ]

    _format_map = None

    @classmethod
    def get_format(cls, format):
        if cls._format_map is None:
            numpy = get_numpy()
            cls._format_map = dict(
                       npy = cls.NPY_FMT,

                      int8 = numpy.int8,
                     uint8 = numpy.uint8,
                     int16 = numpy.int16,
                    uint16 = numpy.uint16,
                     int32 = numpy.int32,
                    uint32 = numpy.uint32,
                     int64 = numpy.int64,
                    uint64 = numpy.uint64,

                   float32 = numpy.float32,
                   float64 = numpy.float64,

                 complex64 = numpy.complex64,
                complex128 = numpy.complex128,
            )
        return cls._format_map[format]

    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('datatype', '(org.vistrails.vistrails.basic:String)',
             {'entry_types': "['enum']", 'values': "[%r]" % FORMATS}),
            ('shape', '(org.vistrails.vistrails.basic:List)')]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        numpy = get_numpy()

        filename = self.get_input('file').name
        if self.has_input('datatype'):
            dtype = NumPyArray.get_format(self.get_input('datatype'))
        else:
            if filename[-4:].lower() == '.npy':
                dtype = self.NPY_FMT
            else:
                dtype = numpy.float32
        if dtype is self.NPY_FMT:
            # Numpy's ".NPY" format
            # Written with: numpy.save('xxx.npy', array)
            array = numpy.load(filename)
        else:
            # Numpy's plain binary format
            # Written with: array.tofile('xxx.dat')
            array = numpy.fromfile(filename, dtype)
        if self.has_input('shape'):
            array.shape = tuple(self.get_input('shape'))
        self.set_output('value', array)


_modules = [NumPyArray]


###############################################################################

import unittest


class NumpyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls._test_dir = os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'test_files')

    def test_raw_numpy(self):
        """Uses NumPyArray to load an array in raw format.
        """
        from ..identifiers import identifier
        from vistrails.tests.utils import execute, intercept_result

        with intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(execute([
                    ('read|NumPyArray', identifier, [
                        ('datatype', [('String', 'float32')]),
                        ('shape', [('List', '[2, 3]')]),
                        ('file', [('File', self._test_dir + '/random.dat')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertTrue(
                (results[0] == [[1.0, 7.0, 5.0], [3.0, 6.0, 1.0]]).all())

    def test_npy_numpy(self):
        """Uses NumPyArray to load an array in .NPY format.
        """
        from ..identifiers import identifier
        from vistrails.tests.utils import execute, intercept_result

        with intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(execute([
                    ('read|NumPyArray', identifier, [
                        ('datatype', [('String', 'npy')]),
                        ('file', [('File', self._test_dir + '/random.npy')]),
                    ]),
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', '')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'l'),
                ],
                add_port_specs=[
                    (1, 'input', 'l',
                     'org.vistrails.vistrails.basic:List'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [1.0, 7.0, 5.0, 3.0, 6.0, 1.0])

    def test_npy_auto_numpy(self):
        """Uses NumPyArray to load an array in (autodetected) .NPY format.
        """
        from ..identifiers import identifier
        from vistrails.tests.utils import execute, intercept_result

        with intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(execute([
                    ('read|NumPyArray', identifier, [
                        ('file', [('File', self._test_dir + '/random.npy')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [1.0, 7.0, 5.0, 3.0, 6.0, 1.0])
