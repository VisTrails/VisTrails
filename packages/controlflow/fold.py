from core.modules.vistrails_module import Module, ModuleError, ModuleConnector,\
     InvalidOutput
from core.modules.basic_modules import Boolean, String, Integer, Float, Tuple,\
     File, NotCacheable, Constant
from core.modules.module_registry import get_module_registry
from core.vistrail.port_spec import PortSpec
from core.utils import VistrailsInternalError
from list_module import ListOfElements
import copy


#################################################################################
## Fold Operator

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
        if connectors_InputList==None:
            raise VistrailsInternalError('Missing value from port InputList')

        ## Updating connectors from 'InputList'
        for connector in connectors_InputList:
            connector.obj.update()
            
        self.inputList = self.getInputFromPort('InputList')
        
        self.partialResult = None
        self.initialValue = None
        
        self.setInitialValue()
        self.partialResult = self.initialValue
        self.elementResult = None
        
        ## If there is some function to consider...
        if self.hasInputFromPort('FunctionPort'):

            ## Getting list of connectors
            self.connectors_FunctionPort = self.inputPorts.get('FunctionPort')
            connectors_InputPort = self.inputPorts.get('InputPort')
            connectors_OutputPort = self.inputPorts.get('OutputPort')

            if self.connectors_FunctionPort==None:
                raise VistrailsInternalError('Missing value from port FunctionPort')
            if connectors_InputPort==None:
                raise VistrailsInternalError('Missing value from port InputPort')
            if connectors_OutputPort==None:
                raise VistrailsInternalError('Missing value from port OutputPort')
           
            ## Updating connectors from 'InputPort'
            for connector in connectors_InputPort:
                connector.obj.update()

            ## Updating connectors from 'OutputPort'
            for connector in connectors_OutputPort:
                connector.obj.update()

            ## Updating connectors from 'FunctionPort' --> This one must be the last
            self.updateFunctionPort()
        
        else:
            for i in xrange(len(self.inputList)):
                ## Getting the value inside the list
                self.element = self.inputList[i]
                self.operation()
                
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def updateFunctionPort(self):
        """
        Function to be used inside the updateUsptream method of the Fold module. It
        updates the modules connected to the FunctionPort port.
        """
        nameInput = self.getInputFromPort('InputPort')
        nameOutput = self.getInputFromPort('OutputPort')

        ## Update everything for each value inside the list
        for i in xrange(len(self.inputList)):
            self.element = self.inputList[i]
            for connector in self.connectors_FunctionPort:
                if not self.upToDate:
                    ##Type checking
                    if i==0:
                        self.typeChecking(connector.obj, nameInput)
                    
                    connector.obj.upToDate = False
                    connector.obj.already_computed = False
                    
                    ## Setting information for logging stuff
                    connector.obj.first_iteration = False
                    if i==0:
                        connector.obj.is_fold_operator = True
                        connector.obj.first_iteration = True
                        connector.obj.last_iteration = False
                    if i==((len(self.inputList))-1):
                        connector.obj.last_iteration = True

                    self.setInputValues(connector.obj, nameInput)
                connector.obj.update()
                
                ## Getting the result from the output port
                if nameOutput not in connector.obj.outputPorts:
                    raise ModuleError(connector.obj,\
                                      'Invalid output port: %s'%nameOutput)
                self.elementResult = connector.obj.get_output(nameOutput)
            self.operation()

    def setInputValues(self, module, inputPorts):
        """
        Function used to set a value inside 'module', given the input port(s).
        """
        if len(inputPorts)==1:
            ## Cleaning the previous connector...
            if inputPorts[0] in module.inputPorts:
                del module.inputPorts[inputPorts[0]]
            new_connector = ModuleConnector(create_constant(self.element),\
                                            'value')
            module.set_input_port(inputPorts[0], new_connector)
        else:
            for j in xrange(len(inputPorts)):
                ## Cleaning the previous connector...
                if inputPorts[j] in module.inputPorts:
                    del module.inputPorts[inputPorts[j]]
                new_connector = ModuleConnector(create_constant(self.element[j]),\
                                                'value')
                module.set_input_port(inputPorts[j], new_connector)

    def typeChecking(self, module, inputPorts):
        """
        Function used to check if the types of the input list element and of the
        inputPort of 'module' match.
        """
        if len(inputPorts)==1:
            port_spec1 = module.moduleInfo['pipeline'].modules\
                         [module.moduleInfo['moduleId']].get_port_spec(inputPorts[0],\
                                                                       'input')
            for element in self.inputList:
                v_module = create_module(element, port_spec1.signature)
                if v_module!=None:
                    self.compare(port_spec1, v_module, inputPorts[0])
                    del v_module
                else:
                    break
            return
        else:
            for element in self.inputList:
                if len(inputPorts)!=len(element):
                    raise VistrailsInternalError\
                          ('The number of input values and input ports are' +
                           ' not the same.')
                for port in xrange(len(inputPorts)):
                    port_spec1 = module.moduleInfo['pipeline'].modules\
                                 [module.moduleInfo['moduleId']].get_port_spec\
                                 (inputPorts[port], 'input')
                    v_module = create_module(element[port], port_spec1.signature)
                    if v_module!=None:
                        self.compare(port_spec1, v_module, inputPorts[port])
                        del v_module
                    else:
                        break
            return

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
                
        if not matched:
            raise VistrailsInternalError\
                  ('The type of a list element does not match with the type' +
                   ' of the port %s.'%port)
            return
        
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
        v_module = ListOfElements()
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
        print "Could not identify the type of the list element."
        print "Type checking is not going to be done inside Fold module."
        return None
    
