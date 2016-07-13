###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from vistrails.core.modules.vistrails_module import ModuleError
from vistrails.core.modules.basic_modules import Module, Float, Integer
from vistrails.core.modules.config import ModuleSettings
import vtk
from .hasher import vtk_hasher
from .vtk_wrapper.wrapper import VTKInstanceWrapper

class vtkBaseInspector(Module):

    _settings = ModuleSettings(abstract=True)
    def auto_set_results(self, vtk_object):
        mid = self.moduleInfo['moduleId']
        for function in self.outputPorts.keys():
            if hasattr(vtk_object, function):
                retValues = getattr(vtk_object, function)()
                if issubclass(retValues.__class__, vtk.vtkObject):
                    output  = VTKInstanceWrapper(retValues, mid)
                    self.set_output(function, output)
                elif isinstance(retValues, (tuple, list)):
                    result = list(retValues)
                    for i in xrange(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            result[i] = VTKInstanceWrapper(result[i], mid)
                    self.set_output(function, type(retValues)(result))
                else:
                    self.set_output(function, retValues)

class vtkDataSetInspector(vtkBaseInspector):

    _settings = ModuleSettings(abstract=False, signature=vtk_hasher)
    _input_ports = [('SetInputConnection0', 'vtkAlgorithmOutput'),
                    ('SetInput', 'vtkDataSet'),
                    ]
    _output_ports = [('GetBounds', [Float] * 6),
                     ('GetScalarRange', [Float] * 2),
                     ('GetLength', [Float]),
                     ('GetCenter', [Float] * 3),
                     ('GetNumberOfPoints', [Integer]),
                     ('GetNumberOfCells', [Integer]),
                     ('GetPointData', 'vtkPointData'),
                     ('GetCellData', 'vtkCellData'),
                     ]

    def compute(self):
        port_object = None
        if self.has_input("SetInputConnection0"):
            ic = self.get_input("SetInputConnection0")
            if hasattr(ic, "vtkInstance"):
                ic = ic.vtkInstance
            producer = ic.GetProducer()
            try:
                port_object = producer.GetOutput()
            except AttributeError:
                raise ModuleError(self, 
                                  "expected a module that supports GetOutput")
        elif self.has_input("SetInput"):
            port_object = self.get_input("SetInput")
            if hasattr(port_object, "vtkInstance"):
                port_object = port_object.vtkInstance
        if port_object:
            self.auto_set_results(port_object)


class vtkDataSetAttributesInspector(vtkBaseInspector):
    
    _settings = ModuleSettings(abstract=False, signature=vtk_hasher)
    _input_ports = [('SetInput', 'vtkDataSetAttributes')]
    _output_ports = [('GetScalars', 'vtkDataArray'),
                     ('GetVectors', 'vtkDataArray'),
                     ('GetNormals', 'vtkDataArray'),
                     ('GetTCoords', 'vtkDataArray'),
                     ('GetTensors', 'vtkDataArray'),
                     ('GetGlobalIds', 'vtkDataArray'),
                     ('GetPedigreeIds', 'vtkAbstractArray'),
                     ]

    def compute(self):
        vtk_object = None
        if self.has_input("SetInput"):
            vtk_object = self.get_input("SetInput")
            if hasattr(vtk_object, "vtkInstance"):
                vtk_object = vtk_object.vtkInstance
        if vtk_object:
            self.auto_set_results(vtk_object)


class vtkDataArrayInspector(vtkBaseInspector):

    _settings = ModuleSettings(abstract=False, signature=vtk_hasher)
    _input_ports = [('SetInput', 'vtkDataArray')]
    _output_ports = [('GetMaxNorm', [Float]),
                    ('GetRange', [Float] * 2)]

    def compute(self):
        vtk_object = None
        if self.has_input("SetInput"):
            vtk_object = self.get_input("SetInput")
            if hasattr(vtk_object, "vtkInstance"):
                vtk_object = vtk_object.vtkInstance
        if vtk_object:
            self.auto_set_results(vtk_object)


class vtkPolyDataInspector(vtkDataSetInspector):

    _settings = ModuleSettings(abstract=False, signature=vtk_hasher)
    _input_ports = [('SetInputConnection0', 'vtkAlgorithmOutput'),
                    ('SetInput', 'vtkDataSet'),
                    ]
    _output_ports = [('GetVerts', 'vtkCellArray'),
                     ('GetLines', 'vtkCellArray'),
                     ('GetPolys', 'vtkCellArray'),
                     ('GetStrips', 'vtkCellArray'),
                     ('GetPoints', 'vtkPoints'),
                     ('GetNumberOfVerts', [Integer]),
                     ('GetNumberOfLines', [Integer]),
                     ('GetNumberOfPolys', [Integer]),
                     ('GetNumberOfStrips', [Integer]),
                     ]

    def compute(self):
        vtk_object = None
        if self.has_input("SetInputConnection0"):
            port_object = self.get_input("SetInputConnection0")
            if hasattr(port_object, "vtkInstance"):
                port_object = port_object.vtkInstance
            producer = port_object.GetProducer()
            try:
                vtk_object = producer.GetOutput()
            except AttributeError:
                raise ModuleError(self, 
                                  "expected a module that supports GetOutput")
        elif self.has_input("SetInput"):
            vtk_object = self.get_input("SetInput")
            if hasattr(vtk_object, "vtkInstance"):
                vtk_object = vtk_object.vtkInstance
        if vtk_object:
            self.auto_set_results(vtk_object)


_modules = [vtkBaseInspector,
            vtkDataSetInspector,
            vtkDataSetAttributesInspector,
            vtkDataArrayInspector,
            vtkPolyDataInspector]
