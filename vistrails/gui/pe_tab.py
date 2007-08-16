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
""" The file describes the parameter exploration tab for VisTrails

QParameterExplorationTab
"""

from PyQt4 import QtCore, QtGui
from core.interpreter.default import get_default_interpreter
from core.modules.module_registry import registry
from core.param_explore import ActionBasedParameterExploration
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.pe_table import QParameterExplorationWidget
from gui.virtual_cell import QVirtualCellWindow
from gui.param_view import QParameterView
from gui.pe_pipeline import QAnnotatedPipelineView

################################################################################

class QParameterExplorationTab(QDockContainer, QToolWindowInterface):
    """
    QParameterExplorationTab is a tab containing different widgets
    related to parameter exploration
    
    """
    explorationId = 0
    
    def __init__(self, parent=None):
        """ QParameterExplorationTab(parent: QWidget)
                                    -> QParameterExplorationTab
        Make it a main window with dockable area and a
        QParameterExplorationTable
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Parameter Exploration')
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()

        self.peWidget = QParameterExplorationWidget()
        self.setCentralWidget(self.peWidget)
        self.connect(self.peWidget.table,
                     QtCore.SIGNAL('requestParameterExploration'),
                     self.performParameterExploration)
        self.connect(self.peWidget,
                     QtCore.SIGNAL('exploreChange(bool)'),
                     self.exploreChange)

        self.paramView = QParameterView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.paramView.toolWindow())
        
        self.annotatedPipelineView = QAnnotatedPipelineView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.annotatedPipelineView.toolWindow())
        
        self.virtualCell = QVirtualCellWindow(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.virtualCell.toolWindow())
        
        self.controller = None
        self.currentVersion = -1

    def addViewActionsToMenu(self, menu):
        """addViewActionsToMenu(menu: QMenu) -> None
        Add toggle view actions to menu
        
        """
        menu.addAction(self.paramView.toolWindow().toggleViewAction())
        menu.addAction(self.annotatedPipelineView.toolWindow().toggleViewAction())
        menu.addAction(self.virtualCell.toolWindow().toggleViewAction())

    def removeViewActionsFromMenu(self, menu):
        """removeViewActionsFromMenu(menu: QMenu) -> None
        Remove toggle view actions from menu
        
        """
        menu.removeAction(self.paramView.toolWindow().toggleViewAction())
        menu.removeAction(self.annotatedPipelineView.toolWindow().toggleViewAction())
        menu.removeAction(self.virtualCell.toolWindow().toggleViewAction())
        
    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a controller to the parameter exploration tab
        
        """
        self.controller = controller

    def showEvent(self, event):
        """ showEvent(event: QShowEvent) -> None
        Update the tab when it is shown
        
        """
        if self.currentVersion!=self.controller.currentVersion:
            self.currentVersion = self.controller.currentVersion
            # Update the virtual cell
            pipeline = self.controller.currentPipeline
            self.virtualCell.updateVirtualCell(pipeline)

            # Now we need to inspect the parameter list
            self.paramView.treeWidget.updateFromPipeline(pipeline)

            # Update the annotated ids
            self.annotatedPipelineView.updateAnnotatedIds(pipeline)

            # Update the parameter exploration table
            self.peWidget.updatePipeline(pipeline)

    def performParameterExploration(self, actions):
        """ performParameterExploration(actions: list) -> None        
        Perform the exploration given a list of action lists
        corresponding to each dimension
        
        """
        if self.controller.currentPipeline:
            explorer = ActionBasedParameterExploration()
            (pipelines, performedActions) = explorer.explore(
                self.controller.currentPipeline, actions)
            
            dim = [max(1, len(a)) for a in actions]
            if (registry.hasModule('CellLocation') and
                registry.hasModule('SheetReference')):
                modifiedPipelines = self.virtualCell.positionPipelines(
                    'PE#%d %s' % (QParameterExplorationTab.explorationId,
                                  self.controller.name),
                    dim[2], dim[1], dim[0], pipelines)
            else:
                modifiedPipelines = pipelines

            mCount = []
            for p in modifiedPipelines:
                if len(mCount)==0:
                    mCount.append(0)
                else:
                    mCount.append(len(p.modules)+mCount[len(mCount)-1])
                
            # Now execute the pipelines
            totalProgress = sum([len(p.modules) for p in modifiedPipelines])
            progress = QtGui.QProgressDialog('Performing Parameter '
                                             'Exploration...',
                                             '&Cancel',
                                             0, totalProgress)
            progress.setWindowTitle('Parameter Exploration')
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()

            QParameterExplorationTab.explorationId += 1
            interpreter = get_default_interpreter()
            for pi in range(len(modifiedPipelines)):
                progress.setValue(mCount[pi])
                QtCore.QCoreApplication.processEvents()
                if progress.wasCanceled():
                    break
                def moduleExecuted(objId):
                    if not progress.wasCanceled():
                        progress.setValue(progress.value()+1)
                        QtCore.QCoreApplication.processEvents()
                interpreter.execute(
                    None,
                    modifiedPipelines[pi],
                    self.controller.locator,
                    self.controller.currentVersion,
                    self.controller.currentPipelineView,
                    moduleExecutedHook=[moduleExecuted],
                    reason='Parameter Exploration',
                    actions=performedActions[pi])
            progress.setValue(totalProgress)

    def exploreChange(self, notEmpty):
        """ exploreChange(notEmpty: bool) -> None
        echo the signal
        
        """
        self.emit(QtCore.SIGNAL('exploreChange(bool)'), notEmpty)

        
