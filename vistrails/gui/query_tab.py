############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
""" The file describes the query tab widget to apply a query/filter to
the current pipeline/version view

QQueryTab
"""

from PyQt4 import QtCore, QtGui
from core.vistrail.vistrail import Vistrail
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
        self.pipelineView.setBackgroundBrush(
            CurrentTheme.QUERY_BACKGROUND_BRUSH)
        
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
        self.emit(QtCore.SIGNAL("queryPipelineChange"),
                  len(self.controller.currentPipeline.modules)>0)
