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
################################################################################
# This describes basic modules used by other VTK module
################################################################################
import vtk
from core.modules.module_registry import registry
from core.modules.vistrails_module import Module, ModuleError
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

        from init import get_method_signature, prune_signatures

        doc = ''
        try:
            doc = self.provide_output_port_documentation(function)
        except:
            doc = ''

        setterSig = []
        if doc != '': setterSig = get_method_signature(None, doc, function)

        if len(setterSig) > 1:
            prune_signatures(self, function, setterSig)

        pp = []
        for j in xrange(len(setterSig)):
          setter = list(setterSig[j][1]) if setterSig[j][1] != None else None
          aux = []
          if setter != None and len(setter) == len(params) and pp == []:
              for i in xrange(len(setter)):
                  if setter[i].find('[') != -1:
                      del aux[:]
                      aux.append(params[i])
                  elif setter[i].find(']') != -1:
                      aux.append(params[i])
                      pp.append(aux)
                  else:
                      if len(aux) > 0: 
                          aux.append(params[i])
                      else:
                          pp.append(params[i])                
        if pp != []:
            params = pp 
            attr(*params)
        else: 
            attr(*params)
        # print "Called ",attr,function,params

    @classmethod
    def _provide_doc(cls, port_name):
        f = port_name.find('_')
        if f != -1:
            name = port_name[:f]
        else:
            name = port_name
        return getattr(cls.vtkClass, name).__doc__

    @classmethod
    def provide_input_port_documentation(cls, port_name):
        return cls._provide_doc(port_name)

    @classmethod
    def provide_output_port_documentation(cls, port_name):
        return cls._provide_doc(port_name)

    def compute(self):
        """ compute() -> None
        Actually perform real VTK task by directing all input/output ports
        to VTK function calls
        
        """

        def call_it(function, p):
            # Translate between VisTrails objects and VTK objects
            if p is None:
                # None indicates a call with no parameters
                params = []
            elif type(p) == tuple:
                # A tuple indicates a call with many parameters
                params = list(p)
            else:
                # Otherwise, it's a single parameter
                params = [p]

            # Unwraps VTK objects
            for i in xrange(len(params)):
                if hasattr(params[i], 'vtkInstance'):
                    params[i] = params[i].vtkInstance
            try:
                self.call_input_function(function, params)
            except Exception, e:
                msg = 'VTK Exception: '
                raise ModuleError(self, msg  + str(type(e)) + ': ' + str(e))

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
                
        #In the case of a vtkRenderer, 
        # we need to call the methods after the
        #input ports are set.
        if isinstance(self.vtkInstance, vtk.vtkRenderer):
            for value in methods:
                (_, port) = value
                conn = self.is_method.inverse[value]
                p = conn()
                call_it(port, p)

        # Call update if appropriate
        if hasattr(self.vtkInstance, 'Update'):
            def ProgressEvent(obj, event):
                self.logging.update_progress(self, obj.GetProgress())
            isAlgorithm = issubclass(self.vtkClass, vtk.vtkAlgorithm)
            if isAlgorithm:
                cbId = self.vtkInstance.AddObserver('ProgressEvent', ProgressEvent)
            self.vtkInstance.Update()
            if isAlgorithm:
                self.vtkInstance.RemoveObserver(cbId)

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
