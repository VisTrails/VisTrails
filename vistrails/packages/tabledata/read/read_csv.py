import csv
from itertools import izip
import numpy

from vistrails.core.modules.vistrails_module import Module, ModuleError


class CSVFile(Module):
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('delimiter', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('value', '(org.vistrails.vistrails.tabledata:read|csv|CSVFile)')]

    _STANDARD_DELIMITERS = [';', ',', '\t', '|']

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

        self.column_count, self.column_names, self.delimiter = \
                self.read_file(csv_file, self.delimiter, self.header_present)
        self.setResult('column_count', self.column_count)
        self.setResult('column_names', self.column_names)
        self.setResult('value', self)


class ExtractColumn(Module):
    _input_ports = [
            ('csv', CSVFile),
            ('column_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('column_index', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('numeric', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        csv_file = self.getInputFromPort('csv')
        if self.hasInputFromPort('column_index'):
            column_index = self.getInputFromPort('column_index')
        if self.hasInputFromPort('column_name'):
            name = self.getInputFromPort('column_name')
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            try:
                index = csv_file.column_names.index(name)
            except ValueError:
                try:
                    name = name.strip()
                    index = csv_file.column_names.index(name)
                except:
                    raise ModuleError(self, "Column name was not found")
            if self.hasInputFromPort('column_index'):
                if column_index != index:
                    raise ModuleError(self,
                                      "Both column_name and column_index were "
                                      "specified, and they don't agree")
        elif self.hasInputFromPort('column_index'):
            index = column_index
        else:
            raise ModuleError(self,
                              "You must set one of column_name or "
                              "column_index")

        if self.getInputFromPort('numeric', allowDefault=True):
            result = numpy.loadtxt(
                    csv_file.filename,
                    dtype=numpy.float32,
                    delimiter=csv_file.delimiter,
                    skiprows=1 if csv_file.header_present else 0,
                    usecols=[index])
        else:
            with open(csv_file.filename, 'rb') as fp:
                if csv_file.header_present:
                    fp.readline()
                reader = csv.reader(
                        fp,
                        delimiter=csv_file.delimiter)
                result = [row[index] for row in reader]

        self.setResult('value', result)


_modules = {'csv': [CSVFile, ExtractColumn]}


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier


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
                        ('read|csv|CSVFile', identifier, [
                            ('file', [('File', self._test_dir + '/test.csv')]),
                        ]),
                        ('read|csv|ExtractColumn', identifier, [
                            ('column_index', [('Integer', '1')]),
                            ('column_name', [('String', 'col 2')]),
                        ]),
                    ],
                    [
                        (0, 'value', 1, 'csv'),
                    ]))
        self.assertEqual(columns, [3])
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [2.0, 3.0, 14.5])

    def test_csv_mismatch(self):
        """Uses CSVFile and ExtractColumn with mismatching columns.
        """
        self.assertTrue(execute([
                ('read|csv|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('read|csv|ExtractColumn', identifier, [
                    ('column_index', [('Integer', '0')]), # index is wrong
                    ('column_name', [('String', 'col 2')]),
                ]),
            ],
            [
                (0, 'value', 1, 'csv'),
            ]))

    def test_csv_missing(self):
        """Uses CSVFile and ExtractColumn with a nonexisting column.
        """
        self.assertTrue(execute([
                ('read|csv|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('read|csv|ExtractColumn', identifier, [
                    ('column_name', [('String', 'col not here')]),
                ]),
            ],
            [
                (0, 'value', 1, 'csv'),
            ]))

    def test_csv_nonnumeric(self):
        """Uses CSVFile and ExtractColumn to load strings.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('read|csv|CSVFile', identifier, [
                        ('file', [('File', self._test_dir + '/test.csv')]),
                        ('header_present', [('Boolean', 'False')]),
                    ]),
                    ('read|csv|ExtractColumn', identifier, [
                        ('column_index', [('Integer', '2')]),
                        ('numeric', [('Boolean', 'False')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'csv'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0],
                         ['col moutarde', '4', 'not a number', '7'])
