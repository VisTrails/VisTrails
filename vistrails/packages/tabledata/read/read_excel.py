try:
    import numpy
except ImportError:
    numpy = None

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.vistrails_module import ModuleError

from ..common import Table


def get_xlrd():
    try:
        return py_import('xlrd', {
                'pip': 'xlrd',
                'linux-debian': 'python-xlrd',
                'linux-ubuntu': 'python-xlrd',
                'linux-fedora': 'python-xlrd'})
    except ImportError: # pragma: no cover
        return None


class ExcelSpreadsheet(Table):
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
            ('self', '(org.vistrails.vistrails.tabledata:'
             'read|ExcelSpreadsheet)')]

    def compute(self):
        xlrd = get_xlrd()
        if xlrd is None: # pragma: no cover
            raise ModuleError(self, "xlrd is not available")

        workbook = self.getInputFromPort('file')
        workbook = xlrd.open_workbook(workbook.name)

        if self.hasInputFromPort('sheet_index'):
            sheet_index = self.getInputFromPort('sheet_index')
        if self.hasInputFromPort('sheet_name'):
            name = self.getInputFromPort('sheet_name')
            try:
                index = workbook.sheet_names().index(name)
            except:
                raise ModuleError(self, "Sheet name not found")
            if self.hasInputFromPort('sheet_index'):
                if sheet_index != index:
                    raise ModuleError(self,
                                      "Both sheet_name and sheet_index were "
                                      "specified, and they don't agree")
        elif self.hasInputFromPort('sheet_index'):
            index = sheet_index
        else:
            index = 0
        self.sheet = workbook.sheet_by_index(index)

        self.header_present = self.getInputFromPort('header_present')
        if self.header_present:
            self.names = [c.value for c in self.sheet.row(0)]
            self.setResult('column_names', self.names)
        else:
            self.names = None

        self.rows = self.sheet.nrows
        if self.header_present:
            self.rows -= 1

        self.columns = self.sheet.ncols
        self.setResult('column_count', self.columns)

        self.column_cache = {}

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        result = [c.value for c in self.sheet.col(index)]
        if self.header_present:
            result = result[1:]
        if numeric and numpy is not None:
            result = numpy.array(result, dtype=numpy.float32)
        elif numeric:
            result = [float(e) for e in result]

        self.column_cache[(index, numeric)] = result
        return result


_modules = [ExcelSpreadsheet]


###############################################################################

import itertools
import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier
from ..common import ExtractColumn


class ExcelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if get_xlrd() is None:
            raise unittest.SkipTest("xlrd not available")
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
                        (0, 'self', 1, 'table'),
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
                        (0, 'self', 1, 'table'),
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
                        (0, 'self', 1, 'table'),
                    ]))
        self.assertEqual(cols, [2])
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual_lists(list(results[0]), [1, -2.8, 3.4, 3.3])
