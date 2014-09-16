###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" This modules builds a widget to visualize workflow execution logs """
from PyQt4 import QtCore, QtGui
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.log.group_exec import GroupExec
from vistrails.core.log.loop_exec import LoopExec, LoopIteration
from vistrails.core.log.workflow_exec import WorkflowExec
from vistrails.gui.pipeline_view import QPipelineView
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.gui.collection.workspace import QWorkspaceWindow
from vistrails.core import system, debug
import vistrails.core.db.io


##############################################################################


class QExecutionItem(QtGui.QTreeWidgetItem):
    """
    QExecutionItem represents a workflow or module execution.

    """
    def __init__(self, execution, parent=None, prev=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.execution = execution
        execution.item = self
        self.modules = []
        self.wf_item = prev or self

        if isinstance(execution, WorkflowExec):
            for item_exec in execution.item_execs:
                QExecutionItem(item_exec, self, self)
            if execution.completed == -2:
                brush = CurrentTheme.SUSPENDED_MODULE_BRUSH
            elif execution.completed == 1:
                brush = CurrentTheme.SUCCESS_MODULE_BRUSH
            else:
                brush = CurrentTheme.ERROR_MODULE_BRUSH

            if execution.db_name:
                self.setText(0, execution.db_name)
            else:
                self.setText(0, 'Version #%s' % execution.parent_version )
        elif isinstance(execution, ModuleExec):
            prev.modules.append(self)
            for loop_exec in execution.loop_execs:
                QExecutionItem(loop_exec, self, prev)
            if execution.completed == 1:
                if execution.error:
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
                    self.wf_item.execution.completed = -1
                elif execution.cached:
                    brush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                else:
                    brush = CurrentTheme.SUCCESS_MODULE_BRUSH
            elif execution.completed == -2:
                brush = CurrentTheme.SUSPENDED_MODULE_BRUSH
            else:
                brush = CurrentTheme.ERROR_MODULE_BRUSH
            self.setText(0, '%s' % execution.module_name)
        elif isinstance(execution, GroupExec):
            prev.modules.append(self)
            for item_exec in execution.item_execs:
                if isinstance(item_exec, LoopExec):
                    QExecutionItem(item_exec, self, prev)
                else:
                    QExecutionItem(item_exec, self, self)
            if execution.completed == 1:
                if execution.error:
                    self.wf_item.execution.completed = -1
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
                elif execution.cached:
                    brush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                else:
                    brush = CurrentTheme.SUCCESS_MODULE_BRUSH
            elif execution.completed == -2:
                brush = CurrentTheme.SUSPENDED_MODULE_BRUSH
            else:
                brush = CurrentTheme.ERROR_MODULE_BRUSH
            self.setText(0, 'Group')
        elif isinstance(execution, LoopExec):
            for iteration in execution.loop_iterations:
                QExecutionItem(iteration, self, prev)
            brush = CurrentTheme.MODULE_BRUSH
            self.setText(0, 'Loop')
        elif isinstance(execution, LoopIteration):
            for item_exec in execution.item_execs:
                QExecutionItem(item_exec, self, prev)
            if execution.completed == 1:
                if execution.error:
                    self.wf_item.execution.completed = -1
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
                else:
                    brush = CurrentTheme.SUCCESS_MODULE_BRUSH
            elif execution.completed == -2:
                brush = CurrentTheme.SUSPENDED_MODULE_BRUSH
            else:
                brush = CurrentTheme.ERROR_MODULE_BRUSH
            self.setText(0, 'Iteration #%s' % execution.iteration)

        self.setText(1, execution.ts_start.strftime(
                    '%H:%M %d/%m').replace(' 0', ' ').replace('/0', '/'))
        self.setData(1, QtCore.Qt.UserRole, str(execution.ts_start))
        #self.setText(2, '%s' % execution.ts_end) end is hidden
        pixmap = QtGui.QPixmap(10,10)
        pixmap.fill(brush.color())
        icon = QtGui.QIcon(pixmap)
        self.setIcon(0, icon)


    def __lt__( self, other ):

        tree = self.treeWidget()
        if ( not tree ):
            column = 0
        else:
            column = tree.sortColumn()

        if column != 1: # only use special sorting for date
            return super(QExecutionItem, self).__lt__(other)

        return self.data(1, QtCore.Qt.UserRole) < other.data(1, QtCore.Qt.UserRole)

class QExecutionListWidget(QtGui.QTreeWidget):
    """
    QExecutionListWidget is a widget containing a list of workflow executions.
    
    """
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setColumnCount(2)
        self.setHeaderLabels(['Pipeline', 'Start']) # end is hidden
        self.header().setDefaultSectionSize(200)
        self.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.setSortingEnabled(True)

    def set_log(self, log=None):
        self.clear()
        if log is not None:
            for execution in log:
                self.addTopLevelItem(QExecutionItem(execution))

    def add_workflow_exec(self, workflow_exec):
        # mark as recent
        workflow_exec.db_name = workflow_exec.db_name + '*' \
                             if workflow_exec.db_name \
          else '%s*' % self.controller.get_pipeline_name(
                  workflow_exec.parent_version)
        
        self.addTopLevelItem(QExecutionItem(workflow_exec))
       
    
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
        
        data = [[0, 0, "Successful",      CurrentTheme.SUCCESS_MODULE_BRUSH],
                [0, 1, "Error",             CurrentTheme.ERROR_MODULE_BRUSH],
                [0, 2, "Cached",     CurrentTheme.NOT_EXECUTED_MODULE_BRUSH],
                [1, 0, "Not executed", CurrentTheme.PERSISTENT_MODULE_BRUSH],
                [1, 1, "Suspended",     CurrentTheme.SUSPENDED_MODULE_BRUSH]]

        for x, y, text, brush in data:         
            self.gridLayout.addWidget(
                QLegendBox(brush, CurrentTheme.VISUAL_DIFF_LEGEND_SIZE, self),
                x*2, y*2)
            self.gridLayout.addWidget(QtGui.QLabel(text, self), x*2, y*2+1)

class QLogDetails(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = None
        self.execution = None
        self.parentItem = None
        self.set_title("Log Details")
        self.legend = QLegendWidget()
        self.executionList = QExecutionListWidget()
        self.executionList.setExpandsOnDoubleClick(False)
        self.isDoubling = False
        self.isUpdating = False
        layout = QtGui.QVBoxLayout()

        self.backButton = QtGui.QPushButton('Go back')
        self.backButton.setToolTip("Go back to parent workflow")
        layout.addWidget(self.backButton)
        self.backButton.hide()

        layout.addWidget(self.legend)
        layout.addWidget(self.executionList)
        self.detailsWidget = QtGui.QTextEdit()
        layout.addWidget(self.detailsWidget)
        self.setLayout(layout)
        self.connect(self.executionList, 
                     QtCore.SIGNAL("itemSelectionChanged()"),
                     self.set_execution)
        self.connect(self.backButton,
                     QtCore.SIGNAL('clicked()'),
                     self.goBack)
#        self.connect(self.executionList, QtCore.SIGNAL(
#         "itemClicked(QTreeWidgetItem *, int)"),
#         self.singleClick)
        self.connect(self.executionList, QtCore.SIGNAL(
         "itemDoubleClicked(QTreeWidgetItem *, int)"),
         self.doubleClick)
        self.addButtonsToToolbar()

    def addButtonsToToolbar(self):
        # Add the open version action
        self.openVersionAction = QtGui.QAction(
            QtGui.QIcon.fromTheme('go-next'),
            'Go to this pipeline', None, triggered=self.openVersion)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.openVersionAction)

    def openVersion(self):
        if not hasattr(self.parentItem, 'item'):
            return
        version = self.parentItem.item.wf_item.parent_version
        from vistrails.gui.vistrails_window import _app
        _app.get_current_view().version_selected(version, True)
        self.controller.recompute_terse_graph()
        _app.get_current_view().version_view.select_current_version()
        _app.get_current_view().version_view.scene().setupScene(self.controller)
        _app.qactions['pipeline'].trigger()

    def execution_updated(self):
        for e in self.controller.log.workflow_execs:
            if e not in self.log:
                self.log[e] = e
                wf_id = e.parent_version
                tagMap = self.controller.vistrail.get_tagMap()
                if wf_id in tagMap:
                    e.db_name = tagMap[wf_id]
                self.executionList.add_workflow_exec(e)
                       
    def set_execution(self):
        item = self.executionList.selectedItems()
        if not item:
            return
        item = item[0]
        if self.isDoubling:
            self.isDoubling = False
            return
        if isinstance(item.wf_item, GroupExec):
            self.backButton.show()
        else:
            self.backButton.hide()
        self.notify_app(item.wf_item, item.execution)

    def notify_app(self, wf_item, execution):
        # make sure it is only called once
        if self.isUpdating:
            return
        self.isUpdating = True
        from vistrails.gui.vistrails_window import _app
        _app.notify("execution_changed", wf_item, execution)
        self.isUpdating = False

    def set_controller(self, controller):
        #print '@@@@ QLogDetails calling set_controller'
        if self.controller == controller:
            return

        self.controller = controller
        self.executionList.controller = self.controller
        if self.controller is not None:
            if not hasattr(self.controller, 'loaded_workflow_execs'):
                self.controller.loaded_workflow_execs = {}
                for e in self.controller.read_log().workflow_execs:
                    # set workflow names
                    e.db_name = controller.get_pipeline_name(e.parent_version)
                    self.controller.loaded_workflow_execs[e] = e
            self.log = self.controller.loaded_workflow_execs
        else:
            self.log = None
        self.executionList.set_log(self.log)

    def execution_changed(self, wf_item, execution):
        if not execution:
            return
        self.execution = execution
        self.parentItem = wf_item
        text = ''
        if hasattr(execution, 'item') and \
           not execution.item == self.executionList.currentItem():
            self.executionList.setCurrentItem(execution.item)
        if hasattr(execution, 'item'):
            text += '%s\n' % execution.item.text(0)
        text += 'Start: %s\n' % execution.ts_start
        text += 'End: %s\n' % execution.ts_end
        if hasattr(execution, 'user'):
            text += 'User: %s\n' % execution.user
        if hasattr(execution, 'cached'):
            text += 'Cached: %s\n' % ("Yes" if execution.cached else 'No')
        if hasattr(execution, 'completed'):
            text += 'Completed: %s\n' % {'0':'No', '1':'Yes'}.get(
                                        str(execution.completed), 'No')
        if hasattr(execution, 'error') and execution.error:
            text += 'Error: %s\n' % execution.error
        annotations = execution.db_annotations \
                      if hasattr(execution, 'db_annotations') else []
        if len(annotations):
            text += '\n\nAnnotations:'
            for annotation in annotations:
                text += "\n  %s: %s" % (annotation.key, annotation.value)
        self.detailsWidget.setText(text)
        self.update_selection()
        
    def singleClick(self, item, col):
        if self.isDoubling:
            self.isDoubling = False
            return
        if isinstance(item.wf_item, GroupExec):
            self.backButton.show()
        else:
            self.backButton.hide()
        self.notify_app(item.wf_item, item.execution)

    def doubleClick(self, item, col):
        # only difference here is that we should show contents of GroupExecs 
        self.isDoubling = True
        if isinstance(item.wf_item, GroupExec):
            self.backButton.show()
        else:
            self.backButton.hide()
        if isinstance(item.execution, GroupExec):
            # use itself as the workflow
            self.notify_app(item.execution, item.execution)
        else:
            self.notify_app(item.wf_item, item.execution)

    def goBack(self):
        if not isinstance(self.parentItem.execution, GroupExec):
            self.backButton.hide()
        self.notify_app(self.parentItem.item.wf_item,
                        self.parentItem)

    def update_selection(self):
        if hasattr(self.execution, 'item') and \
          not self.execution.item.isSelected():
            self.execution.item.setSelected(True)

class QLogView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.setReadOnlyMode(True)
        self.set_title("Provenance")
        self.log = None
        self.execution = None
        self.parentItem = None
        self.isUpdating = False
        # Hook shape selecting functions
        self.connect(self.scene(), QtCore.SIGNAL("moduleSelected"),
                     self.moduleSelected)

    def set_default_layout(self):
        self.set_palette_layout({QtCore.Qt.RightDockWidgetArea: QLogDetails})
            
    def set_action_links(self):
        self.action_links = { }
        
    def set_action_defaults(self):
        self.action_defaults.update(
            {'execute' : [('setEnabled', False, False)],
             'publishWeb': [('setEnabled', False, False)],
             'publishPaper': [('setEnabled', False, False)],
            })

    def notify_app(self, wf_item, execution):
        # make sure it is only called once
        if self.isUpdating:
            return
        self.isUpdating = True
        from vistrails.gui.vistrails_window import _app
        _app.notify("execution_changed", wf_item, execution)
        self.isUpdating = False


    def set_controller(self, controller):
        QPipelineView.set_controller(self, controller)
        if not hasattr(self.controller, 'loaded_workflow_execs'):
            self.controller.loaded_workflow_execs = {}
            for e in self.controller.read_log().workflow_execs:
                # set workflow names
                e.db_name = controller.get_pipeline_name(e.parent_version)
                self.controller.loaded_workflow_execs[e] = e
        self.log = self.controller.loaded_workflow_execs

    def set_to_current(self):
        self.controller.set_pipeline_view(self)

    def version_changed(self):
        pass

    def moduleSelected(self, id, selectedItems):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        """
        if len(selectedItems)!=1 or id==-1:
            if self.execution != self.parentItem.execution:
                self.notify_app(self.parentItem, self.parentItem.execution)
            return

        item = selectedItems[0]
        if hasattr(item,'execution') and item.execution:
            if self.execution != item.execution:
                item = self.scene().selectedItems()[0]
                self.notify_app(self.parentItem, item.execution)
        elif self.execution != self.parentItem.execution:
                self.notify_app(self.parentItem, self.parentItem.execution)

    def set_exec_by_id(self, exec_id):
        if not self.log:
            return False
        try:
            workflow_execs = [e for e in self.log 
                                if e.id == int(str(exec_id))]
        except ValueError:
            return False
        if len(workflow_execs):
            self.notify_app(workflow_execs[0].item, workflow_execs[0])
            return True
        return False

    def set_exec_by_date(self, exec_date):
        if not self.log:
            return False
        workflow_execs = [e for e in self.log
                          if str(e.ts_start) == str(exec_date)]
        if len(workflow_execs):
            self.notify_app(workflow_execs[0].item, workflow_execs[0])
            return True
        return False

    def get_execution_pipeline(self, execution):
        """ Recursively finds pipeline through layers of groupExecs """
        if isinstance(execution, WorkflowExec):
            version = execution.parent_version
            # change the current version to this as well

            return self.controller.vistrail.getPipeline(version)
        if isinstance(execution, GroupExec):
            parent = execution.item.wf_item.execution
            parent_pipeline = self.get_execution_pipeline(parent)
            return parent_pipeline.db_get_module_by_id(
                                   execution.db_module_id).pipeline

    def execution_changed(self, wf_item, execution):
        self.execution = execution
        if self.parentItem != wf_item:
            self.parentItem = wf_item
            self.pipeline = self.get_execution_pipeline(wf_item.execution)
            self.update_pipeline()
        self.update_selection()

    def update_pipeline(self):
        scene = self.scene()
        scene.clearItems()
        self.pipeline.validate(False)
        
        modules = [(e.execution.module_id, e.execution) for e in self.parentItem.modules
                                                   if hasattr(e.execution, 'module_id')]
        modules.reverse()
        module_execs = {}
        for id, m in modules:
            if id not in module_execs:
                module_execs[id] = []
            module_execs[id].append(m)

        # controller = DummyController(self.pipeline)
        scene.controller = self.controller
        self.moduleItems = {}
        for m_id in self.pipeline.modules:
            module = self.pipeline.modules[m_id]
            brush = CurrentTheme.PERSISTENT_MODULE_BRUSH
            if m_id in module_execs:
                e = module_execs[m_id][-1]
                if e.completed == 1:
                    if e.error:
                        brush = CurrentTheme.ERROR_MODULE_BRUSH
                    elif e.cached:
                        brush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                    else:
                        brush = CurrentTheme.SUCCESS_MODULE_BRUSH
                elif e.completed == -2:
                    brush = CurrentTheme.SUSPENDED_MODULE_BRUSH
                else:
                    brush = CurrentTheme.ERROR_MODULE_BRUSH
            module.is_valid = True
            item = scene.addModule(module, brush)
            item.controller = self.controller
            self.moduleItems[m_id] = item
            if m_id in module_execs:
                for e in module_execs[m_id]:
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
        scene.fitToView(self, True)

    def update_selection(self):
        # avoid module update signal
        self.isUpdating = True
        module = None
        if (isinstance(self.execution, ModuleExec) or \
            isinstance(self.execution, GroupExec)) and \
            hasattr(self.execution, 'module') and \
          not self.execution.module.isSelected():
            self.execution.module.setSelected(True)
            module = self.execution.module
        for m in self.scene().selectedItems():
            if m.isSelected() and m != module:
                m.setSelected(False)
        self.isUpdating = False
