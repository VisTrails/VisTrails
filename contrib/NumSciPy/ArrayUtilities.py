import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from scipy import sparse
import vtk
from Array import *
from Matrix import *

class ArrayUtilModule(object):
    my_namespace = 'numpy|array|utilities'

class ArrayToVTKVectors(ArrayUtilModule, Module):
    def compute(self):
        v0 = self.forceGetInputFromPort("Array0")
        v1 = self.forceGetInputFromPort("Array1")
        v2 = self.forceGetInputFromPort("Array2")
        ds = self.get_input("VTK Data")

        v_name = self.forceGetInputFromPort("Vector Name")
        if v_name == None:
            v_name = 'vectors'

        vsize = 0
        if v0:
            vsize += 1
            v0 = v0.get_array().flatten()
        if v1:
            vsize += 1
            v1 = v1.get_array().flatten()
        if v2:
            vsize += 1
            v2 = v2.get_array().flatten()

        np = ds.vtkInstance.GetNumberOfPoints()
        pd = ds.vtkInstance.GetPointData()
        vtk_ar = vtk.vtkDoubleArray()
#        vtk_ar.SetNumberOfValues(np)
        vtk_ar.SetNumberOfComponents(3)
        for i in range(np):
            if vsize == 2:
                vtk_ar.InsertNextTuple3(v0[i], v1[i], 0.)
            elif vsize == 3:
                vtk_ar.InsertNextTuple3(v0[i], v1[i], v2[i])

        vtk_ar.SetName(v_name)
        ds.vtkInstance.GetPointData().AddArray(vtk_ar)
        ds.vtkInstance.GetPointData().SetVectors(vtk_ar)
