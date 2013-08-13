import numpy

from vistrails.core.modules.vistrails_module import Module


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


_modules = {'numpy': [NumPyArray]}


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
                    ('read|numpy|NumPyArray', identifier, [
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
                    ('read|numpy|NumPyArray', identifier, [
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
                    ('read|numpy|NumPyArray', identifier, [
                        ('file', [('File', self._test_dir + '/random.npy')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [1.0, 7.0, 5.0, 3.0, 6.0, 1.0])
