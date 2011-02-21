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
from gui.pipeline_view import QPipelineView
from gui.theme import CurrentTheme
from core import system, debug
import core.db.io

################################################################################

class QExecutionInspector(QtGui.QWidget):
    """
    QExecutionInspector is a widget acting as an inspector vistrail modules
    in diff mode. It consists of a function inspector and annotation
    inspector
    
    """
    def __init__(self, parent=None, execution=None, f=QtCore.Qt.WindowFlags()):
        """ QParamInspector(parent: QWidget, f: WindowFlags)
                            -> QParamInspector
        Construct a widget containing tabs: Functions and Annotations,
        each of them is in turn a table of two columns for two
        corresponding versions.
        
        """
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.Tool )
        self.setWindowTitle('Execution Inspector')
        self.firstTime = True
        self.myLayout = QtGui.QVBoxLayout()
        self.setLayout(self.myLayout)
        self.infoList = QtGui.QListWidget()
        self.infoList.setWrapping(True)
        self.infoList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.myLayout.addWidget(self.infoList)
        if execution:
            self.setDetails(execution)
        else:
            self.clear()
        self.adjustSize()
        self.hide()

    def clear(self):
        self.infoList.clear()
        self.infoList.addItem("None selected")

    def setDetails(self, execution):
        self.infoList.clear()
        import api
        api.e = execution
        startTime = execution.ts_start
        if startTime:
            self.infoList.addItem("Start time: %s" % startTime)
        endTime = execution.ts_end
        if endTime:
            self.infoList.addItem("End time: %s" % endTime)

        error = execution.error
        if error:
            self.infoList.addItem("Error: %s" % error)

        annotations = execution.db_annotations
        if len(annotations):
            self.infoList.addItem('')
            self.infoList.addItem("Annotations:")
            for annotation in annotations:
                self.infoList.addItem("%s: %s" % (annotation.key,annotation.value))
        loop_execs = execution.db_loop_execs
        if len(loop_execs):
            self.infoList.addItem('')
            self.infoList.addItem("Loop executions:")
            for e in loop_execs:
                self.infoList.addItem("Loop %s" % e.db_id)
                startTime = e.ts_start
                if startTime:
                    self.infoList.addItem("    Start time: %s" % startTime)
                endTime = e.ts_end
                if endTime:
                    self.infoList.addItem("    End time: %s" % endTime)
                error = e.error
                if error:
                    self.infoList.addItem("Error: %s" % error)
    
    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None        
        Doesn't allow the QParamInspector widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.parent().showInspectorAction.setChecked(False)

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
        

