from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.basic_modules import List, String

from engine_manager import EngineManager
from map import Map


def initialize(*args,**keywords):
    reg = get_module_registry()

    reg.add_module(Map)
    reg.add_input_port(Map, 'FunctionPort', (Module, ''))
    reg.add_input_port(Map, 'InputList', (List, ''))
    reg.add_input_port(Map, 'InputPort', (List, ''))
    reg.add_input_port(Map, 'OutputPort', (String, ''))
    reg.add_output_port(Map, 'Result', (List, ''))


def finalize():
    EngineManager.cleanup()


def menu_items():
    return (
            ("Start new engine processes",
             lambda: EngineManager.start_engines()),
            ("Show information on the cluster",
             lambda: EngineManager.info()),
            ("Change profile",
             lambda: EngineManager.change_profile()),
            ("Cleanup started processes",
             lambda: EngineManager.cleanup()),
            ("Request cluster shutdown",
             lambda: EngineManager.shutdown_cluster()),
    )
