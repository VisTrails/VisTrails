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

from vistrails.core.modules.utils import make_modules_dict

from .write_csv import _modules as csv_modules
from .write_excel import _modules as excel_modules
from .write_numpy import _modules as numpy_modules


_modules = make_modules_dict(numpy_modules, csv_modules, excel_modules,
                             namespace='write')


###############################################################################

import unittest


class BaseWriteTestCase(object):
    def test_numeric(self):
        from vistrails.tests.utils import execute, intercept_result
        from ..common import ExtractColumn
        from ..identifiers import identifier
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('BuildTable', identifier, [
                        ('a', [('List', '[1, 2, 3]')]),
                        ('b', [('List', '[4, 5, 6]')]),
                    ]),
                    (self.WRITER_MODULE, identifier, []),
                    (self.READER_MODULE, identifier, []),
                    ('ExtractColumn', identifier, [
                        ('column_index', [('Integer', '1')]),
                        ('numeric', [('Boolean', 'True')]),
                    ]),
                ], [
                    (0, 'value', 1, 'table'),
                    (1, 'file', 2, 'file'),
                    (2, 'value', 3, 'table'),
                ],
                add_port_specs=[
                    (0, 'input', 'a',
                     'org.vistrails.vistrails.basic:List'),
                    (0, 'input', 'b',
                     'org.vistrails.vistrails.basic:List'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [4, 5, 6])

    def test_strings(self):
        from vistrails.tests.utils import execute, intercept_result
        from ..common import ExtractColumn
        from ..identifiers import identifier
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('BuildTable', identifier, [
                        ('a', [('List', "['a', '2', 'c']")]),
                        ('b', [('List', "[4, 5, 6]")]),
                    ]),
                    (self.WRITER_MODULE, identifier, []),
                    (self.READER_MODULE, identifier, []),
                    ('ExtractColumn', identifier, [
                        ('column_index', [('Integer', '0')]),
                        ('numeric', [('Boolean', 'False')]),
                    ]),
                ], [
                    (0, 'value', 1, 'table'),
                    (1, 'file', 2, 'file'),
                    (2, 'value', 3, 'table'),
                ],
                add_port_specs=[
                    (0, 'input', 'a',
                     '(org.vistrails.vistrails.basic:List)'),
                    (0, 'input', 'b',
                     '(org.vistrails.vistrails.basic:List)'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ['a', '2', 'c'])


class ExcelWriteTestCase(unittest.TestCase, BaseWriteTestCase):
    WRITER_MODULE = 'write|WriteExcelSpreadsheet'
    READER_MODULE = 'read|ExcelSpreadsheet'

    @classmethod
    def setUpClass(cls):
        from .write_excel import get_xlwt

        if get_xlwt() is None:
            raise unittest.SkipTest("xlwt not available")


class CSVWriteTestCase(unittest.TestCase, BaseWriteTestCase):
    WRITER_MODULE = 'write|WriteCSV'
    READER_MODULE = 'read|CSVFile'
