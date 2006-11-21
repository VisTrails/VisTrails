""" File qbuilder.py
File for qBuilder class, th PyQt widget that handles
the building of new Vistrails by the user
"""
from OpenGL import GL
from PyQt4 import QtCore, QtGui
from core.utils import unimplemented, VistrailsInternalError, withIndex
from core.debug import DebugPrint
from core.utils import enum
from core.modules.module_registry import registry
from core.vis_action import *
from core.vis_connection import VisConnection
from core.vis_macro import VisMacro
from core.vis_types import VistrailModuleType, VisPort, ModuleFunction
from core.vistrail import Vistrail
from core.xml_parser import XMLParser
from gui.param_explore import ParameterExplorationManager
from gui.pipeline_view import QPipelineView, QQueryView
from gui.qbuildertreewidget import *
from gui.qframebox import *
from gui.qgroupboxscrollarea import *
from gui.qmodulefunctiongroupbox import *
from gui.qt import SignalSet
from gui.version_tree import QVersionTree
from gui.vis_shell import ShellGui
from gui.vistrail_controller import VistrailController, QueryController
import core.system
import core.vis_types
import db.DBconfig
import gui.resources.macroicons_rc
import gui.version_tree_search
import math
import os
import sys
import time

################################################################################

class QBuilder(QtGui.QMainWindow):

    def createMenu(self):
        # first, create all actions
        self.newVistrailAct = QtGui.QAction(self.tr("&New VisTrail"), self)
        self.newVistrailAct.setShortcut(self.tr("Ctrl+N"))
        self.connect(self.newVistrailAct, QtCore.SIGNAL("triggered()"),self.newVistrail)

        self.openVistrailAct = QtGui.QAction(self.tr("&Open VisTrail"), self)
        self.openVistrailAct.setShortcut(self.tr("Ctrl+O"))
        self.connect(self.openVistrailAct, QtCore.SIGNAL("triggered()"),self.guiOpenVistrail)

        self.saveVistrailAct = QtGui.QAction(self.tr("&Save VisTrail"), self)
        self.saveVistrailAct.setShortcut(self.tr("Ctrl+S"))
        self.connect(self.saveVistrailAct, QtCore.SIGNAL("triggered()"),self.saveVistrail)

        self.saveVistrailAsAct = QtGui.QAction(self.tr("&Save VisTrail as..."), self)
        self.saveVistrailAsAct.setShortcut(self.tr("Ctrl+Shift+S"))
        self.connect(self.saveVistrailAsAct, QtCore.SIGNAL("triggered()"),self.saveVistrailAs)

        self.closeVistrailAct = QtGui.QAction(self.tr("Close Vistrail"), self)
        self.closeVistrailAct.setShortcut(self.tr("Ctrl+W"))
        self.connect(self.closeVistrailAct,QtCore.SIGNAL("triggered()"), self.closeVistrail)

        self.quitVistrailsAct = QtGui.QAction(self.tr("Quit"), self)
        self.quitVistrailsAct.setShortcut(self.tr("Ctrl+Q"))
        self.connect(self.quitVistrailsAct,QtCore.SIGNAL("triggered()"), self.quitVistrails)
       
        self.copyAct = QtGui.QAction(self.tr("Copy"), self)
        self.copyAct.setShortcut(self.tr("Ctrl+C"))
        self.connect(self.copyAct,QtCore.SIGNAL("triggered()"), self.copyModules)
        self.copyAct.setEnabled(False)

        self.pasteAct = QtGui.QAction(self.tr("Paste"), self)
        self.pasteAct.setShortcut(self.tr("Ctrl+V"))
        self.connect(self.pasteAct,QtCore.SIGNAL("triggered()"), self.pasteModules)
        self.pasteAct.setEnabled(False)

        self.versionTreeAct = QtGui.QAction(self.tr("View Complete Version Tree"), self)
        self.versionTreeAct.setCheckable(True)
        self.connect(self.versionTreeAct, QtCore.SIGNAL("triggered()"), self.toggleVersionTree)
        
        self.shellAct = QtGui.QAction(self.tr("Open VisTrails Console"), self)
        self.shellAct.setShortcut(self.tr("Ctrl+H"))
        self.connect(self.shellAct, QtCore.SIGNAL("triggered()"), self.showConsole)

        self.resetViewAct = QtGui.QAction(self.tr("Reset View"),self)
        self.resetViewAct.setShortcut(self.tr("Ctrl+R"))
        self.connect(self.resetViewAct, QtCore.SIGNAL("triggered()"), self.resetView)

        self.uploadFilesAct = QtGui.QAction(self.tr("Upload Files..."), self)
        self.connect(self.uploadFilesAct, QtCore.SIGNAL("triggered()"), self.launchUploadApp)

        self.fetchFilesAct = QtGui.QAction(self.tr("Fetch Files..."), self)
        self.connect(self.fetchFilesAct, QtCore.SIGNAL("triggered()"), self.launchFetchApp)

        self.existLoginAct = QtGui.QAction(self.tr("Login..."), self)
        self.connect(self.existLoginAct, QtCore.SIGNAL("triggered()"), self.launchExistLogin)
                
        self.existTransactionAct = QtGui.QAction(self.tr("Fetch Files"), self)
        self.connect(self.existTransactionAct, QtCore.SIGNAL("triggered()"), self.launchExistImport)

        self.existUploadAct = QtGui.QAction(self.tr("Synchronize with eXist"), self)
        self.connect(self.existUploadAct, QtCore.SIGNAL("triggered()"), self.launchExistUpload)
        
        self.existLogoutAct = QtGui.QAction(self.tr("Logout..."), self)
        self.connect(self.existLogoutAct, QtCore.SIGNAL("triggered()"), self.launchExistLogout)

        self.helpAct = QtGui.QAction(self.tr("About VisTrails..."), self)
        self.connect(self.helpAct, QtCore.SIGNAL("triggered()"), self.showAboutMessage)

        # then, create the menu
        fileMenu = self.menuBar().addMenu(self.tr("&File"))
        fileMenu.addAction(self.newVistrailAct)
        fileMenu.addAction(self.openVistrailAct)
        fileMenu.addAction(self.saveVistrailAct)
        fileMenu.addAction(self.saveVistrailAsAct)
        fileMenu.addAction(self.closeVistrailAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitVistrailsAct)

        editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        editMenu.addAction(self.copyAct)
        editMenu.addAction(self.pasteAct)

        remoteMenu = self.menuBar().addMenu(self.tr("&Remote"))
        remoteMenu.addAction(self.uploadFilesAct)
        remoteMenu.addAction(self.fetchFilesAct)

        existMenu = self.menuBar().addMenu(self.tr("e&Xist"))
        existMenu.addAction(self.existLoginAct)
        existMenu.addAction(self.existTransactionAct)
        existMenu.addAction(self.existUploadAct)
        existMenu.addAction(self.existLogoutAct)

        viewMenu = self.menuBar().addMenu(self.tr("View"))
        viewMenu.addAction(self.versionTreeAct)
        viewMenu.addAction(self.shellAct)
        viewMenu.addAction(self.resetViewAct)
        
        helpMenu = self.menuBar().addMenu(self.tr("Help"))
        helpMenu.addAction(self.helpAct)

    def connectPipelineViewSignals(self):
        self.connect(self.pipelineView.shapeEngine, QtCore.SIGNAL("shapeSelected(int)"), self.selectModule)
        self.connect(self.pipelineView.shapeEngine, QtCore.SIGNAL("shapesSelected"), self.setCopyEnabled)
        self.connect(self.pipelineView.shapeEngine, QtCore.SIGNAL("polyLineSelected(int)"), self.selectConnection)
        self.connect(self.pipelineView.shapeEngine, QtCore.SIGNAL("shapeUnselected()"), self.unselect)
        self.connect(self.pipelineView, QtCore.SIGNAL("modulescopied"), self.setPasteEnabled)

    def connectQueryViewSignals(self):
        self.connect(self.queryView.shapeEngine, QtCore.SIGNAL("shapeSelected(int)"), self.selectQueryModule)
        self.queryView.plug(self.queryController)

