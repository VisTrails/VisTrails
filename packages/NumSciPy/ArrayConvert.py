from core.modules.vistrails_module import Module, ModuleError
from Array import *

class ArrayConvertModule:
    my_namespace = 'numpy|array|convert'

class ArrayDumpToFile(ArrayConvertModule, Module):
    """ Pickle the input array and dump it to the specified file.  This
    array can then be read in via pickle.load or numpy.load """
    def compute(self):
        a = self.getInputFromPort("Array")
        fn = self.getInputFromPort("Filename")
        a.dump_to_file(fn)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ArrayToPickledFile", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))

class ArrayDumpToString(ArrayConvertModule, Module):
    """ Pickle the input array and dump it to a string.  This array
    can then be read in via pickle.loads or numpy.loads """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Output String", a.dump_to_string())

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ArrayToPickledString", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output String", (basic.String, 'Output String'))

class ArrayToFile(ArrayConvertModule, Module):
    """ Write the data to a file.  If a separator char is given, the file
    will be written in ASCII with the given char acting as a delimiter.  If
    no separator is given, the file is written in Binary.  The array
    is always written in row-major format regardless of the order of the
    input array. """
    def compute(self):
        a = self.getInputFromPort("Array")
        fn = self.getInputFromPort("Filename")
        sep = ""
        if self.hasInputFromPort("Separator"):
            sep = self.getInputFromPort("Separator")
        a.tofile(fn, sep)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Separator", (basic.String, 'Separator'), True)
        

class ArrayToString(ArrayConvertModule, Module):
    """ Convert the array to a Python string.  The output string will
    be represented in row-major form regardless of the ordering of the
    input array. """
    def compute(self):
        a = self.getInputFromPort("Array")
        self.setResult("Output String", a.tostring())

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output String", (basic.String, 'Output String'))
