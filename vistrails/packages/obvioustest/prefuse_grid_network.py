from core.modules.vistrails_module import Module

from extras.java_vm import get_java_vm


_JAVA_VM = get_java_vm()

PrefuseObviousNetwork = _JAVA_VM.obvious.prefuse.data.PrefuseObviousNetwork
GraphLib = _JAVA_VM.prefuse.util.GraphLib


class PrefuseGridNetwork(Module):
    """This module generates a simple grid network of the requested size.
    It uses Prefuse's GraphLib.getGrid().
    """
    def compute(self):
        m = self.getInputFromPort('m')
        n = self.getInputFromPort('n')
        preGraph = GraphLib.getGrid(m, n)
        network = PrefuseObviousNetwork(preGraph)
        self.setResult('network', network)
