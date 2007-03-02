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
################################################################################
# This describes basic modules used by other VTK module
################################################################################
import vtk
from core.modules.module_registry import registry
from core.modules.vistrails_module import Module

################################################################################

class vtkBaseModule(Module):
    """
    vtkBaseModule is the base class for all VTK modules in VisTrails, it acts
    as a wrapper to direct all input/output ports to appropriate VTK function
    calls
    
    """

    def __init__(self):
        """ vtkBaseModule() -> vtkBaseModule
        Instantiate an emptt VTK Module with real VTK instance
        
        """
        Module.__init__(self)
        self.vtkInstance = None

    def is_cacheable(self):
        # VTK objects are by default cacheable only if they're subclasses
        # of vtkAlgorithm
        return (issubclass(self.vtkClass, vtk.vtkAlgorithm)
                and (not issubclass(self.vtkClass, vtk.vtkAbstractMapper)))

    def compute(self):
        """ compute() -> None
        Actually perform real VTK task by directing all input/output ports
        to VTK function calls
        
        """

        # Always re-create vtkInstance module, no caching here
        if self.vtkInstance:
            del self.vtkInstance
        self.vtkInstance = self.vtkClass()

        # Make sure all input ports are called correctly
        for function in self.inputPorts.keys():
            paramList = self.forceGetInputListFromPort(function)
            if function[:18]=='SetInputConnection':
                paramList = zip([int(function[18:])]*len(paramList),
                                 paramList)
                function = 'SetInputConnection'
            if function=='AddInputConnection':
                desc = registry.getDescriptorByName('vtkAlgorithmOutput')
                for i in range(len(paramList)):
                    if type(paramList[i])==desc.module:
                        paramList[i] = (0, paramList[i])
            for p in paramList:
                if type(p)==tuple:
                    param = list(p)
                elif p==None: param = []
                else: param = [p]
                for i in range(len(param)):
                    if hasattr(param[i], 'vtkInstance'):
                        param[i] = param[i].vtkInstance
                getattr(self.vtkInstance, function)(*param)

        # Then update the output ports also with appropriate function calls
        for function in self.outputPorts.keys():
            if function[:13]=='GetOutputPort':
                i = int(function[13:])
                vtkOutput = self.vtkInstance.GetOutputPort(i)
                output = vtkBaseModule.wrapperModule('vtkAlgorithmOutput',
                                                     vtkOutput)
                self.setResult(function, output)
            elif hasattr(self.vtkInstance, function):
                retValues = getattr(self.vtkInstance, function)()
                if issubclass(retValues.__class__, vtk.vtkObject):
                    className = retValues.GetClassName()
                    output  = vtkBaseModule.wrapperModule(className, retValues)
                    self.setResult(function, output)                                   
                elif (type(retValues) in [tuple, list]):
                    result = list(retValues)
                    for i in range(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            className = result[i].GetClassName()
                            result[i] = vtkBaseModule.wrapperModule(className,
                                                                    result[i])
                    self.setResult(function, type(retValues)(result))
                else:
                    self.setResult(function, retValues)
            elif function!='self':
                print 'Unknown output port %s from' % function, self.vtkClass

    @staticmethod
    def wrapperModule(classname, instance):
        """ wrapperModule(classname: str, instance: vtk class) -> Module
        Create a wrapper module in VisTrails with a vtk instance
        
        """
        result = registry.getDescriptorByName(classname).module()
        result.vtkInstance = instance
        return result
