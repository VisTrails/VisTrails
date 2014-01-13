import numpy

from vistrails.core.modules.vistrails_module import Module

from ..read.read_numpy import NumPyArray


class WriteNumPy(Module):
    """Writes a list as a Numpy file.
    """
    _input_ports = [
            ('array', '(org.vistrails.vistrails.basic:List)'),
            ('datatype', '(org.vistrails.vistrails.basic:String)',
             {'entry_types': "['enum']",
              'values': "[%r]" % NumPyArray.FORMAT_MAP.keys()})]
    _output_ports = [('file', '(org.vistrails.vistrails.basic:File)')]

    def compute(self):
        array = self.get_input('array')
        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)
        dtype = NumPyArray.FORMAT_MAP[self.get_input('datatype')]

        fileobj = self.interpreter.filePool.create_file(suffix='.csv')
        fname = fileobj.name

        if dtype is NumPyArray.NPY_FMT:
            # Numpy's ".NPY" format
            numpy.save(fname, array)
        else:
            # Numpy's plain binary format
            array.astype(dtype).tofile(fname)

        self.set_output('file', fileobj)


_modules = [WriteNumPy]
