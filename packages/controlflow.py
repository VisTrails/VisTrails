from core.modules.vistrails_module import *
from core.modules.module_registry import registry
from core.modules.basic_modules import Boolean, Constant, String, Variant,\
     NotCacheable, init_constant, new_constant
import copy


version="0.1"
name="Control Flow"
identifier="edu.utah.sci.vistrails.control_flow"


#################################################################################
## The List Module
## For instance, this module will be inside this package

def list_conv(l):
    if (l[0] != '[') and (l[-1] != ']'):
        raise ValueError('List from String in VisTrails should start with \
"[" and end with "]".')
    else:
        l = eval(l)
        return l

ListOfElements = new_constant('ListOfElements' , staticmethod(list_conv), [],\
                              staticmethod(lambda x: type(x) == list))

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


class Map(Fold):
    """A Map module, that just appends the results in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        self.partialResult.append(self.elementResult)


class Filter(Fold):
    """A Filter module, that returns in a list only the results that satisfy a
    condition."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        if type(self.elementResult)!=bool:
            raise ModuleError(self,'The function applied to the elements of the list must return a boolean result.')

        if self.elementResult:
            self.partialResult.append(self.element)


class AreaFilter(Fold):
    """A Filter module, to be used inside triangle_area.vt; it will discard the
    areas under the value 200000."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        area = self.elementResult
        
        if area>200000:
            self.partialResult.append(area)


class SimilarityFilter(Fold):
    """A Filter module, to be used inside DDBJ_webService.vt; it will discard the
    species with similarity score under 95.00."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        similarityScore = float(self.elementResult[1].split('\t')[1])

        if similarityScore>98.00:
            self.partialResult.append(self.elementResult)


##class Sum(Fold):
##    """A Sum module, that computes the sum of the elements in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 0
##        
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult += self.element
##
##        
##class And(Fold):
##    """An And module, that computes the And result among the elements
##    in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 1
##
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult = self.partialResult and self.element
##
##        
##class Or(Fold):
##    """An Or module, that computes the Or result among the elements
##    in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 0
##
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult = self.partialResult or self.element

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
                        print connector.obj.outputPorts
                        self.setResult('Result',connector.obj.get_output(outputPorts[0]))
                    else:
                        result = []
                        for outputPort in outputPorts:
                            result.append(connector.obj.get_output(outputPort))
                        self.setResult('Result',result)

    def compute(self):
        """ The compute method for the If module."""

        pass

#################################################################################
## Products
## For instance, these modules will be inside this package

class Dot(Module):
    """This module produces a Dot product between two input ports."""
    
    def compute(self):
        list1 = self.getInputFromPort("List_1")
	list2 = self.getInputFromPort("List_2")
	lenght1 = len(list1)
	lenght2 = len(list2)
	result = []
	if lenght1 != lenght2:
            raise ModuleError(self,'Both lists must have the same size.')
        if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort("CombineTuple")):
            for i in xrange(lenght1):
                tuple_ = (list1[i],list2[i])
                result.append(tuple_)
        else:
            for i in xrange(lenght1):
                if type(list1[i])==tuple and type(list2[i])==tuple:
                    tuple_ = list1[i]+list2[i]
                    result.append(tuple_)
                elif type(list1[i])==tuple and type(list2[i])!=tuple:
                    tuple_ = list1[i]+(list2[i],)
                    result.append(tuple_)
                elif type(list1[i])!=tuple and type(list2[i])==tuple:
                    tuple_ = (list1[i],)+list2[i]
                    result.append(tuple_)
                else:
                    tuple_ = (list1[i],list2[i])
                    result.append(tuple_)

        self.setResult("Result", result)


class Cross(Module):
    """This module produces a Cross product between two input ports."""
    
    def compute(self):
        list1 = self.getInputFromPort("List_1")
	list2 = self.getInputFromPort("List_2")
	lenght1 = len(list1)
	lenght2 = len(list2)
	result = []
	if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort("CombineTuple")):
            for i in xrange(lenght1):
                for j in xrange(lenght2):
                    tuple_ = (list1[i],list2[j])
                    result.append(tuple_)
        else:
            for i in xrange(lenght1):
                for j in xrange(lenght2):
                    if type(list1[i])==tuple and type(list2[j])==tuple:
                        tuple_ = list1[i]+list2[j]
                        result.append(tuple_)
                    elif type(list1[i])==tuple and type(list2[j])!=tuple:
                        tuple_ = list1[i]+(list2[j],)
                        result.append(tuple_)
                    elif type(list1[i])!=tuple and type(list2[j])==tuple:
                        tuple_ = (list1[i],)+list2[j]
                        result.append(tuple_)
                    else:
                        tuple_ = (list1[i],list2[j])
                        result.append(tuple_)

        self.setResult("Result", result)

#################################################################################

def registerControl(module):
    """This function is used to register the control modules. In this way, all of
    them will have the same style and shape."""
    
    reg = registry
    reg.add_module(module, moduleRightFringe=[(0.0,0.0),(0.25,0.5),(0.0,1.0)],\
                   moduleLeftFringe=[(0.0,0.0),(0.0,1.0)])

def initialize(*args,**keywords):
    reg=registry

    init_constant(ListOfElements)

    registerControl(Fold)
    registerControl(Map)
    registerControl(Filter)
    registerControl(AreaFilter)
    registerControl(SimilarityFilter)
    registerControl(If)

    reg.add_input_port(Fold, 'FunctionPort', (Module, ""))
    reg.add_input_port(Fold, 'InputList', (ListOfElements, ""))
    reg.add_input_port(Fold, 'InputPort', (ListOfElements, ""))
    reg.add_input_port(Fold, 'OutputPort', (String, ""))
    reg.add_output_port(Fold, 'Result', (Variant, ""))

##    reg.add_module(Sum)
##
##    reg.add_module(And)
##
##    reg.add_module(Or)

    reg.add_input_port(If, 'Condition', (Boolean, ""))
    reg.add_input_port(If, 'TruePort', (Module, ""))
    reg.add_input_port(If, 'FalsePort', (Module, ""))
    reg.add_input_port(If, 'TrueOutputPorts', (ListOfElements, ""), optional=True)
    reg.add_input_port(If, 'FalseOutputPorts', (ListOfElements, ""), optional=True)
    reg.add_output_port(If, 'Result', (Variant, ""))

    reg.add_module(Dot)
    reg.add_input_port(Dot, 'List_1', (ListOfElements, ""))
    reg.add_input_port(Dot, 'List_2', (ListOfElements, ""))
    reg.add_input_port(Dot, 'CombineTuple', (Boolean, ""), optional=True)
    reg.add_output_port(Dot, 'Result', (ListOfElements, ""))

    reg.add_module(Cross)
    reg.add_input_port(Cross, 'List_1', (ListOfElements, ""))
    reg.add_input_port(Cross, 'List_2', (ListOfElements, ""))
    reg.add_input_port(Cross, 'CombineTuple', (Boolean, ""), optional=True)
    reg.add_output_port(Cross, 'Result', (ListOfElements, ""))
