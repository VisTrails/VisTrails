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

##############################################################################
## Order Operator

class ExecuteInOrder(Module):
    """
    The Order Module alows the user to control which sink of a pair of
    sinks ought to executed first.  Connect the "self" port of each
    sink to the corresponding port.  Note that if you have more than
    two sinks, you can string them together by using a string of Order
    modules.
    """

    def updateUpstream(self):
        # don't do update until compute!
        pass

    def compute(self):
        # do updateUpstream as compute, but sort by key
        for _, connectorList in sorted(self.inputPorts.iteritems()):
            for connector in connectorList:
                connector.obj.update()
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)
