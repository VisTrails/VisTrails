from core.modules.vistrails_module import Module, InvalidOutput
from core.modules.basic_modules import NotCacheable
import copy

#################################################################################
## If Operator

class If(Module, NotCacheable):
    """The If Module alows the user to choose the part of the workflow to be
    executed through the use of a condition."""

    def updateUpstream(self):
        """A modified version of the updateUpstream method."""
      
        ## Updating connectors from 'Condition'
        connectors_Condition = self.inputPorts.get('Condition')
        for connector in connectors_Condition:
            connector.obj.update()

        ## Getting the list of connectors
        connectors_TruePort = self.inputPorts.get('TruePort')
        connectors_FalsePort = self.inputPorts.get('FalsePort')

        ## Getting the condition
        cond = self.getInputFromPort('Condition')

        if cond:
            ## Updating connectors from 'TruePort'
            for connector in connectors_TruePort:
                connector.obj.upToDate = False
                connector.obj.update()
                if self.hasInputFromPort('TrueOutputPorts'):
                    ## Getting the list of connectors
                    connectors_TrueOutputPorts = self.inputPorts.get('TrueOutputPorts')

                    ## Updating connectors from 'TrueOutputPorts'
                    for connector_ in connectors_TrueOutputPorts:
                        connector_.obj.update()

                    ## Getting the output ports
                    outputPorts = self.getInputFromPort('TrueOutputPorts')
                    
                    if len(outputPorts)==1:
                        self.setResult('Result',connector.obj.get_output(outputPorts[0]))
                    else:
                        result = []
                        for outputPort in outputPorts:
                            result.append(connector.obj.get_output(outputPort))
                        self.setResult('Result',result)
                
        else:
            ## Updating connectors from 'FalsePort'
            for connector in connectors_FalsePort:
                connector.obj.upToDate = False
                connector.obj.update()
                if self.hasInputFromPort('FalseOutputPorts'):
                    ## Getting the list of connectors
                    connectors_FalseOutputPorts = self.inputPorts.get('FalseOutputPorts')

                    ## Updating connectors from 'FalseOutputPorts'
                    for connector_ in connectors_FalseOutputPorts:
                        connector_.obj.update()

                    ## Getting the output ports
                    outputPorts = self.getInputFromPort('FalseOutputPorts')
                    
                    if len(outputPorts)==1:
                        self.setResult('Result',connector.obj.get_output(outputPorts[0]))
                    else:
                        result = []
                        for outputPort in outputPorts:
                            result.append(connector.obj.get_output(outputPort))
                        self.setResult('Result',result)
                        
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def compute(self):
        """ The compute method for the If module."""

        pass
