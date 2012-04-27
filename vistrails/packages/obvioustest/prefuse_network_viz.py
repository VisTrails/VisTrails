from core.modules.vistrails_module import Module, NotCacheable

from java.util import HashMap
from obvious.prefuse.viz import PrefuseObviousVisualization
from obvious.prefuse.viz.util import PrefuseObviousNetworkViz as Viz


# The visualization shouldn't be cached
class PrefuseNetworkViz(NotCacheable, Module):
    """This module creates a Prefuse network visualization for any Obvious
    network.
    """
    def compute(self):
        network = self.getInputFromPort('network')
        params = HashMap()
        params.put(PrefuseObviousVisualization.GROUP_NAME, 'graph')
        params.put(Viz.LABEL_KEY, 'label')

        visualization = Viz(network, None, None, params)
        self.setResult('visualization', visualization)