#     def __del__(self):
#         print "Builder going away..."
#         QtGui.QMainWindow.__del__(self)

    def createDefaultViews(self):
        """Creates the two default views that always exist in a
        builder: the pipeline view and the query view."""
        self.pipelineView = QPipelineView()
        self.queryView = QQueryView()
        self.queryController.setQueryView(self.queryView)
        self.queryView.shapeEngine.setupBackgroundTexture(core.system.visTrailsRootDirectory() + "/gui/resources/images/query_bg.png")
        self.connectPipelineViewSignals()
        self.connectQueryViewSignals()
        self.tabWidget.addTab(self.pipelineView, self.tr("<no collection>"))
        self.tabWidget.addTab(self.queryView, self.tr("<Query canvas>"))

        # Create signal sets for changeView
        ss = SignalSet(self,
                       [(self.searchLineEdit,
                         QtCore.SIGNAL("textChanged(QString)"),
                         self.changeTreeWidget)])
        self.pipelineView.changeViewSignalSet = ss
        self.queryView.changeViewSignalSet = ss

    def __init__( self, parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.currentVersion = -1
        self.pipeline = None
        self.selectedModule = -1
        self.controllers = {}
        self.versionTrees = {}
        self.currentControllerName = ""
        self.shell = None

        self.createMenu()

        f = QtGui.QWidget(self)
        l = QtGui.QHBoxLayout()
        l.setSpacing(0)
        l.setMargin(0)
        f.setLayout(l)
        
        self.setCentralWidget(f)

        splitter = QtGui.QSplitter()
        l.addWidget(splitter)
        splitterleft = QtGui.QWidget()
        splitter.addWidget(splitterleft)
        splitter.setChildrenCollapsible(False)
        l2 = QtGui.QVBoxLayout()
        l2.setSpacing(0)
        l2.setMargin(0)
        splitterleft.setLayout(l2)

        self.executeStackWidget = QtGui.QStackedWidget()
        l2.addWidget(self.executeStackWidget)
        
        self.sendToSpreadsheetBtn = QtGui.QPushButton("Execute workflow")
        self.executeQueryButton = QtGui.QPushButton("Execute query")
        
        self.executeStackWidget.addWidget(self.sendToSpreadsheetBtn)
        self.executeStackWidget.addWidget(self.executeQueryButton)
        
        sp = QtGui.QSizePolicy()
        sp.setHorizontalPolicy(QtGui.QSizePolicy.MinimumExpanding)
        sp.setVerticalPolicy(QtGui.QSizePolicy.Fixed)

        self.sendToSpreadsheetBtn.setSizePolicy(sp)
        self.sendToSpreadsheetBtn.setMinimumSize(100,10)

        self.executeQueryButton.setSizePolicy(sp)
        self.executeQueryButton.setMinimumSize(100,10)

        self.executeStackWidget.setSizePolicy(sp)
        self.executeStackWidget.setMinimumSize(100,10)
        
        self.tabWidget = QtGui.QTabWidget(splitterleft)
        self.tabWidget.previousWidget = None
        self.connect(self.tabWidget,
                     QtCore.SIGNAL("currentChanged(int)"),
                     self.changeView)
        
        l2.addWidget(self.tabWidget)

        # starts panel in the right
        frame = QtGui.QFrame()
        lframe = QtGui.QVBoxLayout()
        lframe.setSpacing(2)
        lframe.setMargin(0)
        frame.setLayout(lframe)
        frame.setLineWidth(1)

        splitter.addWidget(frame)
        
        infoFrame = QtGui.QFrame()
        lInfoFrame = QtGui.QVBoxLayout()
        lInfoFrame.setSpacing(2)
        lInfoFrame.setMargin(0)
        infoFrame.setLayout(lInfoFrame)
        
        self._buildTagFrame(frame)
        self._buildSearchFrame(frame)
        self._buildInfoFrame(infoFrame)


        self.queryController = QueryController(self)
        # This call must be made after self.searchLineEdit has
        # been created
        self.createDefaultViews()
        self.connect(self.executeQueryButton,
                     QtCore.SIGNAL("clicked()"),
                     self.queryController.performQuery)


        
        # This signal set will be passed to all version tree widgets
        ss = SignalSet(self,
                       [(self.searchLineEdit,
                         QtCore.SIGNAL("returnPressed()"),
                         self.versionTreeSearch)
                       ,(self.refineLineEdit,
                        QtCore.SIGNAL("returnPressed()"),
                         self.refineVersionTree)])
        self.versionTreeChangeViewSignalSet = ss

        self.stackWidget = QtGui.QStackedWidget()
        #tab widget for class and method palettes
        frametw = QtGui.QTabWidget()
        self.vtkClassMethodTab = frametw
        lframe.addWidget(self.stackWidget)

        self.stackWidget.addWidget(infoFrame)
        self.stackWidget.addWidget(frametw)

        import gui
        import gui.module_palette
        self.modulePalette = gui.module_palette.ModulePalette(self)
        
        self.moduleTreeWidget = self.modulePalette.buildModulePalette()
        frametw.addTab(self.moduleTreeWidget, "Modules")
        
        import gui.method_palette
        self.moduleMethods = gui.method_palette.ModuleMethods(self)
        frametw.addTab(self.vtkModuleMethods, "Module Methods")

        import gui.module_annotation
        self.moduleMethods = gui.module_annotation.ModuleAnnotations(self)
        frametw.addTab(self.moduleAnnotations, "Module Annotations")

        import gui.log_tab
        self.logTab = gui.log_tab.LogTab(self)
        frametw.addTab(self.logTab, "Log")

        self.bulkChanges = ParameterExplorationManager(self)
        frametw.addTab(self.bulkChanges.buildPalette(), "Parameters Exploration")

        import gui.macro_bar
        self.macroBar = gui.macro_bar.QMacroBar(self)
        frametw.addTab(self.macroBar, "Macros")
        
        self.setWindowTitle("VisTrails - Vistrail Builder")
        framewidth = 1000
        self.resize(framewidth, 600)

        sp = QtGui.QSizePolicy()
        sp.setHorizontalPolicy(QtGui.QSizePolicy.Fixed)
        sp.setVerticalPolicy(QtGui.QSizePolicy.Minimum)
        frame.setSizePolicy(sp)
        frame.setMinimumSize(QtCore.QSize(200,600))
        frame.update()
        splitterleft.setSizePolicy(sp)
        splitterleft.setMinimumSize(QtCore.QSize(200,600))
        splitterleft.resize(QtCore.QSize(framewidth/((math.sqrt(5.0)+1.0)/2.0), 600))
        splitterleft.update()

    def closeAllVistrails(self):
        while len(self.controllers) > 0:
            self.closeVistrail(False)

    def closeEvent(self,e):
        self.quitVistrails()
        
    def quitVistrails(self):
        self.closeAllVistrails()
        QtCore.QCoreApplication.quit()

    def setCurrentController(self, name, controller, versionTree):
        """
        Parameters
        ----------

        - name : 'str'

        - controller : 'VistrailController'

        - versionTree : 'QVersionTree'

        """
        if self.currentControllerName == name:
            return

        self.unselect()
        self.controllers[name] = controller
        if controller.name != name:
            controller.name = name
        self.versionTrees[controller] = versionTree
        if self.currentControllerName:
            v = self.controllers[self.currentControllerName]
            v.consolidatePendingActions()
        else:
            v = None
        controller.versionTree = versionTree
        self._plugToGL(v, controller)
        self._plugToMethodValues(v, controller)

        self.plugController(controller, name)
        
    def plugController(self, controller, name):
        if self.currentControllerName:
           v = self.controllers[self.currentControllerName]
           self.unplugController(v)
        self.currentControllerName = name

        signalSet = [(controller, QtCore.SIGNAL("tagChanged(int, QString)"), self.changeTag)
                    ,(controller, QtCore.SIGNAL("notesChanged(int, QString)"), self.changeNotes)
                    ,(controller, QtCore.SIGNAL("versionWasChanged"), self.selectVersion)
                    ,(self, QtCore.SIGNAL("updateCurrentTag(QString)"), controller.updateCurrentTag)
                    ,(self, QtCore.SIGNAL("updateNotes(QString)"), controller.updateNotes)
                    ,(self.sendToSpreadsheetBtn, QtCore.SIGNAL("clicked()"), controller.sendToSpreadsheet)]


        self.controllerSignalSet = SignalSet(self, signalSet)
        self.controllerSignalSet.plug()
        
        self.emit(QtCore.SIGNAL("controllerChanged"),controller)

    def unplugController(self,controller):
        self.controllerSignalSet.unplug()
        del self.controllerSignalSet

        self.disconnect(self.macroBar,QtCore.SIGNAL("macroRecordingNow"), controller.recordMacro)
        self.currentControllerName = ''
        
    def callSend(self):
        if self.currentControllerName != "":
            self.controllers[self.currentControllerName].sendToSpreadsheet()

    def setUserMethods(self, moduleName, target, localReg=None):
        """
        Parameters
        ----------

        - vtkClass : 'str'
        
        """
        #Clear user methods
        target.clear()

        module = registry.getDescriptorByName(moduleName).module
        allbases = module.mro()[:-1] # skips object

        for basemodule in allbases:
            name = registry.getDescriptor(basemodule).name
            stringList = QtCore.QStringList(QtCore.QString(name))
            moduleWidget = MyQTreeWidgetItem(target, stringList)
            target.setItemExpanded(moduleWidget, True)
            methods = registry.methodPorts(basemodule)
            if localReg and localReg.hasModule(name):
                methods += localReg.methodPorts(basemodule)
            for m in methods:
                sigs = m.getSignatures()
                for sig in sigs:
                    labelList = QtCore.QStringList()
                    labelList << QtCore.QString(m.name)
                    labelList << QtCore.QString(sig)
                    currentMethod = MyQTreeWidgetItem(moduleWidget, labelList)
                    currentMethod.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
                    currentMethod.index = self.vtkMethodPalette.indexFromItem(currentMethod, 0)
        self.vtkMethodPalette.allItems = self.vtkMethodPalette.findItems('',QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)

    def popup(self, message):
        """ Pops up a model dialog.

        Parameters
        ----------

        - message : 'str'

        """
        QtGui.QMessageBox.warning(self,
                                  self.tr("VisTrails"),
                                  self.tr(message))

    def updateTreeWidget(self, treeWidget, text):
        treeWidget.setUpdatesEnabled(False)
        treeWidget.setVisible(False)
        treeWidget.unprotectAllItems()
        if text != "":
            treeWidget.showMatchedItems(text)
        treeWidget.setVisible(True)
        treeWidget.setUpdatesEnabled(True)

    def changeTreeWidget(self, text, tw=None):
        """
        Parameters
        ----------

        - text : 'QtCore.QString'

        - tw : 'QtGui.QTreeWidget'
        
        """
        print 'ha'
        if self.vtkClassMethodTab.currentWidget() == self.moduleTreeWidget:
            self.updateTreeWidget(self.moduleTreeWidget,text)                
        elif self.vtkClassMethodTab.currentWidget() == self.vtkModuleMethods:
            self.updateTreeWidget(self.vtkMethodPalette,text)                
   
    def updateCurrentTag(self):
        """ Right now the user is not allowed to erase tags,
        only to change them
        
        """
        self.emit(QtCore.SIGNAL("updateCurrentTag(QString)"),self.tagNameEdit.text())

    def updateNotes(self):
        self.emit(QtCore.SIGNAL("updateNotes(QString)"),self.notesText.toHtml())

    def selectConnection(self, connId):
        self.emit(QtCore.SIGNAL("connectionSelected(int)"), connId)

    def selectModule(self, moduleId):
        """
        Parameters
        ----------

        - moduleId : 'int'
        
        """
        self.selectedModule = moduleId
        self.moduleAnnotations.resetTable()
#        if not self.vtkClassMethodTab.currentWidget() == self.macroBar:
#            self.vtkClassMethodTab.setCurrentWidget(self.vtkModuleMethods)
        module = self.pipeline.getModuleById(moduleId)
        self.methodValuesArea.setVisModule(module)
        self.setUserMethods(module.name, self.vtkMethodPalette, module.registry)
        self.setUserMethods(module.name, self.vtkParameterExplorationTreeWidget,
                            module.registry)
        self.emit(QtCore.SIGNAL("moduleSelected(int)"), moduleId)
        try:
            controller = self.controllers[self.currentControllerName]
            l = controller.versionTree.search.tupleLength
        except AttributeError:
            return
        if l != 3:
            return
        self.emit(QtCore.SIGNAL("hasLogExecution"), self.currentVersion, moduleId)
        #exec_ids = self.controller.versionTree.search.executionInstances(self.currentVersion, id)
        #print exec_ids

    def selectQueryModule(self, moduleId):
	"""Method to be called whenever a query module has been selected."""
        self.moduleAnnotations.resetTable()
        module = self.queryView.pipeline.getModuleById(moduleId)
        self.methodValuesArea.setVisModule(module)
        self.setUserMethods(module.name, self.vtkMethodPalette, module.registry)
        self.setUserMethods(module.name, self.vtkParameterExplorationTreeWidget, module.registry)
        self.emit(QtCore.SIGNAL("moduleSelected(int)"), moduleId)

    def unselect(self):
        self.selectedModule = -1
        self.moduleAnnotations.resetTable()
        self.methodValuesArea.setVisModule(None)
        self.vtkMethodPalette.clear()
        self.emit(QtCore.SIGNAL("moduleSelected(int)"), -1)
        self.emit(QtCore.SIGNAL("hideLog"))

    def addNewMethod(self, newMethod):
        """
        Parameters
        ----------

        - newMethod : (str, str, str)
        
        """
        lastSelected = self.pipelineView.selectedModule
        lastSelectedModule = self.pipeline.getModuleById(lastSelected)
        customizedPort = registry.getPortConfigureWidgetType(newMethod[0],
                                                             newMethod[1])!=None
        from core.utils import any
        if customizedPort and any([f.name==newMethod[1]
                                    for f in lastSelectedModule.functions]):
            return
        self.emit(QtCore.SIGNAL("methodToBeAdded"), newMethod,lastSelected)
        if self.selectedModule != -1:
            self.unselect()
            self.selectModule(lastSelected)
            vbar = self.methodValuesArea.verticalScrollBar()
            vbar.setValue(vbar.maximum())

    def deleteMethod(self, methodId):
        """
        Parameters
        ----------

        - methodId : 'int'
        
        """
        lastSelected = self.pipelineView.selectedModule
        lastSelectedModule = self.pipeline.getModuleById(lastSelected)
        functionName = lastSelectedModule.functions[methodId]
        if registry.getPortConfigureWidgetType(lastSelectedModule.name,
                                               functionName)!=None:
            for mid in reversed(lastSelectedModule.getNumFunctions()):
                if lastSelectedModule.functions[mid].name==functionName:
                    self.emit(QtCore.SIGNAL("methodToBeDeleted(int, int)"),
                              mid, lastSelected)
        else:            
            self.emit(QtCore.SIGNAL("methodToBeDeleted(int, int)"),
                      methodId, lastSelected)
        if lastSelected != -1:
            self.unselect()
            self.selectModule(lastSelected)
            
    def perform(self, action):
        """
        Parameters
        ----------

        - action : 'VisAction'
        
        """
        action.perform(self.pipeline)

    def changeTag(self, time, message):
        """
        Parameters
        ----------

        - time : 'int'

        - message : 'QtCore.QString'
        
        """
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                 os.path.basename(self.currentControllerName) + " - "+
                                 message)
        self.tagNameEdit.setText(message)
        
    def changeNotes(self, time, message):
        """
        Parameters
        ----------

        - time : 'int'

        - message : 'QtCore.QString'
        
        """
        self.notesText.setHtml(message)

    def changeValues(self, functionId, gb):
        """
        Parameters
        ----------

        - functionId : 'int'

        - gb : 'QModuleFunctionGroupBox'
        
        """
        if self.selectedModule == -1:
            raise VistrailsInternalError("ChangeValues emitted with unselected module!?")

        action = ChangeParameterAction(0,0)

        for i in range(gb.parameterCount()):
            action.addParameter(self.selectedModule, functionId,
                                i, gb.functionName(), gb.name(i),
                                str(gb.value(i)),gb.type(i), gb.alias(i))

        if self.controllers.has_key(self.currentControllerName):
            f = self.controllers[self.currentControllerName]
        else:
            raise VistrailsInternalError("Name '" + self.currentControllerName
                                         + "'  without a controller?")
        self.pipelineView.updateVistrail()
        f.performAction(action)

    def changeView(self, index):
        """ Event handler when the tabwidget with pipeline and version tree emits
        a changeCurrent

        Parameters
        ----------

        - index : 'int'
          current page index
          
        """

        pw = self.tabWidget.previousWidget
        cw = self.tabWidget.currentWidget()
        self.tabWidget.previousWidget = cw

        if pw: pw.changeViewSignalSet.unplug()
        if cw: cw.changeViewSignalSet.plug()

        cw.updateBuilderOnChangeView(self)

    def refineVersionTree(self):
        refineString = self.refineLineEdit.text()
        s = str(refineString)
        if s == "":
            stmt=None
        elif not s:
            stmt = version_tree_search.TrueSearch()
        else:
            try:
                stmt = version_tree_search.SearchCompiler(s).searchStmt
            except version_tree_search.SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Refine Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                stmt = version_tree_search.TrueSearch()
