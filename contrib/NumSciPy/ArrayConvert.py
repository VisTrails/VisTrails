import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from scipy import sparse
from Array import *
from Matrix import *

class ArrayConvertModule(object):
    my_namespace = 'numpy|array|convert'

class ArrayDumpToFile(ArrayConvertModule, Module):
    """ Pickle the input array and dump it to the specified file.  This
    array can then be read in via pickle.load or numpy.load """
    def compute(self):
        a = self.get_input("Array")
        fn = self.get_input("Filename")
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
        a = self.get_input("Array")
        self.set_output("Output String", a.dump_to_string())

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
        a = self.get_input("Array")
        fn = self.get_input("Filename")
        sep = ""
        if self.has_input("Separator"):
            sep = self.get_input("Separator")
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
        a = self.get_input("Array")
        self.set_output("Output String", a.tostring())

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output String", (basic.String, 'Output String'))

class ArrayToMatrix(ArrayConvertModule, Module):
    """ Convert the input Numpy Array to a Scipy Matrix.  The input array
    must be no more than 2-dimensional """
    def compute(self):
        a = self.get_input("Array")
        try:
            mat = sparse.csc_matrix(a.get_array())
            out_mat = Matrix()
            out_mat.set_matrix(mat)
            self.set_output("Output Matrix", out_mat)
            
        except:
            raise ModuleError("Could not convert input array to matrix")

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array'))
        reg.add_output_port(cls, "Output Matrix", (Matrix, 'Output Matrix'))

class ArrayToVTKImageData(ArrayConvertModule, Module):
    """ Convert the array to a vtImageData dataset.  This works well for
    arrays up to (and including) rank 3.  Behavior is undefined for array of
    rank > 3."""
    def compute(self):
        import vtk
        
        a = self.get_input("Array")
        sh = a.get_shape()

        if len(sh) < 2:
            sh = tuple([sh[0], 1, 0])
        if len(sh) < 3:
            sh = tuple([sh[0], sh[1], 0])

        (num_sigs, num_times, num_freqs) = sh
        num_pts = a.get_num_elements()
        vtk_set = core.modules.module_registry.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkStructuredPoints').module()
        vtk_set.vtkInstance = vtk.vtkImageData()
        vtk_set.vtkInstance.SetDimensions(sh[0], sh[1], sh[2]+1)
        vtk_set.vtkInstance.SetScalarTypeToFloat()
        scalars = vtk.vtkFloatArray()

        ar = a.get_array()
        for ar_x in xrange(sh[0]):
            for ar_y in xrange(sh[1]):
                if sh[2] == 0:
                    val = ar[ar_x, ar_y]
                    vtk_set.vtkInstance.SetScalarComponentFromFloat(ar_x, ar_y, 0, 0, val)
                else:
                    
                    for ar_z in xrange(sh[2]):
                        val = ar[ar_x, ar_y, ar_z]
                        vtk_set.vtkInstance.SetScalarComponentFromFloat(ar_x, ar_y, ar_z, 0, val)

        if self.has_input("SpacingX"):
            x = self.get_input("SpacingX")
        else:
            x = 1.0
        if self.has_input("SpacingY"):
            y = self.get_input("SpacingY")
        else:
            y = 1.0
        if self.has_input("SpacingZ"):
            z = self.get_input("SpacingZ")
        else:
            z = 1.0
        vtk_set.vtkInstance.SetSpacing(x,y,z)

        self.set_output("vtkImageData", vtk_set)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Array", (NDArray, 'Input Array Volume'))
        reg.add_input_port(cls, "SpacingX", (basic.Float, 'X Spacing'))
        reg.add_input_port(cls, "SpacingY", (basic.Float, 'Y Spacing'))
        reg.add_input_port(cls, "SpacingZ", (basic.Float, 'Z Spacing'))
        reg.add_output_port(cls, "vtkImageData", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkImageData').module))
