from core.modules.vistrails_module import Module
from core.modules.module_registry import registry
from core.modules.basic_modules import Boolean, String, Variant, init_constant
import copy

from list_module import ListOfElements
from fold import Fold
from utils import Map, Filter, AreaFilter, SimilarityFilter
from conditional import If
from products import Dot, Cross
from order import ExecuteInOrder


#################################################################################
## An useful register function for control modules

def registerControl(module):
    """This function is used to register the control modules. In this way, all of
    them will have the same style and shape."""
    
    reg = registry
    reg.add_module(module, moduleRightFringe=[(0.0,0.0),(0.25,0.5),(0.0,1.0)],\
                   moduleLeftFringe=[(0.0,0.0),(0.0,1.0)])

#################################################################################

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

    reg.add_module(ExecuteInOrder)
    reg.add_input_port(ExecuteInOrder, 'module1', (Module, ""))
    reg.add_input_port(ExecuteInOrder, 'module2', (Module, ""))
