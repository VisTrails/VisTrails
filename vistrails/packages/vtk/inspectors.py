###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

##############################################################################
# Data inspectors for VTK

from core.modules.vistrails_module import ModuleError
from core.utils import VistrailsInternalError
from core.modules.basic_modules import Module, Float, Integer
from core.modules.module_registry import get_module_registry
import vtk
from base_module import vtkBaseModule
from hasher import vtk_hasher

class vtkBaseInspector(Module):

    @classmethod
    def register_self(cls, **kwargs):
        registry = get_module_registry()
        def resolve_type(t):
            if type(t) == tuple:
                return registry.get_descriptor_by_name(*t).module
            elif type(t) == type:
                return t
            else:
                assert False, ("Unknown type " + str(type(t)))

        registry.add_module(cls, **kwargs)
        try:
            ips = cls.input_ports
        except AttributeError:
            pass
        else:
            for (port_name, types) in ips:
                registry.add_input_port(cls,
                                        port_name,
                                        list(resolve_type(t) for t in types))

        try:
            ops = cls.output_ports
        except AttributeError:
            pass
        else:
            for (port_name, types) in ops:
                registry.add_output_port(cls,
                                         port_name,
                                         list(resolve_type(t) for t in types))

    def auto_set_results(self, vtk_object):
        for function in self.outputPorts.keys():
            if hasattr(vtk_object, function):
                retValues = getattr(vtk_object, function)()
                if issubclass(retValues.__class__, vtk.vtkObject):
                    className = retValues.GetClassName()
                    output  = vtkBaseModule.wrapperModule(className, retValues)
                    self.setResult(function, output)
                elif type(retValues) in [tuple, list]:
                    result = list(retValues)
                    for i in xrange(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            className = result[i].GetClassName()
                            result[i] = vtkBaseModule.wrapperModule(className,
                                                                    result[i])
                    self.setResult(function, type(retValues)(result))
                else:
                    self.setResult(function, retValues)

class vtkDataSetInspector(vtkBaseInspector):

    def compute(self):
        vtk_object = None
        if self.hasInputFromPort("SetInputConnection0"):
            ic = self.getInputFromPort("SetInputConnection0")
            port_object = ic.vtkInstance
            ix = port_object.GetIndex()
            producer = port_object.GetProducer()
            try:
                vtk_object = producer.GetOutput()
            except AttributeError:
                raise ModuleError(self, 
                                  "expected a module that supports GetOutput")
        elif self.hasInputFromPort("SetInput"):
            port_object = self.getInputFromPort("SetInput")
            if hasattr(port_object, "vtkInstance"):
                vtk_object = port_object.vtkInstance
            else:
                raise ModuleError(self, "expected a vtk module")
        if vtk_object:
            self.auto_set_results(vtk_object)

    input_ports = [('SetInputConnection0',
                    [('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput')]),
                   ('SetInput',
                    [('edu.utah.sci.vistrails.vtk', 'vtkDataSet')]),
                   ]
    output_ports = [('GetBounds', [Float] * 6),
                    ('GetScalarRange', [Float] * 2),
                    ('GetLength', [Float]),
                    ('GetCenter', [Float] * 3),
                    ('GetNumberOfPoints', [Integer]),
                    ('GetNumberOfCells', [Integer]),
                    ('GetPointData', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkPointData')]),
                    ('GetCellData',
                     [('edu.utah.sci.vistrails.vtk', 'vtkCellData')]),
                    ]

class vtkDataSetAttributesInspector(vtkBaseInspector):
    
    def compute(self):
        vtk_object = None
        if self.hasInputFromPort("SetInput"):
            port_object = self.getInputFromPort("SetInput")
            if hasattr(port_object, "vtkInstance"):
                vtk_object = port_object.vtkInstance
            else:
                raise ModuleError(self, "expected a vtk module")
        if vtk_object:
            self.auto_set_results(vtk_object)

    input_ports = [('SetInput',
                    [('edu.utah.sci.vistrails.vtk', 'vtkDataSetAttributes')]),
                   ]
    output_ports = [('GetScalars', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetVectors', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetNormals', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetTCoords', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetTensors', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetGlobalIds', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')]),
                    ('GetPedigreeIds', 
                     [('edu.utah.sci.vistrails.vtk', 'vtkAbstractArray')]),
                    ]

class vtkDataArrayInspector(vtkBaseInspector):

   def compute(self):
        vtk_object = None
        if self.hasInputFromPort("SetInput"):
            port_object = self.getInputFromPort("SetInput")
            if hasattr(port_object, "vtkInstance"):
                vtk_object = port_object.vtkInstance
            else:
                raise ModuleError(self, "expected a vtk module")
        if vtk_object:
            self.auto_set_results(vtk_object)

   input_ports = [('SetInput',
                   [('edu.utah.sci.vistrails.vtk', 'vtkDataArray')])]
   output_ports = [('GetMaxNorm', [Float]),
                   ('GetRange', [Float] * 2)]
                   
class vtkPolyDataInspector(vtkDataSetInspector):

    def compute(self):
        vtk_object = None
        if self.hasInputFromPort("SetInputConnection0"):
            ic = self.getInputFromPort("SetInputConnection0")
            port_object = ic.vtkInstance
            ix = port_object.GetIndex()
            producer = port_object.GetProducer()
            try:
                vtk_object = producer.GetOutput()
            except AttributeError:
                raise ModuleError(self, 
                                  "expected a module that supports GetOutput")
        elif self.hasInputFromPort("SetInput"):
            port_object = self.getInputFromPort("SetInput")
            if hasattr(port_object, "vtkInstance"):
                vtk_object = port_object.vtkInstance
            else:
                raise ModuleError(self, "expected a vtk module")
        if vtk_object:
            self.auto_set_results(vtk_object)

    input_ports = [('SetInputConnection0',
                    [('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput')]),
                   ('SetInput',
                    [('edu.utah.sci.vistrails.vtk', 'vtkDataSet')]),
                   ]
    output_ports = [('GetVerts',
                     [('edu.utah.sci.vistrails.vtk', 'vtkCellArray')]),
                    ('GetLines',
                     [('edu.utah.sci.vistrails.vtk', 'vtkCellArray')]),
                    ('GetPolys',
                     [('edu.utah.sci.vistrails.vtk', 'vtkCellArray')]),
                    ('GetStrips',
                     [('edu.utah.sci.vistrails.vtk', 'vtkCellArray')]),
                    ('GetPoints',
                     [('edu.utah.sci.vistrails.vtk', 'vtkPoints')]),
                    ('GetNumberOfVerts', [Integer]),
                    ('GetNumberOfLines', [Integer]),
                    ('GetNumberOfPolys', [Integer]),
                    ('GetNumberOfStrips', [Integer]),
                    ]

def initialize():
    vtkBaseInspector.register_self(abstract=True, signatureCallable=vtk_hasher)
    vtkDataSetInspector.register_self(abstract=False, 
                                      signatureCallable=vtk_hasher)
    vtkDataSetAttributesInspector.register_self(abstract=False, 
                                                signatureCallable=vtk_hasher)
    vtkDataArrayInspector.register_self(abstract=False, 
                                        signatureCallable=vtk_hasher)
    vtkPolyDataInspector.register_self(abstract=False,
                                       signatureCallable=vtk_hasher)
    
