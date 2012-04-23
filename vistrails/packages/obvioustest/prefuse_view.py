from core.modules.vistrails_module import Module, NotCacheable

from java.lang import Class

from javax.swing import JFrame

import prefuse
from prefuse.controls import DragControl, PanControl, ZoomControl
from obvious.prefuse.view import PrefuseObviousControl, PrefuseObviousView as View


# The view shouldn't be cached - we want the frame to be shown after each
# execution
class PrefuseView(NotCacheable, Module):
    """This module displays a visualization in a swing Frame.
    """
    def compute(self):
        visualization = self.getInputFromPort('visualization')
        preView = View(visualization, None, 'graph', None)
        preView.addListener(PrefuseObviousControl(ZoomControl()))
        preView.addListener(PrefuseObviousControl(PanControl()))
        preView.addListener(PrefuseObviousControl(DragControl()))
        
        frame = JFrame()
        frame.setContentPane(preView.getViewJComponent())
        frame.pack()
        frame.setVisible(True)
        
        # This seems to be required by Prefuse
        realPreViz = visualization.getUnderlyingImpl(prefuse.Visualization)
        realPreViz.run('color')
        realPreViz.run('layout')
        self.setResult('frame', frame)
