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
from core.modules.vistrails_module import Module, InvalidOutput
from core.modules.basic_modules import NotCacheable
from core.utils import VistrailsInternalError
import copy

#################################################################################
## If Operator

class If(Module, NotCacheable):
    """
    The If Module alows the user to choose the part of the workflow to be
    executed through the use of a condition.
    """

    def updateUpstream(self):
        """A modified version of the updateUpstream method."""
      
        # everything is the same except that we don't update anything
        # upstream of TruePort or FalsePort
        excluded_ports = set(['TruePort', 'FalsePort', 'TrueOutputPorts',
                              'FalseOutputPorts'])
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name not in excluded_ports:
                for connector in connector_list:
                    connector.obj.update()
        for port_name, connectorList in copy.copy(self.inputPorts.items()):
            if port_name not in excluded_ports:
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput:
                        self.removeInputConnector(port_name, connector)

    def compute(self):
        """ The compute method for the If module."""

        if not self.hasInputFromPort('Condition'):
            raise ModuleError(self, 'Must set condition')
        cond = self.getInputFromPort('Condition')

        if cond:
            port_name = 'TruePort'
            output_ports_name = 'TrueOutputPorts'
        else:
            port_name = 'FalsePort'
            output_ports_name = 'FalseOutputPorts'

        if self.hasInputFromPort(output_ports_name):
            for connector in self.inputPorts.get(output_ports_name):
                connector.obj.update()

        if not self.hasInputFromPort(port_name):
            raise ModuleError(self, 'Must set ' + port_name)

        for connector in self.inputPorts.get(port_name):
            connector.obj.upToDate = False
            connector.obj.update()

            if self.hasInputFromPort(output_ports_name):
                output_ports = self.getInputFromPort(output_ports_name)
                result = []
                for output_port in output_ports:
                    result.append(connector.obj.get_output(output_port))

                # FIXME can we just make this a list?
                if len(output_ports) == 1:
                    self.setResult('Result', result[0])
                else:
                    self.setResult('Result', result)
                                  
