""" The file describes the pipeline tab widget to manage a single
pipeline

QPipelineTab
"""

from PyQt4 import QtCore, QtGui
from core.vistrail.module import Module
from core.vistrail.connection import Connection
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.method_palette import QMethodPalette
from gui.module_annotation import QModuleAnnotation
from gui.module_methods import QModuleMethods
from gui.pipeline_view import QPipelineView
from gui.param_explore import QParameterExploration

################################################################################

class QPipelineTab(QDockContainer, QToolWindowInterface):
    """
    QPipelineTab is a tab widget setting QPipelineView in a center
    while having surrounding tool windows for manipulating a pipeline
    
    """
    def __init__(self, parent=None):
        """ QPipelineTab(parent: QWidget) -> QPipelineTab        
        Make it a main window with dockable area and a QPipelineView
        in the middle
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Pipeline')
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()        

        self.pipelineView = QPipelineView()
        self.setCentralWidget(self.pipelineView)
        
        self.methodPalette = QMethodPalette(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.methodPalette.toolWindow())
        
        self.moduleMethods = QModuleMethods(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.moduleMethods.toolWindow())
        
        self.moduleAnnotations = QModuleAnnotation(self)
        self.tabifyDockWidget(self.moduleMethods.toolWindow(),
                              self.moduleAnnotations.toolWindow())
        
        self.paramExploration = QParameterExploration(self)
        self.tabifyDockWidget(self.moduleAnnotations.toolWindow(),
                              self.paramExploration.toolWindow())
        
        self.connect(self.toolWindow(),
                     QtCore.SIGNAL('topLevelChanged(bool)'),
                     self.updateWindowTitle)
        self.connect(self.pipelineView.scene(),
                     QtCore.SIGNAL('moduleSelected'),
                     self.moduleSelected)

        self.controller = None

    def updatePipeline(self, pipeline):
        """ updatePipeline(pipeline: Pipeline) -> None        
        Setup the pipeline to display and control a specific pipeline
        
        """
        if not self.pipelineView.scene().noUpdate:            
            self.pipelineView.scene().setupScene(pipeline)

    def updateWindowTitle(self, topLevel):
        """ updateWindowTitle(topLevel: bool) -> None
        Change the current widget title depends on the top level status
        
        """
        if topLevel:
            self.setWindowTitle('Pipeline <' +
                                self.toolWindow().parent().windowTitle()+'>')
        else:
            self.setWindowTitle('Pipeline')

    def moduleSelected(self, moduleId, selection = []):
        """ moduleChanged(moduleId: int, selection: [QGraphicsModuleItem])
                          -> None
        Set up the view when module selection has been changed
        
        """
        if self.pipelineView.scene().controller:
            pipeline = self.pipelineView.scene().controller.currentPipeline
        else:
            pipieline = None
        if pipeline:            
            if pipeline.modules.has_key(moduleId):
                module = pipeline.modules[moduleId]
            else:
                module = None
            self.methodPalette.treeWidget.updateModule(module)
            self.moduleMethods.updateModule(module)
            self.moduleAnnotations.updateModule(module)
            self.emit(QtCore.SIGNAL('moduleSelectionChange'),
                      [m.id for m in selection])

    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a vistrail controller to this pipeline view
        
        """
        oldController = self.pipelineView.scene().controller
        if oldController!=controller:
            if oldController!=None:
                self.disconnect(oldController,
                                QtCore.SIGNAL('versionWasChanged'),
                                self.versionChanged)
                self.disconnect(oldController,
                                QtCore.SIGNAL('flushMoveActions()'),
                                self.flushMoveActions)
                oldController.currentPipelineView = None
            self.controller = controller
            self.pipelineView.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('versionWasChanged'),
                         self.versionChanged)
            self.connect(controller,
                         QtCore.SIGNAL('flushMoveActions()'),
                         self.flushMoveActions)
            self.moduleMethods.controller = controller
            self.moduleAnnotations.controller = controller
            self.paramExploration.controller = controller
            controller.currentPipelineView = self.pipelineView.scene()

    def versionChanged(self, newVersion):
        """ versionChanged(newVersion: int) -> None        
        Update the pipeline when the new vistrail selected in the
        controller
        
        """
        self.updatePipeline(self.controller.currentPipeline)
        if newVersion>=0:            
            prevIds = self.controller.previousModuleIds
            if len(prevIds)>0:
                for prevId in prevIds:
                    item = self.pipelineView.scene().modules[prevId]
                    item.setSelected(True)
                    item.update()
                self.controller.previousModuleIds = []
            else:
                self.moduleSelected(-1)
        else:
            self.moduleSelected(-1)
        if self.controller.resetPipelineView:
            self.pipelineView.scene().fitToAllViews()
            
    def flushMoveActions(self):
        """ flushMoveActions() -> None
        Update all move actions into vistrail
        
        """
        controller = self.pipelineView.scene().controller
        moves = []
        for (mId, item) in self.pipelineView.scene().modules.items():
            module = controller.currentPipeline.modules[mId]
            (dx,dy) = (item.scenePos().x() - module.center.x,
                       -item.scenePos().y() - module.center.y)
            if (dx!=0 or dy!=0):
                moves.append((mId, dx, dy))
        if len(moves)>0:
            controller.quiet = True
            controller.moveModuleList(moves)
            controller.quiet = False
