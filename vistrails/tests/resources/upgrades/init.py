from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.upgradeworkflow import  UpgradeModuleRemap

class TestUpgradeA(Module):
    _input_ports = [IPort("aaa", "basic:String")]
    _output_ports = [OPort("zzz", "basic:Integer")]

class TestUpgradeB(Module):
    _input_ports = [IPort("b", "basic:Integer")]

_modules = [TestUpgradeA, TestUpgradeB]
_upgrades = {"TestUpgradeA": 
             [UpgradeModuleRemap('0.8', '0.9', '0.9', None,
                                 function_remap={'a': 'aa'},
                                 src_port_remap={'z': 'zz'}),
              UpgradeModuleRemap('0.9', '1.0', '1.0', None,
                                 function_remap={'aa': 'aaa'},
                                 src_port_remap={'zz': 'zzz'})]}
