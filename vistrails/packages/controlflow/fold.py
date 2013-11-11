###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    ModuleConnector, InvalidOutput
from vistrails.core.modules.basic_modules import Boolean, String, Integer, \
    Float, NotCacheable, Constant, List
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.vistrail.port_spec import PortSpec

import copy
from itertools import izip

###############################################################################
## Fold Operator

class Fold(Module):
    """Fold is the base class for List-reducing modules.

    It can be used to easily implement a module that takes a List and
    aggregates its element one by one to get the final result, such as Sum.

    To use it, create a subclass and override the setInitialValue() and
    operation() methods.
    """

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        """The compute method for the Fold."""

        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None

        for element in self.getInputFromPort('InputList'):
            self.element = element
            self.operation()

        self.setResult('Result', self.partialResult)

    def setInitialValue(self): # pragma: no cover
        """This method defines the initial value of the Fold structure. It must
        be defined before the operation() method."""

        pass

    def operation(self): # pragma: no cover
        """This method defines the interaction between the current element of
        the list and the previous iterations' result."""

        pass

###############################################################################

class FoldWithModule(Fold, NotCacheable):
    """Implementation of Fold that uses another module as its operation.

    This can be used to create structures like Map or Filter, where another
    module will be called with each element of the list to retrieve something
    that this module will use.
    """

    def update(self):
        self.logging.begin_update(self)
        if len(self.inputPorts.get('FunctionPort', [])) != 1:
            raise ModuleError(self,
                              "%s module should have exactly one connection "
                              "on its FunctionPort" % self.__class__.__name__)
        connectors = []
        for port, connectorList in self.inputPorts.iteritems():
            if port != 'FunctionPort':
                connectors.extend(connectorList)
        self.run_upstream_module(
                self.other_ports_ready,
                *connectors,
                priority=self.UPDATE_UPSTREAM_PRIORITY)

    def other_ports_ready(self):
        for port_name, connectorList in list(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    mod, port = connector.obj, connector.port
                    if mod.get_output(port) is InvalidOutput: # pragma: no cover
                        self.removeInputConnector(port_name, connector)

        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None

        input_port = self.getInputFromPort('InputPort')
        input_list = self.getInputFromPort('InputList')

        if len(input_port) == 1:
            input_list = [[element] for element in input_list]
            self.input_is_single_element = True
        else:
            self.input_is_single_element = False

        self.logging.begin_compute(self)
        self.loop_logging = self.logging.begin_loop_execution(
                self,
                len(input_list))

        # Loop on the input to update the function modules
        self.modules_to_run = []
        for i, element in enumerate(input_list):
            connector, = self.inputPorts['FunctionPort']
            module = copy.copy(connector.obj)

            if not self.upToDate: # pragma: no partial
                # Type checking
                if i == 0:
                    self.typeChecking(module, input_port, input_list)

                module.upToDate = False
                module.computed = False
                self.setInputValues(module, input_port, element)

                self.loop_logging.begin_iteration(module, i)

            self.modules_to_run.append((module, element))

        if not self.upToDate:
            self.run_upstream_module(
                    self.functions_ready,
                    *(m for m, e in self.modules_to_run))
        else:
            self.done()

    def functions_ready(self):
        self.done()
        output_port = self.getInputFromPort('OutputPort')

        for module, element in self.modules_to_run:
            self.loop_logging.end_iteration(module)

            # Getting the result from the output port
            if output_port not in module.outputPorts:
                raise ModuleError(module,
                                  'Invalid output port: %s' % output_port)
            # If only one input port is set, self.input_is_single_element is
            # True and the operation() method receives this single element
            # directly as self.elementResult (not in a 1-element list)
            # If several input ports are set, self.input_is_single_element is
            # False and the operation() method receives a list of the arguments
            # as self.elementResult
            if self.input_is_single_element:
                self.element, = element
            else:
                self.element = element
            self.elementResult = module.get_output(output_port)
            self.operation()

        self.setResult('Result', self.partialResult)

        self.upToDate = True
        self.loop_logging.end_loop_execution()
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

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
                v_module = get_module(element, port_spec.signature)
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
        if isinstance(v_module, tuple):
            v_module_class = []
            for module_ in v_module:
                v_module_class.append(self.createSignature(module_))
            return v_module_class
        else:
            return v_module

    def compare(self, port_spec, v_module, port):
        """
        Function used to compare two port specs.
        """
        port_spec1 = port_spec

        reg = get_module_registry()

        v_module = self.createSignature(v_module)
        port_spec2 = PortSpec(**{'signature': v_module})
        matched = reg.are_specs_matched(port_spec2, port_spec1)

        return matched


###############################################################################

class NewConstant(Constant):
    """
    A new Constant module to be used inside the FoldWithModule module.
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

def get_module(value, signature):
    """
    Creates a module for value, in order to do the type checking.
    """
    if isinstance(value, Constant):
        return type(value)
    elif isinstance(value, bool):
        return Boolean
    elif isinstance(value, str):
        return String
    elif isinstance(value, int):
        return Integer
    elif isinstance(value, float):
        return Float
    elif isinstance(value, list):
        return List
    elif isinstance(value, tuple):
        v_modules = ()
        for element in xrange(len(value)):
            v_modules += (get_module(value[element], signature[element]),)
        return v_modules
    else: # pragma: no cover
        debug.warning("Could not identify the type of the list element.")
        debug.warning("Type checking is not going to be done inside"
                      "FoldWithModule module.")
        return None
