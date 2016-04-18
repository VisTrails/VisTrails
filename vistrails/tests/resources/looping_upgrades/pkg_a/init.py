from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.upgradeworkflow import UpgradeModuleRemap


class A(Module):
    _output_ports = [('result', 'basic:String')]

    def compute(self):
        self.set_output('result', 'A')


_modules = [A]

_upgrades = {'A' : [UpgradeModuleRemap(
        # Upgrade for looping_fix.a 0.1 -> 0.2
        # replaces module A with module B from looping_fix.b 0.1
        '0.1', '0.2', '0.2',
        new_module=ModuleDescriptor(
                package='org.vistrails.vistrails.tests.looping_fix.b',
                name='B',
                namespace='',
                package_version='0.1'))]}
