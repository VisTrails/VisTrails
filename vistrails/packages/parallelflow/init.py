from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry
from core.modules.basic_modules import String, Variant, List

from map import Map

def initialize(*args,**keywords):
    reg = get_module_registry()

    reg.add_module(Map)
    reg.add_input_port(Map, 'FunctionPort', (Module, ""))
    reg.add_input_port(Map, 'InputList', (List, ""))
    reg.add_input_port(Map, 'InputPort', (List, ""))
    reg.add_input_port(Map, 'OutputPort', (List, ""))
    reg.add_output_port(Map, 'Result', (Variant, ""))