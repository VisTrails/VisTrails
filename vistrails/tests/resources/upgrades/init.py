from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.config import IPort, OPort

class TestUpgradeA(Module):
    _input_ports = [IPort("aaa", "basic:String")]

class TestUpgradeB(Module):
    _input_ports = [IPort("b", "basic:Integer")]

_modules = [TestUpgradeA, TestUpgradeB]
