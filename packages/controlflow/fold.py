from core.modules.vistrails_module import Module, ModuleConnector, InvalidOutput
from core.modules.basic_modules import Constant, NotCacheable
import copy

#################################################################################
## Fold Operator

class NewConstant(Constant):
    """A new Constant module to be used inside the Fold module."""
        
    def setValue(self, v):
        self.setResult("value", v)
        self.upToDate = True


class Fold(Module, NotCacheable):
    """The Fold Module is a high-order operator to implement some other structures,
    such as map, filter, sum, and so on.
    To use it, the user must inherit this class.
    Initially, the method setInitialValue() must be defined.
    Later, the method operation() must be defined."""

    def updateUpstream(self):
        """A modified version of the updateUpstream method."""

        ## Getting list of connectors
        connectors_InputList = self.inputPorts.get('InputList')

        ## Updating connectors from 'InputList'
        for connector in connectors_InputList:
            connector.obj.update()
            
        InputList = self.getInputFromPort('InputList')

        self.partialResult = None
        self.initialValue = None
        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None
        
        ## If there is some function to consider...
        if self.hasInputFromPort('FunctionPort'):

            ## Getting list of connectors
            connectors_FunctionPort = self.inputPorts.get('FunctionPort')
            connectors_InputPort = self.inputPorts.get('InputPort')
            connectors_OutputPort = self.inputPorts.get('OutputPort')

            ######################################################################
            ## updateFunctionPort()

            def updateFunctionPort():
                """Function to be used inside this updateUsptream method. It
                updates the modules connected to the FunctionPort port."""

                nameInput = self.getInputFromPort('InputPort')
                nameOutput = self.getInputFromPort('OutputPort')

                ## Function to be used inside in the next step
                def create_constant(value):
                    """Creates a Constant module."""

                    constant = NewConstant()
                    constant.setValue(value)
                    return constant

                ## Update everything for each value inside the list
                for i in xrange(len(InputList)):
                    self.element = InputList[i]
                    for connector in connectors_FunctionPort:
                        if not self.upToDate:
                            connector.obj.upToDate = False
                            ## Setting the value InputList[i] in the input port
                            if len(nameInput)==1:
                                ## Cleaning the previous connector...
                                if nameInput[0] in connector.obj.inputPorts:
                                    del connector.obj.inputPorts[nameInput[0]]
                                new_connector = ModuleConnector(create_constant(\
                                    self.element),'value')
                                connector.obj.set_input_port(nameInput[0],new_connector)
                            else:
                                if len(nameInput)!=len(InputList[i]):
                                    raise ModuleError(self,'The number of input values and input ports are not the same.')
                                for j in xrange(len(nameInput)):
                                    ## Cleaning the previous connector...
                                    if nameInput[j] in connector.obj.inputPorts:
                                        del connector.obj.inputPorts[nameInput[j]]
                                    new_connector = ModuleConnector(create_constant(\
                                        self.element[j]),'value')
                                    connector.obj.set_input_port(nameInput[j],new_connector)
                        connector.obj.update()
                        ## Getting the result from the output port
                        self.elementResult = connector.obj.get_output(nameOutput)
                    self.operation()

            ######################################################################
           
            ## Updating connectors from 'InputPort'
            for connector in connectors_InputPort:
                connector.obj.update()

            ## Updating connectors from 'OutputPort'
            for connector in connectors_OutputPort:
                connector.obj.update()

            ## Updating connectors from 'FunctionPort' --> This one must be the last
            for connector in connectors_FunctionPort:
                updateFunctionPort()
        
        else:
            for i in xrange(len(InputList)):
                self.element = InputList[i]
                self.operation()
                
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def compute(self):
        """The compute method for the Fold."""

        self.setResult('Result', self.partialResult)

    def setInitialValue(self):
        """This method defines the initial value of the Fold structure. It must
        be defined before the operation() method."""
        
        pass

    def operation(self):
        """This method defines the interaction between the current element of
        the list and the previous iterations' result."""

        pass
