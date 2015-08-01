from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.upgradeworkflow import UpgradeModuleRemap


class B(Module):
    _output_ports = [('result', 'basic:String')]

    def compute(self):
        self.set_output('result', 'B')


_modules = [B]

_upgrades = {'B' : [UpgradeModuleRemap(
        # Upgrade for looping_fix.b 0.1 -> 0.2
        # replaces module B with module C from looping_fix.c 1.0
        '0.1', '0.2', '0.2',
        new_module=ModuleDescriptor(
                package='org.vistrails.vistrails.tests.looping_fix.c',
                name='C',
                namespace='',
                package_version='1.0'))]}
