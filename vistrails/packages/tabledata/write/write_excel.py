from vistrails.core.bundles.pyimport import py_import
from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, ModuleError

from ..common import Table
from ..identifiers import identifier


def get_xlwt():
    try:
        return py_import('xlwt', {
                'pip': 'xlwt',
                'linux-debian': 'python-xlwt',
                'linux-ubuntu': 'python-xlwt',
                'linux-fedora': 'python-xlwt'})
    except ImportError: # pragma: no cover
        return None


class WriteExcelSpreadsheet(Module):
    """Writes a table to an Excel spreadsheet file.
    """
    _input_ports = [('table', Table)]
    _output_ports = [('file', '(org.vistrails.vistrails.basic:File)')]

    def compute(self):
        table = self.get_input('table')
        rows = table.rows

        xlwt = get_xlwt()
        if xlwt is None: # pragma: no cover
            raise ModuleError(self, "xlwt is not available")

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Sheet1')

        fileobj = self.interpreter.filePool.create_file(suffix='.xls')
        fname = fileobj.name

        for c in xrange(table.columns):
            column = table.get_column(c)
            for r, e in enumerate(column):
                sheet.write(r, c, e)
            if r != rows: # pragma: no cover
                debug.warning("WriteExcelSpreadsheet wrote %d lines instead "
                              "of expected %d" % (r, rows))

        workbook.save(fname)
        self.set_output('file', fileobj)


_modules = [WriteExcelSpreadsheet]


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_result


class ExcelWriteTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if get_xlwt() is None: # pragma: no cover
            raise unittest.SkipTest("xlwt not available")

    def test_xls_numeric(self):
        from ..common import ExtractColumn
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('BuildTable', identifier, [
                        ('a', [('List', '[1, 2, 3]')]),
                        ('b', [('List', '[4, 5, 6]')]),
                    ]),
                    ('write|WriteExcelSpreadsheet', identifier, []),
                    ('read|ExcelSpreadsheet', identifier, []),
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

    def test_xls_strings(self):
        from ..common import ExtractColumn
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('BuildTable', identifier, [
                        ('a', [('List', "['a', 2, 'c']")]),
                        ('b', [('List', "[4, 5, 6]")]),
                    ]),
                    ('write|WriteExcelSpreadsheet', identifier, []),
                    ('read|ExcelSpreadsheet', identifier, []),
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
        self.assertEqual(results[0], ['a', 2, 'c'])
