from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.upgradeworkflow import UpgradeModuleRemap


class X(Module):
    _output_ports = [('result', 'basic:String')]

    def compute(self):
        self.set_output('result', 'X')


_modules = [X]

_upgrades = {'X' : [UpgradeModuleRemap(
        # Upgrade for looping_fix.x 0.1 -> 0.2
        # replaces module X with module Y from looping_fix.y 0.1
        '0.1', '0.2', '0.2',
        new_module=ModuleDescriptor(
                package='org.vistrails.vistrails.tests.looping_fix.y',
                name='Y',
                namespace='',
                package_version='0.1'))]}
