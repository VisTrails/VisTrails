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

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.vistrails_module import ModuleError

from ..common import get_numpy, TableObject, Table


def get_xlrd():
    try:
        return py_import('xlrd', {
                             'pip': 'xlrd',
                             'linux-debian': 'python-xlrd',
                             'linux-ubuntu': 'python-xlrd',
                             'linux-fedora': 'python-xlrd'},
                         True)
    except ImportError: # pragma: no cover
        return None


class ExcelTable(TableObject):
    def __init__(self, sheet, header_present):
        self.sheet = sheet

        self.header_present = header_present
        if self.header_present:
            self.names = [c.value for c in self.sheet.row(0)]
        else:
            self.names = None

        self.rows = self.sheet.nrows
        if self.header_present:
            self.rows -= 1

        self.columns = self.sheet.ncols

        self.column_cache = {}

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        numpy = get_numpy(False)

        result = [c.value for c in self.sheet.col(index)]
        if self.header_present:
            result = result[1:]
        if numeric and numpy is not None:
            result = numpy.array(result, dtype=numpy.float32)
        elif numeric:
            result = [float(e) for e in result]

        self.column_cache[(index, numeric)] = result
        return result


class ExcelSpreadsheet(Table):
    """Reads a table from a Microsoft Excel file.

    This module uses xlrd from the python-excel.org project to read a XLS or
    XLSX file.
    """
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('sheet_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('sheet_index', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['False']"})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:String)'),
            ('value', Table)]

    def compute(self):
        xlrd = get_xlrd()
        if xlrd is None: # pragma: no cover
            raise ModuleError(self, "xlrd is not available")

        workbook = self.get_input('file')
        workbook = xlrd.open_workbook(workbook.name)

        if self.has_input('sheet_index'):
            sheet_index = self.get_input('sheet_index')
        if self.has_input('sheet_name'):
            name = self.get_input('sheet_name')
            try:
                index = workbook.sheet_names().index(name)
            except Exception:
                raise ModuleError(self, "Sheet name not found")
            if self.has_input('sheet_index'):
                if sheet_index != index:
                    raise ModuleError(self,
                                      "Both sheet_name and sheet_index were "
                                      "specified, and they don't agree")
        elif self.has_input('sheet_index'):
            index = sheet_index
        else:
            index = 0
        sheet = workbook.sheet_by_index(index)
        header_present = self.get_input('header_present')
        table = ExcelTable(sheet, header_present)
        self.set_output('value', table)

        if table.names is not None:
            self.set_output('column_names', table.names)
        self.set_output('column_count', table.columns)


_modules = [ExcelSpreadsheet]


###############################################################################

import itertools
import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier
from ..common import ExtractColumn

@unittest.skipIf(get_xlrd() is None, "xlrd not available")
class ExcelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls._test_dir = os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'test_files')

    def assertAlmostEqual_lists(self, a, b):
        for i, j in itertools.izip(a, b):
            self.assertAlmostEqual(i, j, places=5)

    def test_xls_numeric(self):
        """Uses ExcelSpreadsheet to load a numeric array.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            with intercept_result(ExcelSpreadsheet, 'column_count') as cols:
                self.assertFalse(execute([
                        ('read|ExcelSpreadsheet', identifier, [
                            ('file', [('File', self._test_dir + '/xl.xls')]),
                            ('sheet_index', [('Integer', '1')]),
                            ('sheet_name', [('String', 'Feuil2')]),
                            ('header_present', [('Boolean', 'False')])
                        ]),
                        ('ExtractColumn', identifier, [
                            ('column_index', [('Integer', '0')]),
                            ('numeric', [('Boolean', 'True')]),
                        ]),
                    ],
                    [
                        (0, 'value', 1, 'table'),
                    ]))
        self.assertEqual(cols, [1])
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual_lists(list(results[0]), [1, 2, 2, 3, -7.6])

    def test_xls_sheet_mismatch(self):
        """Uses ExcelSpreadsheet with mismatching sheets.
        """
        err = execute([
                ('read|ExcelSpreadsheet', identifier, [
                    ('file', [('File', self._test_dir + '/xl.xls')]),
                    ('sheet_index', [('Integer', '0')]),
                    ('sheet_name', [('String', 'Feuil2')]),
                ]),
            ])
        self.assertEqual(list(err.keys()), [0])
        self.assertEqual(
                err[0].msg,
                "Both sheet_name and sheet_index were specified, and they "
                "don't agree")

    def test_xls_sheetname_missing(self):
        """Uses ExcelSpreadsheet with a missing sheet.
        """
        err = execute([
                ('read|ExcelSpreadsheet', identifier, [
                    ('file', [('File', self._test_dir + '/xl.xls')]),
                    ('sheet_name', [('String', 'Sheet12')]),
                ]),
            ])
        self.assertEqual(list(err.keys()), [0])
        self.assertEqual(err[0].msg, "Sheet name not found")

    def test_xls_header_nonnumeric(self):
        """Uses ExcelSpreadsheet to load data.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            with intercept_result(ExcelSpreadsheet, 'column_count') as cols:
                self.assertFalse(execute([
                        ('read|ExcelSpreadsheet', identifier, [
                            ('file', [('File', self._test_dir + '/xl.xls')]),
                            ('sheet_name', [('String', 'Feuil1')]),
                            ('header_present', [('Boolean', 'True')])
                        ]),
                        ('ExtractColumn', identifier, [
                            ('column_index', [('Integer', '0')]),
                            ('column_name', [('String', 'data1')]),
                            ('numeric', [('Boolean', 'False')]),
                        ]),
                    ],
                    [
                        (0, 'value', 1, 'table'),
                    ]))
        self.assertEqual(cols, [2])
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), ['here', 'is', 'some', 'text'])

    def test_xls_header_numeric(self):
        """Uses ExcelSpreadsheet to load a numeric array.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            with intercept_result(ExcelSpreadsheet, 'column_count') as cols:
                self.assertFalse(execute([
                        ('read|ExcelSpreadsheet', identifier, [
                            ('file', [('File', self._test_dir + '/xl.xls')]),
                            # Will default to first sheet
                            ('header_present', [('Boolean', 'True')])
                        ]),
                        ('ExtractColumn', identifier, [
                            ('column_name', [('String', 'data2')]),
                            ('numeric', [('Boolean', 'True')]),
                        ]),
                    ],
                    [
                        (0, 'value', 1, 'table'),
                    ]))
        self.assertEqual(cols, [2])
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual_lists(list(results[0]), [1, -2.8, 3.4, 3.3])
