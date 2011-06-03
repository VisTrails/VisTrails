############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
                                  
