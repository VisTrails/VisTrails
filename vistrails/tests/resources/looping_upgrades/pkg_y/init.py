from vistrails.core.modules.module_descriptor import ModuleDescriptor
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.upgradeworkflow import UpgradeModuleRemap


class Y(Module):
    _output_ports = [('result', 'basic:String')]

    def compute(self):
        self.set_output('result', 'Y')


_modules = [Y]

_upgrades = {'Y' : [UpgradeModuleRemap(
        # Upgrade for looping_fix.y 0.1 -> 0.2
        # replaces module Y with module X from looping_fix.x 0.1
        '0.1', '0.2', '0.2',
        new_module=ModuleDescriptor(
                package='org.vistrails.vistrails.tests.looping_fix.x',
                name='X',
                namespace='',
                package_version='0.1'))]}
