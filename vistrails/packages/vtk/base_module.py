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
from itertools import izip

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

    def call_input_function(self, function, params):
        """self.call_input_function(function, params) -> None
        Calls the input function on the vtkInstance, or a special
        input function if one exists in the class."""
        if hasattr(self, '_special_input_function_' + function):
            attr = getattr(self, '_special_input_function_' + function)
        else:
            try:
                attr = getattr(self.vtkInstance, function)
            except AttributeError:
                # Compensates for overload by exploiting the fact that
                # no VTK method has underscores.
                f = function.find('_')
                if f != -1:
                    function = function[:f]
                attr = getattr(self.vtkInstance, function)
        attr(*params)
        # print "Called ",attr,function,params

    def compute(self):
        """ compute() -> None
        Actually perform real VTK task by directing all input/output ports
        to VTK function calls
        
        """

        def call_it(function, p):
            if type(p) == tuple:
                param = list(p)
            elif p == None: param = []
            else: param = [p]
            for i in xrange(len(param)):
                if hasattr(param[i], 'vtkInstance'):
                    param[i] = param[i].vtkInstance
            try:
                self.call_input_function(function, param)
            except e:
                print e

        # Always re-create vtkInstance module, no caching here
        if self.vtkInstance:
            del self.vtkInstance
        self.vtkInstance = self.vtkClass()

        # We need to call method ports before anything else, and in
        # the right order.

        # FIXME: This does not belong here, it belongs in the main class
        # No time for that now
        methods = self.is_method.values()
        methods.sort()
        for value in methods:
            (_, port) = value
            conn = self.is_method.inverse[value]
            p = conn()
            call_it(port, p)

        # Make sure all input ports are called correctly
        for (function, connector_list) in self.inputPorts.iteritems():
            paramList = self.forceGetInputListFromPort(function)
            if function[:18]=='SetInputConnection':
                paramList = zip([int(function[18:])]*len(paramList),
                                 paramList)
                function = 'SetInputConnection'
            if function=='AddInputConnection':
                desc = registry.get_descriptor_by_name(
                    'edu.utah.sci.vistrails.vtk',
                    'vtkAlgorithmOutput')
                for i in xrange(len(paramList)):
                    if type(paramList[i])==desc.module:
                        paramList[i] = (0, paramList[i])
            for p,connector in izip(paramList, connector_list):
                # Don't call method
                if connector in self.is_method:
                    continue
                call_it(function, p)

        # Call update if appropriate
        if hasattr(self.vtkInstance, 'Update'):
            # print "Called update on",self.vtkInstance
            self.vtkInstance.Update()

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
                    for i in xrange(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            className = result[i].GetClassName()
                            result[i] = vtkBaseModule.wrapperModule(className,
                                                                    result[i])
                    self.setResult(function, type(retValues)(result))
                else:
                    self.setResult(function, retValues)

    @staticmethod
    def wrapperModule(classname, instance):
        """ wrapperModule(classname: str, instance: vtk class) -> Module
        Create a wrapper module in VisTrails with a vtk instance
        
        """
        result = registry.get_descriptor_by_name(
            'edu.utah.sci.vistrails.vtk',
            classname).module()
        result.vtkInstance = instance
        return result
