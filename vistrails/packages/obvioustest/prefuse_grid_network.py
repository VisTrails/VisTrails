from core.modules.vistrails_module import Module

from obvious.prefuse.data import PrefuseObviousNetwork
from prefuse.util import GraphLib


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
