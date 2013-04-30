from __future__ import absolute_import # 'import numpy' is not ambiguous

import csv
from itertools import izip
import numpy

from vistrails.core.modules.vistrails_module import Module, ModuleError


class NumPyArray(Module):
    """
    A Numpy Array, that can be loaded from a file.

    Declared as returning a List, but returns a Numpy array instead!
    """
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('datatype', '(org.vistrails.vistrails.basic:String)'),
            ('shape', '(org.vistrails.vistrails.basic:List)')]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    NPY_FMT = object()

    FORMAT_MAP = dict(
               npy = NPY_FMT,

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

    def compute(self):
        filename = self.getInputFromPort('file').name
        if self.hasInputFromPort('datatype'):
            dtype = NumPyArray.FORMAT_MAP[self.getInputFromPort('datatype')]
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
        if self.hasInputFromPort('shape'):
            array.shape = tuple(self.getInputFromPort('shape'))
        self.setResult('value', array)


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
            ('value', '(org.vistrails.vistrails.matplotlib:CSVFile)')]

    _STANDARD_DELIMITERS = [';', ',', '\t', '|']

    def compute(self):
        csv_file = self.getInputFromPort('file').name
        self.header_present = self.getInputFromPort('header_present',
                                               allowDefault=True)
        if self.hasInputFromPort('delimiter'):
            self.delimiter = self.getInputFromPort('delimiter')
        else:
            self.delimiter = None

        self.filename = csv_file

        if self.header_present or self.delimiter is None:
            try:
                with open(csv_file, 'rb') as fp:
                    first_line = fp.readline()
                counts = [first_line.count(d)
                          for d in self._STANDARD_DELIMITERS]
                self.delimiter, count = max(
                        izip(self._STANDARD_DELIMITERS, counts),
                        key=lambda (delim, count): count)
                if count == 0:
                    raise ModuleError(self, "Couldn't guess the field delimiter")

                self.column_count = count - 1
                self.setResult('column_count', self.column_count)

                if self.header_present:
                    self.column_names = [
                            name.strip()
                            for name in first_line.split(self.delimiter)]
                    self.setResult('column_names', self.column_names)
            except IOError:
                raise ModuleError(self, "File does not exist")

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


_modules = [NumPyArray, CSVFile, ExtractColumn]


###############################################################################

import contextlib
import unittest


class NumpyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls._test_dir = os.path.join(
                os.path.dirname(__file__),
                'test_files')

    @staticmethod
    @contextlib.contextmanager
    def intercept_result(module, output_name):
        old_setResult = module.setResult
        results = []
        def new_setResult(self, name, value):
            if name == output_name:
                results.append(value)
            old_setResult(self, name, value)
        module.setResult = new_setResult
        try:
            yield results
        finally:
            module.setResult = old_setResult

    @staticmethod
    def execute(modules, connections=[]):
        from vistrails.core.db.locator import XMLFileLocator
        from vistrails.core.interpreter.default import get_default_interpreter
        from vistrails.core.utils import DummyView
        from vistrails.core.vistrail.connection import Connection
        from vistrails.core.vistrail.module import Module
        from vistrails.core.vistrail.module_function import ModuleFunction
        from vistrails.core.vistrail.module_param import ModuleParam
        from vistrails.core.vistrail.pipeline import Pipeline
        from vistrails.core.vistrail.port import Port

        pipeline = Pipeline()
        module_list = []
        for name, identifier, version, functions in modules:
            function_list = []
            for func_name, params in functions:
                param_list = []
                for param_type, param_val in params:
                    param_list.append(ModuleParam(type=param_type,
                                                  val=param_val))
                function_list.append(ModuleFunction(name=func_name,
                                                    parameters=param_list))
            module = Module(name=name,
                            package=identifier,
                            version=version,
                            id=len(module_list),
                            functions=function_list)
            pipeline.add_module(module)
            module_list.append(module)

        for i, (sid, sport, did, dport, sig) in enumerate(connections):
            pipeline.add_connection(Connection(
                    id=i,
                    ports=[
                        Port(id=i*2,
                             type='source',
                             moduleId=module_list[sid].id,
                             name=sport,
                             signature=sig),
                        Port(id=i*2+1,
                             type='destination',
                             moduleId=module_list[did].id,
                             name=dport,
                             signature=sig),
                    ]))

        interpreter = get_default_interpreter()
        result = interpreter.execute(
                pipeline,
                locator=XMLFileLocator('foo.xml'),
                current_version=1,
                view=DummyView())
        return result.errors

    def test_raw_numpy(self):
        """Uses NumPyArray to load an array in raw format.
        """
        from .identifiers import identifier, version

        with NumpyTestCase.intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(self.execute([
                    ('NumPyArray', identifier, version, [
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
        from .identifiers import identifier, version

        with NumpyTestCase.intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(self.execute([
                    ('NumPyArray', identifier, version, [
                        ('datatype', [('String', 'npy')]),
                        ('file', [('File', self._test_dir + '/random.npy')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [1.0, 7.0, 5.0, 3.0, 6.0, 1.0])

    def test_npy_auto_numpy(self):
        """Uses NumPyArray to load an array in (autodetected) .NPY format.
        """
        from .identifiers import identifier, version

        with NumpyTestCase.intercept_result(NumPyArray, 'value') as results:
            self.assertFalse(self.execute([
                    ('NumPyArray', identifier, version, [
                        ('file', [('File', self._test_dir + '/random.npy')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [1.0, 7.0, 5.0, 3.0, 6.0, 1.0])

    def test_csv_numeric(self):
        """Uses CSVFile and ExtractColumn to load a numeric array.
        """
        from .identifiers import identifier, version

        with NumpyTestCase.intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(self.execute([
                    ('CSVFile', identifier, version, [
                        ('file', [('File', self._test_dir + '/test.csv')]),
                    ]),
                    ('ExtractColumn', identifier, version, [
                        ('column_index', [('Integer', '1')]),
                        ('column_name', [('String', 'col 2')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'csv',
                     '(org.vistrails.vistrails.matplotlib:CSVFile)'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [2.0, 3.0, 14.5])

    def test_csv_mismatch(self):
        """Uses CSVFile and ExtractColumn with mismatching columns.
        """
        from .identifiers import identifier, version

        self.assertTrue(self.execute([
                ('CSVFile', identifier, version, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, version, [
                    ('column_index', [('Integer', '0')]), # index is wrong
                    ('column_name', [('String', 'col 2')]),
                ]),
            ],
            [
                (0, 'value', 1, 'csv',
                 '(org.vistrails.vistrails.matplotlib:CSVFile)'),
            ]))

    def test_csv_missing(self):
        """Uses CSVFile and ExtractColumn with a nonexisting column.
        """
        from .identifiers import identifier, version

        self.assertTrue(self.execute([
                ('CSVFile', identifier, version, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, version, [
                    ('column_name', [('String', 'col not here')]),
                ]),
            ],
            [
                (0, 'value', 1, 'csv',
                 '(org.vistrails.vistrails.matplotlib:CSVFile)'),
            ]))

    def test_csv_nonnumeric(self):
        """Uses CSVFile and ExtractColumn to load strings.
        """
        from .identifiers import identifier, version

        with NumpyTestCase.intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(self.execute([
                    ('CSVFile', identifier, version, [
                        ('file', [('File', self._test_dir + '/test.csv')]),
                        ('header_present', [('Boolean', 'False')]),
                    ]),
                    ('ExtractColumn', identifier, version, [
                        ('column_index', [('Integer', '2')]),
                        ('numeric', [('Boolean', 'False')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'csv',
                     '(org.vistrails.vistrails.matplotlib:CSVFile)'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0],
                         ['col moutarde', '4', 'not a number', '7'])
