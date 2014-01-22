from vistrails.core.modules.utils import make_modules_dict

try:
    # write_numpy requires numpy
    import numpy
except ImportError: # pragma: no cover
    numpy_modules = []
else:
    from write_numpy import _modules as numpy_modules

from write_csv import _modules as csv_modules
from write_excel import _modules as excel_modules


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
    @classmethod
    def setUpClass(cls):
        from .write_excel import get_xlwt
        if get_xlwt() is None: # pragma: no cover
            raise unittest.SkipTest("xlwt not available")

    WRITER_MODULE = 'write|WriteExcelSpreadsheet'
    READER_MODULE = 'read|ExcelSpreadsheet'


class CSVWriteTestCase(unittest.TestCase, BaseWriteTestCase):
    WRITER_MODULE = 'write|WriteCSV'
    READER_MODULE = 'read|CSVFile'
