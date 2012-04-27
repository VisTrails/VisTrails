from core.modules.vistrails_module import Module, NotCacheable

import prefuse
from prefuse.controls import DragControl, PanControl, ZoomControl
from obvious.prefuse.view import PrefuseObviousControl, PrefuseObviousView as View


# The view shouldn't be cached - we want the frame to be shown after each
# execution
class PrefuseView(NotCacheable, Module):
    """This module displays a visualization as a swing component.
    """
    def compute(self):
        visualization = self.getInputFromPort('visualization')
        preView = View(visualization, None, 'graph', None)
        preView.addListener(PrefuseObviousControl(ZoomControl()))
        preView.addListener(PrefuseObviousControl(PanControl()))
        preView.addListener(PrefuseObviousControl(DragControl()))

        view = preView.getViewJComponent()

        # This seems to be required by Prefuse
        realPreViz = visualization.getUnderlyingImpl(prefuse.Visualization)
        realPreViz.run('color')
        realPreViz.run('layout')
        self.setResult('view', view)