class QLegendWindow(QtGui.QWidget):
    """
    QLegendWindow contains a list of QLegendBox and its description
    
    """
    def __init__(self, parent='', f=QtCore.Qt.WindowFlags()):
        """ QLegendWindow(parent: QWidget, f: WindowFlags)
                          -> QLegendWindow
        Construct a window by default with 3 QLegendBox and 3 QLabels
        
        """
        QtGui.QWidget.__init__(self, parent,
                               f | QtCore.Qt.Tool )
        self.setWindowTitle('Visual Log Legend')
        self.firstTime = True
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.setFont(CurrentTheme.VISUAL_DIFF_LEGEND_FONT)
        
        data = [[0, "Successful execution",CurrentTheme.SUCCESS_MODULE_BRUSH],
                [1, "Failed execution",      CurrentTheme.ERROR_MODULE_BRUSH],
                [2, "Not executed",     CurrentTheme.PERSISTENT_MODULE_BRUSH],
                [3, "Cached",         CurrentTheme.NOT_EXECUTED_MODULE_BRUSH]]
        
        for n, text, brush in data:         
            self.gridLayout.addWidget(
                QLegendBox(brush, CurrentTheme.VISUAL_DIFF_LEGEND_SIZE, self),
                n, 0)
            self.gridLayout.addWidget(QtGui.QLabel(text, self), n, 1)

        self.adjustSize()
        
    def closeEvent(self,e):
        """ closeEvent(e: QCloseEvent) -> None
        Doesn't allow the Legend widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.parent().showLegendsAction.setChecked(False)
        

class QVisualLog(QtGui.QMainWindow):
    """
    QVisualLog is a main widget for Visual Log containing a GL
    Widget to draw the pipeline
    
    """
    def __init__(self, vistrail, v, execution,
                 parent=None, f=QtCore.Qt.WindowFlags()):
        """ QVisualLog(vistrail: Vistrail, v: str, execution: DBExecution
                        parent: QWidget, f: WindowFlags) -> QVisualLog
        Initialize with all
        
        """
        # Set up the version name correctly
        vName = vistrail.getVersionName(v)
        if not vName: vName = 'Version %d' % v

        self.execution = execution
        self.pipeline = vistrail.getPipeline(v)
        self.v_name = vName
        self.v = v

        # Create the top-level Visual Diff window
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Execution of "%s" starting at %s' % (vName, execution.db_ts_start))
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.createPipelineView()
        self.createToolBar()
        self.createToolWindows()

        self.installEventFilter(self)
        self.center()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, 
        (screen.height()-size.height())/2)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.ShortcutOverride and \
                event.key() == QtCore.Qt.Key_W and \
                event.modifiers() == QtCore.Qt.ControlModifier:
            event.accept()
            self.close()
        return QtGui.QMainWindow.eventFilter(self, object, event)

    def closeEvent(self, event):
        self.inspectorWindow.close()
        self.legendWindow.close()

    def createPipelineView(self):
        """ createPipelineView() -> None        
        Create a center pipeline view for Visual Log and setup the
        view based on the log
        
        """
        # Initialize the shape engine
        self.pipelineView = QPipelineView()
        self.setCentralWidget(self.pipelineView)

        # Add all the shapes into the view
        self.createLogPipeline()

        # Hook shape selecting functions
        self.connect(self.pipelineView.scene(), QtCore.SIGNAL("moduleSelected"),
                     self.moduleSelected)

    def createToolBar(self):
        """ createToolBar() -> None        
        Create the default toolbar of Visual Log window with two
        buttons to toggle the Parameter Inspector and Legend window
        
        """
        # Initialize the Visual Log toolbar
        self.toolBar = self.addToolBar('Visual Log Toolbar')
        self.toolBar.setMovable(False)

        # Add the Show Legend window action
        self.showLegendsAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_SHOW_LEGEND_ICON,
            'Show Legends')
        self.showLegendsAction.setCheckable(True)
        self.connect(self.showLegendsAction, QtCore.SIGNAL("toggled(bool)"),
                     self.toggleShowLegend)

        self.showInspectorAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_SHOW_LEGEND_ICON,
            'Show Inspector')
        self.showInspectorAction.setCheckable(True)
        self.connect(self.showInspectorAction, QtCore.SIGNAL("toggled(bool)"),
                     self.toggleShowInspector)

        # Add the show details action
        self.showDetailsAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_CREATE_ANALOGY_ICON,
            'Show details')
        self.showDetailsAction.setCheckable(True)
        self.connect(self.showDetailsAction, QtCore.SIGNAL("triggered()"),
                     self.toggleShowDetails)

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

    def toggleShowLegend(self):
        """ toggleShowLegend() -> None
        Show/Hide the legend window when toggle this button
        
        """
        if self.legendWindow.firstTime:
            self.legendWindow.move(self.pos().x()+self.frameSize().width()-
                                   self.legendWindow.frameSize().width(),
                                   self.pos().y())
        self.legendWindow.setVisible(self.showLegendsAction.isChecked())
        if self.legendWindow.firstTime:
            self.legendWindow.firstTime = False
            self.legendWindow.setFixedSize(self.legendWindow.size())            

    def toggleShowInspector(self):
        """ toggleShowInspector() -> None
        Show/Hide the inspector window when toggle this button
        
        """
        if self.inspectorWindow.firstTime:
            self.inspectorWindow.move(self.pos().x()+self.frameSize().width()-
                                   self.inspectorWindow.frameSize().width(),
                                   self.pos().y())
        self.inspectorWindow.setVisible(self.showInspectorAction.isChecked())
        if self.inspectorWindow.firstTime:
            self.inspectorWindow.firstTime = False
            self.inspectorWindow.setMinimumSize(300, 200)
            self.inspectorWindow.adjustSize()

    def createToolWindows(self):
        """ createToolWindows() -> None
        Create Inspector and Legend window

        """
        self.inspectorWindow = QExecutionInspector(self)
        self.legendWindow = QLegendWindow(self)

    def moduleSelected(self, id, selectedItems):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        When the user click on a module, display its parameter changes
        in the Inspector
        
        """
        if len(selectedItems)!=1 or id==-1:
            self.moduleUnselected()
            return
        if selectedItems[0].execution:
            self.inspectorWindow.setDetails(selectedItems[0].execution)


    def moduleUnselected(self):
        """ moduleUnselected() -> None
        When a user selects nothing, make sure to display nothing as well
        
        """
        self.inspectorWindow.clear()
                    
    def createLogPipeline(self):
        """ createLogPipeline() -> None
        Actually walk through the self.log result and add all modules
        into the pipeline view
        
        """

        scene = self.pipelineView.scene()
        scene.clearItems()
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
                
        module_execs = dict([(e.db_module_id, e) \
                             for e in self.execution.db_get_item_execs()])
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
                # add text to scene
            module.is_valid = True
            item = scene.addModule(module, brush)
            item.controller = controller
            self.moduleItems[m_id] = item
            if m_id in module_execs:
                item.execution = module_execs[m_id]
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
