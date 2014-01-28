# VisTrails module imports
from vistrails.core.modules.vistrails_module import Module

# Java imports
from vistrails.packages.java.java_vm import get_java_vm


_JAVA_VM = get_java_vm()
JLabel = _JAVA_VM.javax.swing.JLabel


# Module that represents a swing component
# Essentially used as a datatype, may be instantiated as a module for
# debugging/testing purposes
class Component(Module):
    def compute(self):
        text = self.force_get_input('text', "<Swing component>")
        component = JLabel(text)
        self.set_output('component', component)
