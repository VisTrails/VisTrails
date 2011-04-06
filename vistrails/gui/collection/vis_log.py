############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
""" This modules builds a widget to visualize workflow execution logs """
from PyQt4 import QtCore, QtGui
from core.vistrail.pipeline import Pipeline
from core.log.module_exec import ModuleExec
from core.log.group_exec import GroupExec
from core.log.loop_exec import LoopExec
from core.log.workflow_exec import WorkflowExec
from gui.pipeline_view import QPipelineView
from gui.theme import CurrentTheme
from core import system, debug
import core.db.io


##############################################################################


class QExecutionItem(QtGui.QTreeWidgetItem):
    """
    QExecutionListWidget is a widget containing a list of workflow executions.
    
    """
    def __init__(self, execution, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.execution = execution
        execution.item = self
        if execution.__class__ == WorkflowExec:
            self.setText(0, 'Workflow %s' % execution.parent_version )
            for item_exec in execution.item_execs:
                self.addChild(QExecutionItem(item_exec))
        if execution.__class__ == ModuleExec:
            self.setText(0, '%s' % execution.module_name)
            for loop_exec in execution.loop_execs:
                self.addChild(QExecutionItem(loop_exec))
        if execution.__class__ == GroupExec:
            self.setText(0, 'Group')
            for item_exec in execution.item_execs:
                self.addChild(QExecutionItem(item_exec))
        if execution.__class__ == LoopExec:
            self.setText(0, 'Loop #%s' % execution.db_iteration)
            for item_exec in execution.item_execs:
                self.addChild(QExecutionItem(item_exec))
        self.setText(1, '%s' % execution.ts_start)
        self.setText(2, '%s' % execution.ts_end)
        self.setText(3, '%s' % {'0':'No', '1':'Yes'}.get(
                               str(execution.completed), 'Error'))

class QExecutionListWidget(QtGui.QTreeWidget):
    """
    QExecutionListWidget is a widget containing a list of workflow executions.
    
    """
    def __init__(self, log, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setColumnCount(4)
        self.setHeaderLabels(['Type', 'Start', 'End', 'Completed'])
        for execution in log.workflow_execs:
            self.addTopLevelItem(QExecutionItem(execution))
        self.setSortingEnabled(True)

#        annotations = execution.db_annotations
#        if len(annotations):
#            self.infoList.addItem('')
#            self.infoList.addItem("Annotations:")
#            for annotation in annotations:
#                self.infoList.addItem("%s: %s" % (annotation.key,annotation.value))
#        loop_execs = execution.db_loop_execs
#        if len(loop_execs):
#            self.infoList.addItem('')
#            self.infoList.addItem("Loop executions:")
#            for e in loop_execs:
#                self.infoList.addItem("Loop %s" % e.db_id)
#                startTime = e.ts_start
#                if startTime:
#                    self.infoList.addItem("    Start time: %s" % startTime)
#                endTime = e.ts_end
#                if endTime:
#                    self.infoList.addItem("    End time: %s" % endTime)
#                error = e.error
#                if error:
#                    self.infoList.addItem("Error: %s" % error)
    
class QLegendBox(QtGui.QFrame):
    """
    QLegendBox is just a rectangular box with a solid color
    
    """
    def __init__(self, brush, size, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QLegendBox(color: QBrush, size: (int,int), parent: QWidget,
                      f: WindowFlags) -> QLegendBox
        Initialize the widget with a color and fixed size
        
        """
        QtGui.QFrame.__init__(self, parent, f)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette(self.palette())
        palette.setBrush(QtGui.QPalette.Window, brush)
        self.setPalette(palette)
        self.setFixedSize(*size)
        if system.systemType in ['Darwin']:
            #the mac's nice looking messes up with the colors
            if QtCore.QT_VERSION < 0x40500:
                self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
            else:
                self.setAttribute(QtCore.Qt.WA_MacBrushedMetal, False)
        

class QLegendWidget(QtGui.QWidget):
    """
    QLegendWindow contains a list of QLegendBox and its description
    
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.setFont(CurrentTheme.VISUAL_DIFF_LEGEND_FONT)
        
        data = [[0, "Successful",      CurrentTheme.SUCCESS_MODULE_BRUSH],
                [1, "Error",             CurrentTheme.ERROR_MODULE_BRUSH],
                [2, "Not executed", CurrentTheme.PERSISTENT_MODULE_BRUSH],
                [3, "Cached",     CurrentTheme.NOT_EXECUTED_MODULE_BRUSH]]
        
        for n, text, brush in data:         
            self.gridLayout.addWidget(
                QLegendBox(brush, CurrentTheme.VISUAL_DIFF_LEGEND_SIZE, self),
                0, n*2)
            self.gridLayout.addWidget(QtGui.QLabel(text, self), 0, n*2+1)

class QVisualLog(QtGui.QDialog):
    """
    QVisualLog is a main widget for Visual Log containing a GL
    Widget to draw the pipeline
    
    """
    def __init__(self, vistrail, exec_id=None,
                 parent=None, f=QtCore.Qt.WindowFlags()):
        """ QVisualLog(vistrail: Vistrail, exec_id: id/date
                       parent: QWidget, f: WindowFlags) -> QVisualLog
        
        """
        QtGui.QDialog.__init__(self, parent)
        self.vistrail = vistrail
        self.version = None
        self.currentItem = None
        self.workflowExecution = None
        self.parentExecution = None
        self.execution = None
        self.pipeline = None
        self.log = vistrail.get_log()
        # exec_id can be a number or a datetime
        try:
            workflow_execs = \
                [e for e in self.log.workflow_execs if e.id == int(exec_id)]
        except (ValueError, TypeError):
            workflow_execs = [e for e in self.log.workflow_execs
                              if str(e.ts_start) == str(exec_id)]

        # Set up the version name correctly
#        vName = vistrail.getVersionName(version)
#        if not vName: vName = 'Version %d' % version
#        self.v_name = vName

        # Create the top-level Visual Diff window
        self.setWindowTitle("Exploring workflow executions in vistrail '%s'" %
                            vistrail.db_name)
        widget = QtGui.QSplitter()
        widget.setOpaqueResize(False)
        widget.setOrientation(QtCore.Qt.Horizontal)
        layout=QtGui.QGridLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(widget)
        self.setLayout(layout)
        pipelineLayout = QtGui.QVBoxLayout()
        pipelineLayout.setMargin(0)
        pipelineLayout.setSpacing(0)
        pipelineLayout.addWidget(QLegendWidget(), QtCore.Qt.AlignCenter)
        self.pipelineView = QPipelineView()
        pipelineLayout.addWidget(self.pipelineView)
        pipelineLayout.setStretch(0,0)
        pipelineLayout.setStretch(1,1)
        pipelineWidget = QtGui.QWidget()
        pipelineWidget.setLayout(pipelineLayout)
        widget.addWidget(pipelineWidget)
        executionWidget = QtGui.QSplitter()
        executionWidget.setOrientation(QtCore.Qt.Vertical)
        self.executionList = QExecutionListWidget(self.log)
        executionWidget.addWidget(self.executionList)
        self.detailsWidget = QtGui.QTextEdit()
        executionWidget.addWidget(self.detailsWidget)
        widget.addWidget(executionWidget)
        self.resize(1024,768)
        widget.setStretchFactor(0,1)
        widget.setStretchFactor(1,1)
        
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.connect(self.executionList, QtCore.SIGNAL(
         "currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
         self.itemClicked)
#        self.center()

        # Hook shape selecting functions
        self.connect(self.pipelineView.scene(), QtCore.SIGNAL("moduleSelected"),
                     self.moduleSelected)

        if len(workflow_execs):
            self.execution = workflow_execs[0]
            self.workflowExecution = self.execution
            self.parentExecution = self.execution
            self.version = self.execution.parent_id
            self.showExecution()
            self.executionList.setCurrentItem(self.execution.item)
        else:
            core.debug.warning("Workflow Execution not found: %s" % exec_id)

    def itemClicked(self, item, olditem):
        self.currentItem = item
        self.execution = item.execution
        import api
        api.e = self.execution
        self.workflowExecution = item
        while self.workflowExecution.parent():
            self.workflowExecution = self.workflowExecution.parent()
        self.workflowExecution = self.workflowExecution.execution
        self.parentExecution = item
        while self.parentExecution.execution.__class__ not in \
                [WorkflowExec, LoopExec]:
            self.parentExecution = self.parentExecution.parent()
        self.parentExecution = self.parentExecution.execution
        self.showExecution()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2,
        (screen.height()-size.height())/2)

    def toggleShowDetails(self):
        scene = self.pipelineView.scene()
        if self.showDetailsAction.isChecked():
            self.infoItems = []
            module_execs = dict([(e.db_module_id, e) \
                                 for e in self.execution.db_get_item_execs()])
            for m_id, item in self.moduleItems.iteritems():
                if m_id in module_execs:
                    e = module_execs[m_id]
                    text = "Start: %s\nEnd:   %s" % \
                                         (str(e.ts_start), str(e.ts_end))
                    if e.error:
                        text += '\nError: %s' % e.error
                    textItem = scene.addText(text)
                    textItem.setFont(QtGui.QFont('Courier', 10, QtGui.QFont.Normal))
                    textItem.setDefaultTextColor(QtGui.QColor(255, 255, 255))
                    bg = scene.addRect(textItem.boundingRect(),
                                       QtGui.QPen(QtCore.Qt.NoPen),
                                       QtGui.QBrush(QtGui.QColor(0, 0, 0, 128+64)))
                    x =  - textItem.boundingRect().width()/2
                    y = item.boundingRect().bottom()
                    bg.setPos(x, y)
                    bg.setParentItem(item)
                    bg.setZValue(100000.0)
                    textItem.setParentItem(bg)
                    textItem.setZValue(200000.0)
                    self.infoItems.append(bg)
        else:
            for item in self.infoItems:
                scene.removeItem(item)

    def moduleSelected(self, id, selectedItems):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        """
        if len(selectedItems)!=1 or id==-1:
            self.moduleUnselected()
            return

        item = selectedItems[0]
        if hasattr(item,'execution') and item.execution:
            self.execution = item.execution
            self.executionList.setCurrentItem(item.execution.item)
        else:
            self.executionList.clearSelection()
            self.execution = self.parentExecution
        self.showDetails()

    def moduleUnselected(self):
        """ moduleUnselected() -> None
        When a user selects nothing, make sure to display nothing as well
        
        """
        self.executionList.clearSelection()
        self.execution = self.parentExecution
        self.showDetails()
                    
    def showExecution(self):
        self.version = self.workflowExecution.parent_version
        self.updatePipeline()
        self.showDetails()

    def showDetails(self):
        if not self.execution:
            return

        text = ''
        text += '%s\n' % self.execution.item.text(0)
        text += 'Start: %s\n' % self.execution.ts_start
        text += 'End: %s\n' % self.execution.ts_end
        if hasattr(self.execution, 'user'):
            text += 'User: %s\n' % self.execution.user
        if hasattr(self.execution, 'cached'):
            text += 'Cached: %s\n' % ("Yes" if self.execution.cached else 'No')
        text += 'Completed: %s\n' % {'0':'No', '1':'Yes'}.get(
                                    str(self.execution.completed), 'Error')
        if hasattr(self.execution, 'error') and self.execution.error:
            text += 'Error: %s\n' % self.execution.error
        self.detailsWidget.setText(text)
        
    def updatePipeline(self):
        """ createLogPipeline() -> None
        Actually walk through the version and add all modules
        into the pipeline view
        
        """
        scene = self.pipelineView.scene()
        scene.clearItems()
        self.pipeline = self.vistrail.getPipeline(self.version)
        self.pipeline.validate(False)

        # FIXME HACK: We will create a dummy object that looks like a
        # controller so that the qgraphicsmoduleitems and the scene
        # are happy. It will simply store the pipeline will all
        # modules and connections of the diff, and know how to copy stuff
        class DummyController(object):
            def __init__(self, pip):
                self.current_pipeline = pip
                self.search = None
            def copy_modules_and_connections(self, module_ids, connection_ids):
                """copy_modules_and_connections(module_ids: [long],
                                             connection_ids: [long]) -> str
                Serializes a list of modules and connections
                """

                pipeline = Pipeline()
#                 pipeline.set_abstraction_map( \
#                     self.current_pipeline.abstraction_map)
                for module_id in module_ids:
                    module = self.current_pipeline.modules[module_id]
#                     if module.vtType == Abstraction.vtType:
#                         abstraction = \
#                             pipeline.abstraction_map[module.abstraction_id]
#                         pipeline.add_abstraction(abstraction)
                    pipeline.add_module(module)
                for connection_id in connection_ids:
                    connection = self.current_pipeline.connections[connection_id]
                    pipeline.add_connection(connection)
                return core.db.io.serialize(pipeline)
                
#        if 
#        execs = 
        module_execs = dict([(e.db_module_id, e) \
                             for e in self.parentExecution.db_get_item_execs()])
        controller = DummyController(self.pipeline)
        scene.controller = controller
        self.moduleItems = {}
        for m_id in self.pipeline.modules:
            module = self.pipeline.modules[m_id]
            brush = CurrentTheme.PERSISTENT_MODULE_BRUSH
            if m_id in module_execs:
                e = module_execs[m_id]
                if e.completed:
                    if e.error:
                        brush = CurrentTheme.ERROR_MODULE_BRUSH
                    elif e.cached:
                        brush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                    else:
                        brush = CurrentTheme.SUCCESS_MODULE_BRUSH
                else:
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
            module.is_valid = True
            item = scene.addModule(module, brush)
            item.controller = controller
            self.moduleItems[m_id] = item
            if m_id in module_execs:
                e = module_execs[m_id]
                item.execution = e
                e.module = item
            else:
                item.execution = None
        connectionItems = []
        for c in self.pipeline.connections.values():
            connectionItems.append(scene.addConnection(c))

        # Color Code connections
        for c in connectionItems:
            pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
            pen.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 128+64)))
            c.connectionPen = pen

        scene.updateSceneBoundingRect()
        scene.fitToView(self.pipelineView, True)
        if self.execution.__class__ in [ModuleExec, GroupExec]:
            self.execution.item.setSelected(True)
            self.execution.module.setSelected(True)
