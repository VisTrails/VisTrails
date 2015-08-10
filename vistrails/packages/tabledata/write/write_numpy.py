from __future__ import division

from vistrails.core.modules.vistrails_module import Module

from ..common import get_numpy
from ..read.read_numpy import NumPyArray


class WriteNumPy(Module):
    """Writes a list as a Numpy file.

    NumPy can use one of two schemes: either 'plain' binary arrays, i.e. just
    the binary representation of the data format (in this case you must specify
    the exact format to get the original data back), or the NPY format, i.e.
    .npy files that know what the actual structure of the array is.
    """
    _input_ports = [
            ('array', '(org.vistrails.vistrails.basic:List)'),
            ('datatype', '(org.vistrails.vistrails.basic:String)',
             {'entry_types': "['enum']",
              'values': "[%r]" % NumPyArray.FORMATS})]
    _output_ports = [('file', '(org.vistrails.vistrails.basic:File)')]

    def compute(self):
        numpy = get_numpy()

        array = self.get_input('array')
        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)
        dtype = NumPyArray.get_format(self.get_input('datatype'))

        if dtype is NumPyArray.NPY_FMT:
            fileobj = self.interpreter.filePool.create_file(suffix='.npy')
            fname = fileobj.name

            # Numpy's ".NPY" format
            numpy.save(fname, array)
        else:
            fileobj = self.interpreter.filePool.create_file(suffix='.dat')
            fname = fileobj.name

            # Numpy's plain binary format
            array.astype(dtype).tofile(fname)

        self.set_output('file', fileobj)


_modules = [WriteNumPy]


###############################################################################

import unittest


class WriteNumpyTestCase(unittest.TestCase):
    def test_raw_numpy(self):
        """Uses WriteNumPy to write an array in raw format.
        """
        import array
        from vistrails.tests.utils import execute, intercept_result
        from ..identifiers import identifier
        with intercept_result(WriteNumPy, 'file') as results:
            self.assertFalse(execute([
                    ('write|WriteNumPy', identifier, [
                        ('array', [('List', '[0, 1, 258, 6758]')]),
                        ('datatype', [('String', 'uint32')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        expected_bytes = [0, 0, 0, 0,
                          1, 0, 0, 0,
                          2, 1, 0, 0,
                          102, 26, 0, 0]
        with open(results[0].name, 'rb') as fp:
            self.assertEqual(fp.read(),
                             array.array('B', expected_bytes).tostring())

    def test_npy_numpy(self):
        """Uses WriteNumPy to write an array in .NPY format.
        """
        import numpy
        from vistrails.tests.utils import execute, intercept_result
        from ..identifiers import identifier
        with intercept_result(WriteNumPy, 'file') as results:
            self.assertFalse(execute([
                    ('write|WriteNumPy', identifier, [
                        ('array', [('List', '[0, 1, 258, 6758]')]),
                        ('datatype', [('String', 'npy')]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(list(numpy.load(results[0].name)), [0, 1, 258, 6758])

    def test_write_read(self):
        """Uses WriteNumPy and NumPyArray to write then read an array.
        """
        from vistrails.tests.utils import execute, intercept_result
        from ..identifiers import identifier
        for dtype in ('npy', 'uint32'):
            with intercept_result(NumPyArray, 'value') as results:
                self.assertFalse(execute([
                        ('write|WriteNumPy', identifier, [
                            ('array', [('List', '[0, 1, 258, 6758]')]),
                            ('datatype', [('String', dtype)]),
                        ]),
                        ('read|NumPyArray', identifier, [
                            ('datatype', [('String', dtype)]),
                        ]),
                    ], [
                        (0, 'file', 1, 'file'),
                    ]))
            self.assertEqual(len(results), 1)
            self.assertEqual(list(results[0]), [0, 1, 258, 6758])
