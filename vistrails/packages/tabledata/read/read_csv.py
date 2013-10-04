import csv
from itertools import izip
import numpy

from vistrails.core.modules.vistrails_module import ModuleError
from ..common import Table


def count_lines(fp):
    lines = 0
    for line in fp:
        lines += 1
    return lines


class CSVFile(Table):
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('delimiter', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('self', '(org.vistrails.vistrails.tabledata:read|CSVFile)')]

    _STANDARD_DELIMITERS = [';', ',', '\t', '|']

    def __init__(self):
        Table.__init__(self)
        self._rows = None

    @staticmethod
    def read_file(filename, delimiter=None, header_present=True):
        try:
            with open(filename, 'rb') as fp:
                first_line = fp.readline()
            if delimiter is None:
                counts = [first_line.count(d)
                          for d in CSVFile._STANDARD_DELIMITERS]
                read_delimiter, count = max(
                        izip(CSVFile._STANDARD_DELIMITERS, counts),
                        key=lambda (delim, count): count)
                if count == 0:
                    raise ModuleError(self,
                                      "Couldn't guess the field delimiter")
                else:
                    delimiter = read_delimiter
            else:
                count = first_line.count(delimiter)

            column_count = count + 1

            if header_present:
                column_names = [
                        name.strip()
                        for name in first_line.split(delimiter)]
            else:
                column_names = None
        except IOError:
            raise ModuleError(self, "File does not exist")

        return column_count, column_names, delimiter

    def compute(self):
        csv_file = self.getInputFromPort('file').name
        self.header_present = self.getInputFromPort('header_present',
                                                    allowDefault=True)
        if self.hasInputFromPort('delimiter'):
            self.delimiter = self.getInputFromPort('delimiter')
        else:
            self.delimiter = None

        self.filename = csv_file

        self.columns, self.names, self.delimiter = \
                self.read_file(csv_file, self.delimiter, self.header_present)

        self.column_cache = {}

        self.setResult('column_count', self.columns)
        self.setResult('column_names', self.names)

    def get_column(self, index, numeric=False):
        if index in self.column_cache:
            return self.column_cache[index]

        if numeric:
            result = numpy.loadtxt(
                    self.filename,
                    dtype=numpy.float32,
                    delimiter=self.delimiter,
                    skiprows=1 if self.header_present else 0,
                    usecols=[index])
        else:
            with open(self.filename, 'rb') as fp:
                if self.header_present:
                    fp.readline()
                reader = csv.reader(
                        fp,
                        delimiter=self.delimiter)
                result = [row[index] for row in reader]

        self.column_cache[index] = result
        return result

    @property
    def rows(self):
        if self._rows is not None:
            return self._rows
        with open(self.filename, 'rb') as fp:
            self._rows = count_lines(fp)
        if self.header_present:
            self._rows -= 1
        return self._rows


_modules = [CSVFile]


###############################################################################

from StringIO import StringIO
import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier
from ..common import ExtractColumn


class CSVTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls._test_dir = os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'test_files')

    def test_csv_numeric(self):
        """Uses CSVFile and ExtractColumn to load a numeric array.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            with intercept_result(CSVFile, 'column_count') as columns:
                self.assertFalse(execute([
                        ('read|CSVFile', identifier, [
                            ('file', [('File', self._test_dir + '/test.csv')]),
                        ]),
                        ('ExtractColumn', identifier, [
                            ('column_index', [('Integer', '1')]),
                            ('column_name', [('String', 'col 2')]),
                            ('numeric', [('Boolean', 'True')]),
                        ]),
                        ('PythonSource', 'org.vistrails.vistrails.basic', [
                            ('source', [('String', '')]),
                        ]),
                    ],
                    [
                        (0, 'self', 1, 'table'),
                        (1, 'value', 2, 'l'),
                    ],
                    add_port_specs=[
                        (2, 'input', 'l',
                         'org.vistrails.vistrails.basic:List'),
                    ]))
                # Here we use a PythonSource just to check that a numpy array
                # can be passed on a List port
        self.assertEqual(columns, [3])
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [2.0, 3.0, 14.5])

    def test_csv_mismatch(self):
        """Uses CSVFile and ExtractColumn with mismatching columns.
        """
        self.assertTrue(execute([
                ('read|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, [
                    ('column_index', [('Integer', '0')]), # index is wrong
                    ('column_name', [('String', 'col 2')]),
                ]),
            ],
            [
                (0, 'self', 1, 'table'),
            ]))

    def test_csv_missing(self):
        """Uses CSVFile and ExtractColumn with a nonexisting column.
        """
        self.assertTrue(execute([
                ('read|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, [
                    ('column_name', [('String', 'col not here')]),
                ]),
            ],
            [
                (0, 'self', 1, 'table'),
            ]))

    def test_csv_nonnumeric(self):
        """Uses CSVFile and ExtractColumn to load strings.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('read|CSVFile', identifier, [
                        ('file', [('File', self._test_dir + '/test.csv')]),
                        ('header_present', [('Boolean', 'False')]),
                    ]),
                    ('ExtractColumn', identifier, [
                        ('column_index', [('Integer', '2')]),
                        ('numeric', [('Boolean', 'False')]),
                    ]),
                ],
                [
                    (0, 'self', 1, 'table'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0],
                         ['col moutarde', '4', 'not a number', '7'])


class TestCountlines(unittest.TestCase):
    def test_countlines(self):
        # Simple
        fp = StringIO("first\nsecond")
        self.assertEqual(count_lines(fp), 2)

        # With newline at EOF
        fp = StringIO("first\nsecond\n")
        self.assertEqual(count_lines(fp), 2)

        # Empty
        fp = StringIO("")
        self.assertEqual(count_lines(fp), 0)

        # Single newline
        fp = StringIO("\n")
        self.assertEqual(count_lines(fp), 1)