#        for c in self.controllers:
#            self.versionTrees[self.controllers[c]].refine = stmt
        self.versionTrees[self.controllers[self.currentControllerName]].refine=stmt
        self.versionTrees[self.controllers[self.currentControllerName]].setRefineTree()

    def newQuery(self, queryTemplate):
        """Updates vistrail and pipeline views to take into account
        the given query."""
        for (n, c) in self.controllers.iteritems():
            print "template: ", queryTemplate
            q = queryTemplate()
            print "query: ", q
            v = c.vistrail
            q.run(v, n)
            self.versionTrees[c].search = q
        self.versionTrees[self.controllers[self.currentControllerName]].invalidateLayout()
        self.pipelineView.invalidateLayout()

    def versionTreeSearch(self):
        """Updates the version trees by setting the search matcher to the contents
of the search line edit widget."""
        import query
        searchString = self.searchLineEdit.text()
        s = str(searchString)
        d = {'__query1a__': query.Query1a,
             '__query1b__': query.Query1b,
             '__query1c__': query.Query1c,
             '__query2__':  query.Query2,
             '__query3__':  query.Query3,
             '__query4__':  query.Query4,
             '__query5__':  query.Query5,
             '__query6__':  query.Query6,
             '__query8__':  query.Query8,
             '__query9__':  query.Query9 }
        if not s:
            self.newQuery(version_tree_search.TrueSearch)
        elif d.has_key(s):
            self.newQuery(d[s])
        else:
            try:
                stmt = version_tree_search.SearchCompiler(s).searchStmt
            except version_tree_search.SearchParseError, e:
                QtGui.QMessageBox.warning(self,
                                          QtCore.QString("Search Parse Error"),
                                          QtCore.QString(str(e)),
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.NoButton,
                                          QtGui.QMessageBox.NoButton)
                stmt = version_tree_search.TrueSearch()
            self.newQuery(stmt)

    def newVistrail(self):
        count = 1
        vistrailname = ''
        while 1:
            s = "<New" + str(count) + ">"
            if not self.controllers.has_key(s):
                vistrailname = s
                break
            count = count + 1

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                 os.path.basename(vistrailname) + " - no name")

        vistrail = Vistrail()
        controller = VistrailController(vistrail)

        vt = QVersionTree(None, controller)
        vt.changeViewSignalSet = self.versionTreeChangeViewSignalSet

        self.tabWidget.addTab(vt, vistrailname)
        self.setCurrentController(vistrailname, controller, vt)
        self.connect(vt, QtCore.SIGNAL("makeCurrent"),
                     self.makeVersionTreeCurrent)
        self.tabWidget.setCurrentWidget(vt)
        self.selectVersion(0)

    def guiOpenVistrail(self):
        s = QtGui.QFileDialog.getOpenFileName(self,
                                              "Open VisTrail...",
                                              core.system.vistrailsDirectory(),
                                              "Vistrail files (*.xml)")
        self.openVistrail(s)

    def openVistrail(self, s):
        """ Open the vistrail file with name s
            This is to make possible open a vistrail from the console
        """
        if not s:
            return
        if self.controllers.has_key(str(s)):
            return
        parser = XMLParser()
        parser.openVistrail(str(s))
        vistrail = parser.getVistrail()

        controller = VistrailController(vistrail, str(s))

        vt = QVersionTree(None, controller)
        vt.changeViewSignalSet = self.versionTreeChangeViewSignalSet

        self.tabWidget.addTab(vt, os.path.basename(str(s)))
        self.setCurrentController(str(s), controller, vt)
        self.connect(vt, QtCore.SIGNAL("makeCurrent"),
                     self.makeVersionTreeCurrent)
        self.tabWidget.setCurrentWidget(vt)
    
    def closeVistrail(self, showCancelButton=True):
        if self.currentControllerName == "":
            return
        #remove tabs
        if not self.controllers.has_key(self.currentControllerName):
                raise VistrailsInternalError("Name '" + self.currentControllerName
                                         + "' does not have a controller!")
        close = True
        controller = self.controllers[self.currentControllerName]
        controller.consolidatePendingActions()
        if controller.vistrail.changed:
            text = "Vistrail " + QtCore.Qt.escape(self.currentControllerName) + " contains unsaved changes.\n Do you want to save changes before closing it?"
            if showCancelButton:
                res = QtGui.QMessageBox.information(None,
                                          self.tr("Vistrails"),
                                          text, 
                                          self.tr("&Save"), 
                                          self.tr("&Discard"),
                                          self.tr("Cancel"),
                                          0,
                                          2)
            else:
                res = QtGui.QMessageBox.information(None,
                                          self.tr("Vistrails"),
                                          text, 
                                          self.tr("&Save"), 
                                          self.tr("&Discard"),
                                          "",
                                          0,
                                          1)
            if res == 0:
                self.saveVistrail()
                controller = self.controllers[self.currentControllerName]
                close = True
            elif res == 1:
                close = True
            else:
                close = False
        oldname = self.currentControllerName
        if close:
            vt = self.versionTrees[controller]
            del self.versionTrees[controller]
            if len(self.versionTrees) == 0:
                self.unplugController(controller)
                self.tabWidget.removeTab(self.tabWidget.currentIndex())
                self.tabWidget.removeTab(self.tabWidget.currentIndex())
                self.tabWidget.removeTab(self.tabWidget.currentIndex())
                self.createDefaultViews()
            else:
                def getFirstVersionTreeIndex():
                    p = self.tabWidget.currentIndex()
                    result = self.tabWidget.widget(p)
                    while result == self.pipelineView or result == self.queryView:
                        p += 1
                        result = self.tabWidget.widget(p)
                    return p
                
                self.tabWidget.removeTab(getFirstVersionTreeIndex())
                p = getFirstVersionTreeIndex()
                new_vt = self.tabWidget.widget(p)
                print new_vt
                controller = new_vt.controller
                self.makeVersionTreeCurrent(new_vt)
                self.selectVersion(controller.currentVersion)
            vt.signalSet.unplug()
        del self.controllers[oldname]
        
    def saveVistrail(self):
        self.pipelineView.updateVistrail()
        if self.currentControllerName == "":
            return
        if self.currentControllerName[0:4] == '<New':
            self.saveVistrailAs()
        else:
            if not self.controllers.has_key(self.currentControllerName):
                raise VistrailsInternalError("Name '" + self.currentControllerName
                                         + "' does not have a controller!")
            controller = self.controllers[self.currentControllerName]
            vistrail = controller.vistrail
            vistrail.serialize(self.currentControllerName)

    def saveVistrailAs(self):
        self.pipelineView.updateVistrail()
        if not self.currentControllerName:
            return

        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save Vistrail As..",
                                                     core.system.vistrailsDirectory(),
                                                     "XML files (*.xml)")
        if not fileName:
            return

        if not self.controllers.has_key(self.currentControllerName):
            raise VistrailsInternalError("Name '" + self.currentControllerName
                                         + "' does not have a controller!")

        controller = self.controllers[self.currentControllerName]

        del self.controllers[self.currentControllerName]
        self.currentControllerName = str(fileName)
        controller.name = str(fileName)
        self.controllers[self.currentControllerName] = controller
        vistrail = controller.vistrail
        versionTree = self.versionTrees[controller]
        vistrail.serialize(self.currentControllerName)

        if vistrail.hasTag(self.currentVersion):
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                     os.path.basename(self.currentControllerName) + " - "+
                                     vistrail.inverseTagMap[self.currentVersion])
        else:
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                     os.path.basename(self.currentControllerName) +
                                     " - no name")
        self.tabWidget.setTabText(self.tabWidget.indexOf(versionTree),
                                 os.path.basename(self.currentControllerName))

    def selectVersion(self, version, quiet=False):
        """
        Parameters
        ----------

        - version : 'int'
        
        """
        if quiet:
            self.currentVersion = version
            return

        if not self.controllers.has_key(self.currentControllerName):
            raise VistrailsInternalError("Name '" + self.currentControllerName
                                         + "' does not have a controller!")
        if version == self.currentVersion:
            return
        controller = self.controllers[self.currentControllerName]
        vistrail = controller.vistrail
        self.pipeline = controller.currentPipeline
        #clear bulk change area
        self.bulkChanges.clear()
        self.currentVersion = version
        self.pipelineView.setCurrent(vistrail, version, self.pipeline)
        self.pipelineView.setAcceptDrops(True)
        if vistrail.hasTag(version):
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                     os.path.basename(self.currentControllerName) + " - "+
                                     vistrail.inverseTagMap[version])
            self.tagNameEdit.setText(vistrail.inverseTagMap[version])
        else:
           self.tabWidget.setTabText(self.tabWidget.indexOf(self.pipelineView),
                                     os.path.basename(self.currentControllerName) +
                                     " - no name")
        if vistrail.actionMap.has_key(version):
            username = vistrail.actionMap[version].user
            date = vistrail.actionMap[version].date
            notes = vistrail.actionMap[version].notes
            self.showVersionInfo(username,date,notes)

    def showVersionInfo(self, username, date, notes):
        """ Shows version info in the GUI

        Parameters
        ----------

        - username: 'str'
        - date: 'str'
        - note: 'str'
        
        """
        if username == None:
            username = "<unknown>"
        if date == None:
            date = "<unknown>"
            
        self.userText.setText(self.tr("User: " + username))
        self.dateText.setText(self.tr("Date: "+ date))
        if notes != None:
            self.notesText.setHtml(self.tr(notes))
        else:
            self.notesText.clear()

    def makeVersionTreeCurrent(self, tree):
        """
        Parameters
        ----------

        - tree : 'QVersionTree'
        
        """
        viscon = None
        for (vc,vt) in self.versionTrees.items():
            if tree == vt:
                viscon = vc
                break
        if not viscon:
            raise VistrailsInternalError("Version Tree without a controller?")

        name = None
        for (s,vc) in self.controllers.items():
            if viscon == vc:
                name = s
                break
        if not name:
            raise VistrailsInternalError("Vistrail Controller without a name?")

        self.setCurrentController(name,viscon,tree)

    def toggleVersionTree(self):
        if self.versionTreeAct.isChecked():
            for c in self.controllers.values():
                self.versionTrees[c].setCompleteTree()
        else:
            for c in self.controllers.values():
                self.versionTrees[c].setTerseTree()

    def copyModules(self):
        self.tabWidget.currentWidget().copySel()
            
    def pasteModules(self):
        self.tabWidget.currentWidget().paste()

    def launchUploadApp(self):
        # As this window blocks according to I/O operations, we have to put it in a different thread/process.
        from remote import RemoteRep
        from gui.vis_application import VistrailsApplication
        remote = RemoteRep(VistrailsApplication.configuration.fileRepository,'Upload')

    def launchFetchApp(self):
        # As this window blocks according to I/O operations, we have to put it in a different thread/process.
        from remote import RemoteRep
        from gui.vis_application import VistrailsApplication
        remote = RemoteRep(VistrailsApplication.configuration.fileRepository,'Fetch')

    def showConsole(self):
        if not self.shell:
            self.shell = ShellGui(self,self)
        self.shell.show()

    def resetView(self):
        if self.tabWidget.currentWidget() == self.pipelineView:
            self.pipelineView.resetCamera()
        else:
            controller = self.controllers[self.currentControllerName]
            vt = self.versionTrees[controller]
            vt.resetCamera()

    def launchExistLogin(self):
        from login import Ui_Login
        window = Ui_Login()
        window.exec_()

    def launchExistLogout(self):
        from logout import Ui_Logout
        window = Ui_Logout()
        window.exec_()

    def launchExistImport(self):
        from GetFile import Ui_ImportFile
        window = Ui_ImportFile()
        window.exec_()
        if window.writeFile == 0:
                f = file("tmp.xml", "w")
                f.write(window.content)
                f.close()
                parser = XMLParser()
                parser.openVistrail("tmp.xml")
                vistrail = parser.getVistrail()

                controller = VistrailController(vistrail)

                vt = QVersionTree(None, controller)

                self.tabWidget.addTab(vt, os.path.basename(window.name))
                self.setCurrentController(window.name, controller, vt)
                self.connect(vt, QtCore.SIGNAL("makeCurrent"),
                     self.makeVersionTreeCurrent)

    def launchExistUpload(self):
        from xMerge import existMerge
        merger = existMerge()
        nvt = merger.synchronize(self.currentControllerName)

        controller = self.controllers[self.currentControllerName]
        controller.vistrail = nvt
        controller.currentVersion = 0

        vt = self.versionTrees[controller]
        vt.invalidateLayout()

    def setCopyEnabled(self, value):
        self.copyAct.setEnabled(value)

    def setPasteEnabled(self):
        self.pasteAct.setEnabled(True)

    def getLargestTimestep(self, vt1, vt2):
        #  Here, we go through the supplied vistrail and grab the largest timestamp
        timestamp = vt1.getLastCommonVersion(vt2)
        return timestamp

    def showAboutMessage(self):
        QtGui.QMessageBox.about(self,self.tr("About VisTrails..."),
                                self.tr(core.system.aboutString()))

    def _buildTagFrame(self, parent):
        """
        Parameters
        ----------

        - parent : 'QtGui.QWidget'
        
        """
        tagFrame = QtGui.QFrame(parent)
