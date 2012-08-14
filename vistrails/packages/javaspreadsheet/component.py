# VisTrails module imports
from core.modules.vistrails_module import Module

# Java imports
from extras.java_vm import get_java_vm


_JAVA_VM = get_java_vm()
JLabel = _JAVA_VM.javax.swing.JLabel


# Module that represents a swing component
# Essentially used as a datatype, may be instantiated as a module for
# debugging/testing purposes
class Component(Module):
    def compute(self):
        text = self.forceGetInputFromPort('text', "<Swing component>")
        component = JLabel(text)
        self.setResult('component', component)
