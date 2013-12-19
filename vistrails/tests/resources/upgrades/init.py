from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.config import IPort, OPort

class TestUpgradeA(Module):
    _input_ports = [IPort("aaa", "basic:String")]
    _output_ports = [OPort("zzz", "basic:Integer")]

class TestUpgradeB(Module):
    _input_ports = [IPort("b", "basic:Integer")]

def handle_module_upgrade_request(c, module_id, pipeline):
    from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler, \
        UpgradePackageRemap, UpgradeModuleRemap
   
    module_remap_1 = UpgradeModuleRemap('0.8', '0.9', '0.9', None)
    module_remap_1.add_remap('function_remap', 'a', 'aa')
    module_remap_1.add_remap('src_port_remap', 'z', 'zz')
    module_remap_2 = UpgradeModuleRemap('0.9', '1.0', '1.0', None)
    module_remap_2.add_remap('function_remap', 'aa', 'aaa')
    module_remap_2.add_remap('src_port_remap', 'zz', 'zzz')
    pkg_remap = UpgradePackageRemap()
    pkg_remap.add_module_remap("TestUpgradeA", module_remap_1)
    pkg_remap.add_module_remap("TestUpgradeA", module_remap_2)

    return UpgradeWorkflowHandler.remap_module(c, module_id, pipeline,
                                               pkg_remap)

_modules = [TestUpgradeA, TestUpgradeB]