#        ds.vtkInstance.GetPointData().SetActiveVectors(v_name)
        self.setResult("Output", ds)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "Array0", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "Array1", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "Array2", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "VTK Data", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkDataSet').module))
        reg.add_input_port(cls, "Vector Name", (basic.String, 'Scalar Name'), True)
        reg.add_output_port(cls, "Output", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkDataSet').module))

class ArrayToTimeVaryingVTKVectors(ArrayUtilModule, Module):
    def update_progress(self, cur, total):
        t = float(cur) / float(total)
        self.logging.update_progress(self, t)

    def compute(self):
        v0 = self.forceGetInputFromPort("Array0")
        v1 = self.forceGetInputFromPort("Array1")
        v2 = self.forceGetInputFromPort("Array2")
        ds = self.get_input("VTK Data")

        v_name = self.forceGetInputFromPort("Vector Name")
        if v_name == None:
            v_name = 'vectors'

        vsize = 0
        if v0:
            vsize += 1
        if v1:
            vsize += 1
        if v2:
            vsize += 1

        num_times = ds.vtkInstance.GetNumberOfTimeSteps()
        for i in range(num_times):
            self.update_progress(i, num_times)
            np = ds.vtkInstance.GetTimeStep(i).GetNumberOfPoints()
            pd = ds.vtkInstance.GetTimeStep(i).GetPointData()
            vtk_ar = vtk.vtkDoubleArray()
#        vtk_ar.SetNumberOfValues(np)
            vtk_ar.SetNumberOfComponents(3)
            arx = v0.get_array().squeeze()
            arx = arx[i,::].squeeze().flatten()
            ary = v1.get_array().squeeze()
            ary = ary[i,::].squeeze().flatten()
            if vsize == 3:
                arz = v2.get_array().squeeze()
                arz = arz[i,::].squeeze().flatten()
            for j in range(np):
                if vsize == 2:
                    vtk_ar.InsertNextTuple3(arx[j], ary[j], 0.)
                elif vsize == 3:
                    vtk_ar.InsertNextTuple3(arz[j], ary[j], arz[j])

            vtk_ar.SetName(v_name)
            ds.vtkInstance.GetTimeStep(i).GetPointData().AddArray(vtk_ar)
            ds.vtkInstance.GetTimeStep(i).GetPointData().SetVectors(vtk_ar)
#        ds.vtkInstance.GetPointData().SetActiveVectors(v_name)
        self.setResult("Output", ds)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "Array0", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "Array1", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "Array2", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "VTK Data", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkTemporalDataSet').module))
        reg.add_input_port(cls, "Vector Name", (basic.String, 'Scalar Name'), True)
        reg.add_output_port(cls, "Output", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkTemporalDataSet').module))
        

class ArrayToTimeVaryingVTKScalars(ArrayUtilModule, Module):
    def update_progress(self, cur, total):
        t = float(cur) / float(total)
        self.logging.update_progress(self, t)
        
    def compute(self):
        ds = self.get_input("VTK Data")
        ar = self.get_input("Scalars")
        v_name = self.forceGetInputFromPort("Array Name")
        if v_name == None:
            v_name = 'scalars'
        num_times = ds.vtkInstance.GetNumberOfTimeSteps()
        ar_ = ar.get_array()
        if ar_.shape[0] != num_times:
            raise ModuleError("Cannot process array with num timesteps = " +
                              str(ar_.shape[0]) +
                              " and vtkdata with " +
                              str(num_times) + " timesteps")
        
        for i in range(num_times):
            self.update_progress(i, num_times)
            s_ar = ar_[i,::].squeeze().flatten()
            vtk_ar = vtk.vtkDoubleArray()
            vtk_ar.SetNumberOfValues(s_ar.size)
            vtk_ar.SetName(v_name)
            for j in range(s_ar.size):
                vtk_ar.InsertNextValue(s_ar[j])
            
            ds.vtkInstance.GetTimeStep(i).GetPointData().AddArray(vtk_ar)
            ds.vtkInstance.GetTimeStep(i).GetPointData().SetScalars(vtk_ar)

        self.setResult("Output", ds)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "Scalars", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "VTK Data", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkTemporalDataSet').module))
        reg.add_input_port(cls, "Array Name", (basic.String, 'Scalar Name'), True)
        reg.add_output_port(cls, "Output", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkTemporalDataSet').module))

class ArrayToVTKScalars(ArrayUtilModule, Module):
    """ Take a scalar array and consider it as an array of scalars
    to assign to a VTK dataset.  The number of elements in the
    scalar array must be equivalent to the number of points in
    the VTK dataset.  Please note that this module adds a scalar
    array to the input dataset and can be considered a mutating filter
    because of this."""

    def compute(self):
        a = self.get_input("Array")
        ds = self.get_input("VTK Data")
        scalar_name = ''
        if self.hasInputFromPort("Scalar Name"):
            scalar_name = self.get_input("Scalar Name")
        else:
            scalar_name = 'scalars'
        
        s_ar = a.get_array().flatten()
        np = ds.vtkInstance.GetNumberOfPoints()
#        if s_ar.size != np:
#            raise ModuleError("Could not assign scalars to VTK dataset with different number of elements")

        pd = ds.vtkInstance.GetPointData()
        vtk_ar = vtk.vtkDoubleArray()
        vtk_ar.SetNumberOfValues(np)
        for i in xrange(np):
            vtk_ar.SetValue(i, s_ar[i])

        vtk_ar.SetName(scalar_name)
        ds.vtkInstance.GetPointData().AddArray(vtk_ar)
#        ds.vtkinstance.GetPointData().SetActiveScalars(scalar_name)
        ds.vtkInstance.GetPointData().SetScalars(vtk_ar)
        self.setResult("Output", ds)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "Array", (NDArray, 'Scalar Array'))
        reg.add_input_port(cls, "VTK Data", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkDataSet').module))
        reg.add_input_port(cls, "Scalar Name", (basic.String, 'Scalar Name'), True)
        reg.add_output_port(cls, "Output", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkDataSet').module))

class VTKDataSetToPointArray(ArrayUtilModule, Module):
    """
    Extract points and scalar values from a vtkDataSet.  The
    output will be of the form [[x,y,z,v]] with the v component
    optionally added if the IncludeScalars flag is set.
    """
    def compute(self):
        data = self.get_input("vtkDataSet").vtkInstance
        flag = self.forceGetInputFromPort("IncludeScalars")

        np = data.GetNumberOfPoints()
        ndim = 3
        if flag:
            ndim = 4

        out_ar = numpy.ones((np, ndim))
        for i in xrange(np):
            (out_ar[i,0], out_ar[i,1], out_ar[i,2]) = data.GetPoint(i)
            if flag:
                out_ar[i,3] = data.GetPointData().GetArray(0).GetTuple1(i)

        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "vtkDataSet", (reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkDataSet').module))
        reg.add_input_port(cls, "IncludeScalars", (basic.Boolean, 'Include Scalars in Output'), True)
        reg.add_output_port(cls, "Output", (NDArray, 'Output Array'))

        
            
        
