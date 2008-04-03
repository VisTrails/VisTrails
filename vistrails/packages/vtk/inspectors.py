############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

##############################################################################
# Data inspectors for VTK

from core.modules.vistrails_module import ModuleError
from core.utils import VistrailsInternalError
from core.modules.basic_modules import Module, Float, Integer
from core.modules.module_registry import registry
import vtk
from hasher import vtk_hasher

class vtkBaseInspector(Module):

    @classmethod
    def register_self(cls, **kwargs):
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

class vtkDataSetInspector(vtkBaseInspector):

    def compute(self):
        ic = self.getInputFromPort("SetInputConnection")
        port_object = ic.vtkInstance
        ix = port_object.GetIndex()
        producer = port_object.GetProducer()
        try:
            vtk_object = producer.GetOutput()
        except AttributeError:
            raise ModuleError(self, "expected a module that supports GetOutput")

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

    input_ports = [('SetInputConnection',
                    [('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput')])]
    output_ports = [('GetBounds', [Float] * 6),
                    ('GetScalarRange', [Float] * 2),
                    ('GetLength', [Float]),
                    ('GetCenter', [Float] * 3),
                    ('GetNumberOfPoints', [Integer]),
                    ('GetNumberOfCells', [Integer]),
                    ]

def initialize():
    vtkBaseInspector.register_self(abstract=True, signatureCallable = vtk_hasher)
    vtkDataSetInspector.register_self(abstract=False, signatureCallable = vtk_hasher)
    
