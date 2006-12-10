""" The file describes the query tab widget to apply a query/filter to
the current pipeline/version view

QQueryTab
"""

from PyQt4 import QtCore, QtGui
from core.vistrail import Vistrail
from gui.pipeline_tab import QPipelineTab
from gui.theme import CurrentTheme
from gui.vistrail_controller import VistrailController

################################################################################

class QQueryTab(QPipelineTab):
    """
    QQuery is the similar to the pipeline tab where we can interact
    with pipeline. However, no modules properties is accessibled. Just
    connections. Then we can apply this pipeline to be a query on both
    version and pipeline view
    
    """
    def __init__(self, parent=None):
        """ QQueryTab(parent: QWidget) -> QQueryTab
        Create an empty vistrail controller for this query tab
        
        """
        QPipelineTab.__init__(self, parent)
#        self.pipelineView.setBackgroundBrush(
#            CurrentTheme.QUERY_BACKGROUND_BRUSH)
        
        controller = VistrailController()
        controller.setVistrail(Vistrail(), 'Query Vistrail')
        self.setController(controller)
        controller.changeSelectedVersion(0)
        self.connect(controller,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        Update the pipeline when the vistrail version has changed
        
        """
        self.updatePipeline(self.controller.currentPipeline)
