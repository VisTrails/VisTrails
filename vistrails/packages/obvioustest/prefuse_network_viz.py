from core.modules.vistrails_module import Module, NotCacheable

from extras.java_vm import get_java_vm


_JAVA_VM = get_java_vm()

HashMap = _JAVA_VM.java.util.HashMap
PrefuseObviousVisualization = \
        _JAVA_VM.obvious.prefuse.viz.PrefuseObviousVisualization
Viz = _JAVA_VM.obvious.prefuse.viz.util.PrefuseObviousNetworkViz


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
