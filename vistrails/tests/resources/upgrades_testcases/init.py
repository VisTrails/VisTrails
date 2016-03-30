from vistrails.core.modules.vistrails_module import Module
from vistrails.core.upgradeworkflow import UpgradeModuleRemap


_upgrades = {}
_modules = []


class Test1(Module):
    _input_ports = [('port2', 'basic:String')]


_upgrades['Test1'] = [UpgradeModuleRemap('0.2', '0.4', '0.4', None,
                                         function_remap={'port': 'port2'},
                                         src_port_remap={'port': 'port2'})]
_modules.append(Test1)


class Test2(Module):
    _input_ports = [('port3', 'basic:String')]

_upgrades['Test2'] = [UpgradeModuleRemap('0.1', '0.3', '0.3', None,
                                         function_remap={'port': 'port2'},
                                         src_port_remap={'port': 'port2'}),
                      UpgradeModuleRemap('0.3', '0.4', '0.5', None,
                                         function_remap={'port2': 'port3'},
                                         src_port_remap={'port2': 'port3'}),
                      UpgradeModuleRemap('0.4', '0.5', '0.5', 'Test2n')]
_modules.append(Test2)


class Test3(Module):
    _input_ports = [('port4', 'basic:String')]

_upgrades['Test3'] = [UpgradeModuleRemap('0.1', '0.3', '0.3', None,
                                         function_remap={'port': 'port2'},
                                         src_port_remap={'port': 'port2'}),
                      UpgradeModuleRemap('0.3', '0.4', '0.5', None,
                                         function_remap={'port2': 'port3'},
                                         src_port_remap={'port2': 'port3'}),
                      UpgradeModuleRemap('0.2', '0.3', '0.5', None,
                                         function_remap={'port': 'port4'},
                                         src_port_remap={'port': 'port4'})]
_modules.append(Test3)


class Test4(Module):
    _input_ports = [('port3', 'basic:String')]

_upgrades['Test4'] = [UpgradeModuleRemap('0.1', '0.2', '0.2', None,
                                         function_remap={'port': 'port2'},
                                         src_port_remap={'port': 'port2'}),
                      UpgradeModuleRemap('0.3', '0.4', '0.4', None,
                                         function_remap={'port2': 'port3'},
                                         src_port_remap={'port2': 'port3'})]
_modules.append(Test4)
