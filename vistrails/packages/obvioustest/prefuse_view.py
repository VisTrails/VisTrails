from core.modules.vistrails_module import Module, NotCacheable

from extras.java_vm import get_java_vm


_JAVA_VM = get_java_vm()

prefuse = _JAVA_VM.prefuse
DragControl = prefuse.controls.DragControl
PanControl = prefuse.controls.PanControl
ZoomControl = prefuse.controls.ZoomControl

PrefuseObviousControl = _JAVA_VM.obvious.prefuse.view.PrefuseObviousControl
View = _JAVA_VM.obvious.prefuse.view.PrefuseObviousView


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
