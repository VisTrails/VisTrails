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
from core import debug
from core.modules.vistrails_module import Module, ModuleError, ModuleErrors, \
    ModuleConnector, InvalidOutput
from core.modules.basic_modules import Boolean, String, Integer, Float, Tuple,\
     File, NotCacheable, Constant, List
from core.modules.module_registry import get_module_registry
from core.vistrail.port_spec import PortSpec
from core.utils import VistrailsInternalError

import copy
from itertools import izip

#################################################################################
## Fold Operator

class Fold(Module, NotCacheable):
    """The Fold Module is a high-order operator to implement some other structures,
    such as map, filter, sum, and so on.
    To use it, the user must inherit this class.
    Initially, the method setInitialValue() must be defined.
    Later, the method operation() must be defined."""
    
    def __init__(self):
        Module.__init__(self)
        self.is_fold_module = True

    def updateUpstream(self):
        """A modified version of the updateUpstream method."""

        # everything is the same except that we don't update anything
        # upstream of FunctionPort
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    connector.obj.updateUpstream()
            else:
                for connector in connector_list:
                    connector.obj.update()
        for port_name, connectorList in copy.copy(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput:
                        self.removeInputConnector(port_name, connector)

    def updateFunctionPort(self):
        """
        Function to be used inside the updateUsptream method of the Fold module. It
        updates the modules connected to the FunctionPort port.
        """
        nameInput = self.getInputFromPort('InputPort')
        nameOutput = self.getInputFromPort('OutputPort')
        rawInputList = self.getInputFromPort('InputList')

        # create inputList to always have iterable elements
        # to simplify code
        if len(nameInput) == 1:
            element_is_iter = False
        else:
            element_is_iter = True
        inputList = []
        for element in rawInputList:
            if not element_is_iter:
                inputList.append([element])
            else:
                inputList.append(element)

        ## Update everything for each value inside the list
        for i in xrange(len(inputList)): 
            element = inputList[i]
            if element_is_iter:
                self.element = element
            else:
                self.element = element[0]
            for connector in self.inputPorts.get('FunctionPort'):
                if not self.upToDate:
                    ##Type checking
                    if i==0:
                        self.typeChecking(connector.obj, nameInput, inputList)
                    
                    connector.obj.upToDate = False
                    connector.obj.already_computed = False
                    
                    ## Setting information for logging stuff
                    connector.obj.is_fold_operator = True
                    connector.obj.first_iteration = False
                    connector.obj.last_iteration = False
                    connector.obj.fold_iteration = i
                    if i==0:
                        connector.obj.first_iteration = True
                    if i==((len(inputList))-1):
                        connector.obj.last_iteration = True

                    self.setInputValues(connector.obj, nameInput, element)
                connector.obj.update()
                
                ## Getting the result from the output port
                if nameOutput not in connector.obj.outputPorts:
                    raise ModuleError(connector.obj,\
                                      'Invalid output port: %s'%nameOutput)
                self.elementResult = connector.obj.get_output(nameOutput)
            self.operation()

    def setInputValues(self, module, inputPorts, elementList):
        """
        Function used to set a value inside 'module', given the input port(s).
        """
        for element, inputPort in izip(elementList, inputPorts):
            ## Cleaning the previous connector...
            if inputPort in module.inputPorts:
                del module.inputPorts[inputPort]
            new_connector = ModuleConnector(create_constant(element), 'value')
            module.set_input_port(inputPort, new_connector)
            
    def typeChecking(self, module, inputPorts, inputList):
        """
        Function used to check if the types of the input list element and of the
        inputPort of 'module' match.
        """
        for elementList in inputList:
            if len(elementList) != len(inputPorts):
                raise ModuleError(self,
                                  'The number of input values and input ports '
                                  'are not the same.')
            for element, inputPort in izip(elementList, inputPorts):
                p_modules = module.moduleInfo['pipeline'].modules
                p_module = p_modules[module.moduleInfo['moduleId']]
                port_spec = p_module.get_port_spec(inputPort, 'input')
                v_module = create_module(element, port_spec.signature)
                if v_module is not None:
                    if not self.compare(port_spec, v_module, inputPort):
                        raise ModuleError(self,
                                          'The type of a list element does '
                                          'not match with the type of the '
                                          'port %s.' % inputPort)

                    del v_module
                else:
                    break

    def createSignature(self, v_module):
        """
    `   Function used to create a signature, given v_module, for a port spec.
        """
        if type(v_module)==tuple:
            v_module_class = []
            for module_ in v_module:
                v_module_class.append(self.createSignature(module_))
            return v_module_class
        else:
            return v_module.__class__

    def compare(self, port_spec, v_module, port):
        """
        Function used to compare two port specs.
        """
        port_spec1 = port_spec

        reg = get_module_registry()

        v_module = self.createSignature(v_module)
        port_spec2 = PortSpec(**{'signature': v_module})
        matched = reg.are_specs_matched(port_spec1, port_spec2)
                
        return matched
        
    def compute(self):
        """The compute method for the Fold."""

        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None
        if self.hasInputFromPort('FunctionPort'):
            self.updateFunctionPort()
        else:
            for element in self.getInputFromPort('InputList'):
                self.element = element
                self.operation()

        self.setResult('Result', self.partialResult)

    def setInitialValue(self):
        """This method defines the initial value of the Fold structure. It must
        be defined before the operation() method."""
        
        pass

    def operation(self):
        """This method defines the interaction between the current element of
        the list and the previous iterations' result."""

        pass

#################################################################################

class NewConstant(Constant):
    """
    A new Constant module to be used inside the Fold module.
    """
    def setValue(self, v):
        self.setResult("value", v)
        self.upToDate = True

def create_constant(value):
    """
    Creates a NewConstant module, to be used for the ModuleConnector.
    """
    constant = NewConstant()
    constant.setValue(value)
    return constant

def create_module(value, signature):
    """
    Creates a module for value, in order to do the type checking.
    """    
    if type(value)==bool:
        v_module = Boolean()
        return v_module
    elif type(value)==str:
        v_module = String()
        return v_module
    elif type(value)==int:
        if type(signature)==list:
            signature = signature[0]
        if signature[0]==Float().__class__:
            v_module = Float()
        else:
            v_module = Integer()
        return v_module
    elif type(value)==float:
        v_module = Float()
        return v_module
    elif type(value)==list:
        v_module = List()
        return v_module
    elif type(value)==file:
        v_module = File()
        return v_module
    elif type(value)==tuple:
        v_modules = ()
        for element in xrange(len(value)):
            v_modules += (create_module(value[element], signature[element]),)
        return v_modules
    else:
        debug.warning("Could not identify the type of the list element.")
        debug.warning("Type checking is not going to be done inside Fold module.")
        return None

