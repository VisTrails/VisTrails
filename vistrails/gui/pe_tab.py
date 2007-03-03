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
from core.interpreter.default import default_interpreter, noncached_interpreter
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
            self.virtualCell.updateVirtualCell(
                self.controller.currentPipeline)

            # Now we need to inspect the parameter list
            self.paramView.treeWidget.updateFromPipeline(
                self.controller.currentPipeline)

            # Update the annotated ids
            self.annotatedPipelineView.updateAnnotatedIds(
                self.controller.currentPipeline)

            # Update the parameter exploration table
            self.peWidget.updatePipeline(self.controller.currentPipeline)

    def performParameterExploration(self, actions):
        """ performParameterExploration(actions: list) -> None        
        Perform the exploration given a list of action lists
        corresponding to each dimension
        
        """
        if self.controller.currentPipeline:
            explorer = ActionBasedParameterExploration()
            pipelines = explorer.explore(self.controller.currentPipeline,
                                         actions)
            # Now execute the pipelines
            progress = QtGui.QProgressDialog('Performing Parameter '
                                             'Exploration...',
                                             '&Cancel',
                                             0, len(pipelines))
            progress.setWindowTitle('Parameter Exploration')
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()

            if (registry.hasModule('CellLocation') and
                registry.hasModule('SheetReference')):
                CellLocation = registry.getDescriptorByName('CellLocation')
                SheetReference = registry.getDescriptorByName('SheetReference')
            else:
                CellLocation = SheetReference = None
            (rCount, cCount, cells) = self.virtualCell.getConfiguration()
            dim = [max(1, len(a)) for a in actions]
            pi = 0
            interpreter = default_interpreter.get()
            for t in range(dim[3]):
                for s in range(dim[2]):
                    for r in range(dim[1]):
                        for c in range(dim[0]):
                            progress.setValue(pi)
                            QtCore.QCoreApplication.processEvents()
                            if progress.wasCanceled():
                                break
                            def doneSummonHook(pipeline, objects):
                                """Hook to set the cell location"""
                                if CellLocation and SheetReference:
                                    dec = self.virtualCell.decodeConfiguration
                                    decodedCells = dec(pipeline, cells)
                                    for (mId, vRow, vCol) in decodedCells:
                                        location = CellLocation.module()
                                        location.row = r*rCount+vRow
                                        location.col = c*cCount+vCol
                                        ref = SheetReference.module()
                                        ref.compute()
                                        ref = ref.sheetReference
                                        ref.sheetName = ('PE %s %d'
                                            % (self.controller.name, (s+1)))
                                        ref.minimumRowCount = dim[1]*rCount
                                        ref.minimumColumnCount = dim[0]*cCount
                                        location.sheetReference = ref
                                        objects[mId].overrideLocation(location)
                                        
                            interpreter.setDoneSummonHook(doneSummonHook)
                            interpreter.execute(
                                pipelines[pi],
                                self.controller.name,
                                self.controller.currentVersion,
                                self.controller.currentPipelineView,
                                self.controller.logger)
                            pi += 1
            progress.setValue(len(pipelines))