#        tagFrame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        tagFrame.setLineWidth(1)

        tagLayout = QtGui.QHBoxLayout()
        tagLayout.setSpacing(2)
        tagLayout.setMargin(2)
        tagLabel = QtGui.QLabel(self.tr("Visualization Name:"), tagFrame)
        self.tagNameEdit = QtGui.QLineEdit(tagFrame)

        self.connect(self.tagNameEdit, QtCore.SIGNAL("returnPressed()"),
                     self.updateCurrentTag)

        self.setTagName = QtGui.QPushButton("Change", tagFrame)
        
        tagLayout.addWidget(tagLabel)
        tagLayout.addWidget(self.tagNameEdit)
        tagLayout.addWidget(self.setTagName)
        
        self.connect(self.setTagName, QtCore.SIGNAL("clicked()"),
                self.updateCurrentTag)

        tagFrame.setLayout(tagLayout)

        if parent.layout():
            parent.layout().addWidget(tagFrame)

    def _buildSearchFrame(self, parent):
        """
        Parameters
        ----------

        - parent : 'QtGui.QWidget'
        
        """
        searchFrame = QtGui.QFrame(parent)
#        searchFrame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)


        allLayout = QtGui.QVBoxLayout()
        allLayout.setSpacing(2)
        allLayout.setMargin(2)

        searchFrame.setLineWidth(1)
        
        searchLayout = QtGui.QHBoxLayout()
        searchLayout.setSpacing(2)
        searchLayout.setMargin(2)
        refineLayout = QtGui.QHBoxLayout()
        refineLayout.setSpacing(2)
        refineLayout.setMargin(2)
     
        refineLabel = QtGui.QLabel("Refine:", searchFrame)
        self.refineLineEdit = QtGui.QLineEdit(searchFrame)

        searchLabel = QtGui.QLabel("Search:", searchFrame)
        self.searchLineEdit = QtGui.QLineEdit(searchFrame)
        
        refineLayout.addWidget(refineLabel)
        refineLayout.addWidget(self.refineLineEdit)
        
        searchLayout.addWidget(searchLabel)
        searchLayout.addWidget(self.searchLineEdit)
        
        allLayout.addLayout(refineLayout)
        allLayout.addLayout(searchLayout)

        searchFrame.setLayout(allLayout)
        if parent.layout():
            parent.layout().addWidget(searchFrame)

    def _buildInfoFrame(self, parent):

        self.userText = QtGui.QLabel("User: ")
       
        vlayout = QtGui.QVBoxLayout()

        vlayout.addWidget(self.userText,0,QtCore.Qt.AlignLeft)
        vlayout.setSpacing(3)
        vlayout.setMargin(2)

        self.dateText = QtGui.QLabel("Date: ")
        
        vlayout.addWidget(self.dateText,0,QtCore.Qt.AlignLeft)

        lAnnotation = QtGui.QLabel("Notes")
        
        self.notesText = QNotesEdit()
        self.connect(self.notesText, QtCore.SIGNAL("needToSave()"),
                     self.updateNotes)
       

        vlayout.addWidget(lAnnotation)
        vlayout.addWidget(self.notesText)

        if parent:
            if parent.layout():
                parent.layout().addLayout(vlayout)
            else:
                parent.setLayout(vlayout)
        
    def addNewRange(*x):
        pass
    
    def deleteRange(*x):
        pass
    
    def changeRanges(*x):
        pass

    def _plugToGL(self, old_controller, new_controller):
        """
        Parameters
        ----------

        - old_controller : 'VistrailController'

        - new_controller : 'VistrailController'
        
        """
        if old_controller:
            self.pipelineView.unplug(old_controller)
        if new_controller:
            self.pipelineView.plug(new_controller)

    def _plugToMethodValues(self, old_controller, new_controller):
        """
        Parameters
        ----------

        - old_controller : 'VistrailController'

        - new_controller : 'VistrailController'
        
        """
        if old_controller:
            self.disconnect(self, QtCore.SIGNAL("methodToBeAdded"),
                            old_controller.addMethod)
            self.disconnect(self, QtCore.SIGNAL("methodToBeDeleted(int, int)"),
                            old_controller.deleteMethod)
            
        self.connect(self, QtCore.SIGNAL("methodToBeAdded"),
                     new_controller.addMethod)
        self.connect(self, QtCore.SIGNAL("methodToBeDeleted(int, int)"),
                     new_controller.deleteMethod)
    
class QNotesEdit(QtGui.QTextEdit):
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAcceptRichText(True)
        
    def focusOutEvent(self, event):
        self.emit(QtCore.SIGNAL("needToSave()"))
        QtGui.QTextEdit.focusOutEvent(self,event)
