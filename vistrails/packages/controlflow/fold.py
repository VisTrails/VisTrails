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
from __future__ import division

import copy

from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    InvalidOutput, ModuleSuspended, ModuleWasSuspended

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

        for element in self.get_input('InputList'):
            self.element = element
            self.operation()

        self.set_output('Result', self.partialResult)

    def setInitialValue(self): # pragma: no cover
        """This method defines the initial value of the Fold structure. It must
        be defined before the operation() method."""

        pass

    def operation(self): # pragma: no cover
        """This method defines the interaction between the current element of
        the list and the previous iterations' result."""

        pass

###############################################################################

class FoldWithModule(Fold):
    """Implementation of Fold that uses another module as its operation.

    This can be used to create structures like Map or Filter, where another
    module will be called with each element of the list to retrieve something
    that this module will use.
    """

    def update_upstream(self):
        """A modified version of the update_upstream method."""

        # everything is the same except that we don't update the module on
        # FunctionPort
        suspended = []
        was_suspended = None
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    try:
                        connector.obj.update_upstream()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
            else:
                for connector in connector_list:
                    try:
                        connector.obj.update()
                    except ModuleWasSuspended, e:
                        was_suspended = e
                    except ModuleSuspended, e:
                        suspended.append(e)
        if len(suspended) == 1:
            raise suspended[0]
        elif suspended:
            raise ModuleSuspended(
                    self,
                    "multiple suspended upstream modules",
                    children=suspended)
        elif was_suspended is not None:
            raise was_suspended
        for port_name, connectorList in list(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput: # pragma: no cover
                        self.remove_input_connector(port_name, connector)

    def updateFunctionPort(self):
        """
        Function to be used inside the updateUsptream method of the
        FoldWithModule module. It updates the modules connected to the
        FunctionPort port.
        """
        nameInput = self.get_input('InputPort')
        nameOutput = self.get_input('OutputPort')
        rawInputList = self.get_input('InputList')

        # Create inputList to always have iterable elements
        # to simplify code
        if len(nameInput) == 1:
            element_is_iter = False
            inputList = [[element] for element in rawInputList]
        else:
            element_is_iter = True
            inputList = rawInputList
        suspended = []
        loop = self.logging.begin_loop_execution(self, len(inputList))
        ## Update everything for each value inside the list
        for i, element in enumerate(inputList):
            self.logging.update_progress(self, float(i)/len(inputList))
            if element_is_iter:
                self.element = element
            else:
                self.element = element[0]
            do_operation = True
            for connector in self.inputPorts.get('FunctionPort'):
                module = copy.copy(connector.obj)

                if not self.upToDate: # pragma: no branch
                    ## Type checking
                    if i == 0:
                        self.typeChecking(module, nameInput, inputList)

                    module.upToDate = False
                    module.computed = False

                    self.setInputValues(module, nameInput, element, i)

                loop.begin_iteration(module, i)

                try:
                    module.update()
                except ModuleSuspended, e:
                    suspended.append(e)
                    do_operation = False
                    loop.end_iteration(module)
                    continue

                loop.end_iteration(module)

                ## Getting the result from the output port
                if nameOutput not in module.outputPorts:
                    raise ModuleError(module,
                                      'Invalid output port: %s' % nameOutput)
                self.elementResult = module.get_output(nameOutput)
            if do_operation:
                self.operation()

            self.logging.update_progress(self, i * 1.0 / len(inputList))

        if suspended:
            raise ModuleSuspended(
                    self,
                    "function module suspended in %d/%d iterations" % (
                            len(suspended), len(inputList)),
                    children=suspended)
        loop.end_loop_execution()

    def compute(self):
        """The compute method for the Fold."""

        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None

        self.updateFunctionPort()

        self.set_output('Result', self.partialResult)
