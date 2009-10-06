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
