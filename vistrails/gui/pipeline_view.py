from PyQt4 import QtCore, QtGui
from core.common import *
from core.data_structures import *
from core.debug import notify, DebugPrint, timecall
from core.vis_action import *
from core.vis_object import VisModule
from core.vis_types import *
from core.vistrail import Vistrail
from core.xml_utils import *
from gui.builder_utils import *
from gui.qt import SignalSet
from gui.shape import PolyLine, ModuleShape, PortShape
from gui.shape_engine import GLWidget
import core.system
import os
import threading

class QPipelineView(QtGui.QScrollArea):
    def __init__(self, parent=None):
        """
        Parameters
        ----------
        
        - parent = 'QtGui.QWidget'
        """
        QtGui.QScrollArea.__init__(self,parent)
        self.pipeline = None
        self.currentVistrail = None
        self.currentVersion = 0
        self.shapeEngine = GLWidget()
#        print "pipeline_view's shapeEngine:", self.shapeEngine
        texPath = core.system.visTrailsRootDirectory() + "/gui/resources/images/pipeline_bg.png"
        self.shapeEngine.setupBackgroundTexture(texPath)
        self.shapeEngine.lineWidth = 2.0
        self.shapeEngine.panZ = 0.25
        self.shapeEngine.pipelineView = self
        self.setWidget(self.shapeEngine)
        self.setWidgetResizable(True)
        self.selectedModule = -1
        self.setAcceptDrops(True)
        self.shapeEngine.setAcceptDrops(True)
        self.moveAction = MoveModuleAction()
        signalList = [(self.shapeEngine, QtCore.SIGNAL("shapeSelected(int)"), self.moduleSelected)
                      ,(self.shapeEngine, QtCore.SIGNAL("shapeUnselected()"), self.moduleUnselected)
                      ,(self.shapeEngine, QtCore.SIGNAL("shapesMove"), self.modulesMove)
                      ,(self.shapeEngine, QtCore.SIGNAL("connectionToBeAdded"), self.addConnection)
                      ,(self.shapeEngine, QtCore.SIGNAL("ctrlClick()"), self.multiPick)
                      ,(self.shapeEngine, QtCore.SIGNAL("rightClick"), self.rClickMenu)
                      ,(self.shapeEngine, QtCore.SIGNAL("doubleClick"), self.handleDoubleClick)]
        self.shapeEngineSignalSet = SignalSet(self, signalList)
        self.shapeEngineSignalSet.plug()
	self.draw()
        self.lock = threading.Lock()
        self.controller = None
	self.canPaste = False

    def updateBuilderOnChangeView(self, builder):
        """updateBuilderOnChangeView(self, builder) -> None.

        Shows the stack that is appropriate for a pipeline view on builder's
        stack widget, and disallows editing of refine lineEdit.

        (updateBuilderOnChangeView gets called whenever this widget becomes
        visible on the builder's tabWidget.)"""
        builder.stackWidget.setCurrentIndex(1)
        builder.refineLineEdit.setReadOnly(True)
        builder.executeStackWidget.setCurrentIndex(0)
        
    def draw(self):
        if (self.isVisible()):
	    self.shapeEngine.updateGL()

    def invalidateLayout(self):
        if self.pipeline:
            self.setPipeline(self.pipeline)

    def setPipeline(self, pipeline):
        self.shapeEngine.clearShapes()
        stmt = self.controller.versionTree.search
        scale = 200.0
        centerX = 0.0
        centerY = 0.0
        minX = 1.0e20
        minY = 1.0e20
        maxX = -1.0e20
        maxY = -1.0e20
        for (id,m) in pipeline.modules.items():
            for c in pipeline.connections.itervalues():
                if c.source.moduleId==m.id:
                    m.portVisible.add(c.source.name)
                if c.destination.moduleId==m.id:
                    m.portVisible.add(c.destination.name)
            self.shapeEngine.addModuleShape(m,matched=stmt.matchModule(self.currentVersion, m))
#             self.shapeEngine.addModuleShape(m)
            centerX+=m.center.x
            centerY+=m.center.y
            if (m.center.x > maxX): maxX = m.center.x
            if (m.center.y > maxY): maxY = m.center.y
            if (m.center.x < minX): minX = m.center.x
            if (m.center.y < minY): minY = m.center.y
        if len(pipeline.modules.items()) > 1:
            centerX/=len(pipeline.modules.items())
            centerY/=len(pipeline.modules.items())
            w = maxX-minX
            h = maxY-minY
            scale = max(w,h)
        if (self.pipeline == None):
            self.shapeEngine.panX = centerX
            self.shapeEngine.panY = centerY
            self.shapeEngine.panZ = 1.0/scale
            self.shapeEngine.scale = scale
        self.shapeEngine.setPortConnections(pipeline.connections)
        self.pipeline = pipeline
        
    def updateVistrail(self):
        """ Updates Vistrail with pending move actions. """
        if len(self.moveAction.moves):
            self.emit(QtCore.SIGNAL("actionToBePerformed"), self.moveAction)
            self.moveAction = MoveModuleAction()

    def setCurrent(self, vistrail=None, version=0, pipeline=None):
        self.currentVistrail = vistrail
        self.currentVersion = version
        if pipeline != None:
            self.setPipeline(pipeline)
        else:
            self.shapeEngine.clearShapes()
        self.draw()

    def plug(self, controller):
        tripleList = [(self.shapeEngine, QtCore.SIGNAL("moduleToBeAdded"), controller.addModule)
                      ,(self.shapeEngine, QtCore.SIGNAL("moduleToBeDeleted(int)"), controller.deleteModule)
                      ,(self.shapeEngine, QtCore.SIGNAL("modulesToBeDeleted"), controller.deleteModuleList)
                      ,(self.shapeEngine, QtCore.SIGNAL("connectionToBeDeleted(int)"), controller.deleteConnection)
                      ,(self.shapeEngine, QtCore.SIGNAL("connectionsToBeDeleted"), controller.deleteConnectionList)
                      ,(self, QtCore.SIGNAL("connectionToBeAdded"), controller.addConnection)
                      ,(self, QtCore.SIGNAL("actionToBePerformed"), controller.performAction)
                      ,(controller, QtCore.SIGNAL("actedOnCurrentVistrail(VisAction)"), self.perform)
                      ,(controller, QtCore.SIGNAL("flushPendingActions()"), self.updateVistrail)
                      ,(self, QtCore.SIGNAL("updateGL"), self.shapeEngine.updateGL)
                      ,(self, QtCore.SIGNAL("copyAndPaste"), controller.pasteModulesAndConnections)]
        self.plugSignalSet = SignalSet(self, tripleList)
        self.plugSignalSet.plug()
	controller.currentPipelineView = self
        self.controller = controller

    def unplug(self, controller):
        controller.currentPipelineView = None
        self.controller = None

        self.plugSignalSet.unplug()
        del self.plugSignalSet

    def perform(self, action=None):
        action.perform(self.pipeline)
        self.currentVersion = action.timestep
        self.update()

    def moduleSelected(self, id):
        self.selectedModule = id

    def moduleUnselected(self):
        self.selectedModule = -1

    def modulesMove(self, dict):
	for (id,point) in dict.items():
	    self.moveAction.addMove(id, point.x, point.y)

    def addConnection(self, conn):
        conn.id = self.pipeline.freshConnectionId()
        self.emit(QtCore.SIGNAL("connectionToBeAdded"), conn)
    
    def showEvent(self, event):
        self.shapeEngine.updateGL()

    def setModuleActive(self, id):
        self.lock.acquire()
        try:
            self.shapeEngine.shapes[id].setActive()
            self.emit(QtCore.SIGNAL("updateGL"))
        finally:
            self.lock.release()

    def setModuleComputing(self, id):
        self.lock.acquire()
        try:
            self.shapeEngine.shapes[id].setComputing()
            self.emit(QtCore.SIGNAL("updateGL"))
        finally:
            self.lock.release()

    def setModuleError(self, id, error):
        self.lock.acquire()
        try:
            self.shapeEngine.shapes[id].setError(error)
            self.emit(QtCore.SIGNAL("updateGL"))
        finally:
            self.lock.release()

    def setModuleSuccess(self, id):
        self.lock.acquire()
        try:
            self.shapeEngine.shapes[id].setSuccess()
            self.emit(QtCore.SIGNAL("updateGL"))
        finally:
            self.lock.release()

    def setModuleNotExecuted(self, id):
        self.lock.acquire()
        try:
            self.shapeEngine.shapes[id].setNotExecuted()
            self.emit(QtCore.SIGNAL("updateGL"))
        finally:
            self.lock.release()

    def multiPick(self):
        if self.shapeEngine.currentShape:
            if not isinstance(self.shapeEngine.currentShape,PolyLine):
                if self.shapeEngine.currentShape not in self.shapeEngine.selectedShapes:
                    self.shapeEngine.selectedShapes.append(self.shapeEngine.currentShape)
                else:
                    self.shapeEngine.selectedShapes.remove(self.shapeEngine.currentShape)
                    self.shapeEngine.currentShape.setSelected(False)
            else:
                self.shapeEngine.currentShape.setSelected(False)

    def rClickMenu(self, event):
        menu = QtGui.QMenu()
        copyAct = QtGui.QAction(self.tr("Copy"),self)
        pasteAct = QtGui.QAction(self.tr("Paste"),self)
	upstreamAct = QtGui.QAction(self.tr("Select upstream"),self)
	if len(self.shapeEngine.selectedShapes) < 1:
	    copyAct.setEnabled(False)
	    upstreamAct.setEnabled(False)
	pasteAct.setEnabled(self.canPaste)
		
        self.connect(copyAct, QtCore.SIGNAL("triggered()"), self.copySel)
        self.connect(pasteAct, QtCore.SIGNAL("triggered()"), self.paste)
	self.connect(upstreamAct, QtCore.SIGNAL("triggered()"), self.selectUpstream)
        menu.addAction(copyAct)
        menu.addAction(pasteAct)
	menu.addAction(upstreamAct)
        menu.exec_(event.globalPos())

    def copySel(self):
        cb = QtGui.QApplication.clipboard()
        cb.clear()
	modules = []
	connections = []
	import xml.dom.minidom
	impl = xml.dom.minidom.getDOMImplementation()
	dom = impl.createDocument(None, 'network',None)
	root = dom.documentElement
	if self.shapeEngine.selectedShapes > 0:
	    for s in self.shapeEngine.selectedShapes:
		module = self.pipeline.modules[s.id]
		module.dumpToXML(dom,root)
		modules.append(s.id)
	    for c in self.pipeline.connections.values():
		if c.sourceId in modules and c.destinationId in modules:
		    c.serialize(dom,root)
	    cb.setText (dom.toxml(), core.system.getClipboard())
	    self.emit(QtCore.SIGNAL("modulescopied"))
	    self.canPaste = True
    def paste(self):

	cb = QtGui.QApplication.clipboard()
	import xml.dom.minidom
	dom = xml.dom.minidom.parseString(str(cb.text(core.system.getClipboard())))
	root = dom.documentElement
	modules = []
	connections = []
	for xmlmodule in named_elements(root, 'module'):
	    module = VisModule.loadFromXML(xmlmodule)
	    modules.append(module)
	
	for xmlconnection in named_elements(root, 'connect'):
	    conn = VisConnection.loadFromXML(xmlconnection)
	    connections.append(conn)

	if len(modules) > 0:
	    self.emit(QtCore.SIGNAL("copyAndPaste"), modules, connections)
              
    def keyPressEvent(self, event):
	if(event.key() == QtCore.Qt.Key_R and (event.modifiers() & QtCore.Qt.ControlModifier)):
	    self.resetCamera()
	elif (event.key() == QtCore.Qt.Key_C and (event.modifiers() & QtCore.Qt.ControlModifier)):
	    self.copySel()
	elif (event.key() == QtCore.Qt.Key_V and (event.modifiers() & QtCore.Qt.ControlModifier)):
	    self.paste()
	else:
	    event.ignore()

    def resetCamera(self):
	pipeline = self.pipeline
	self.pipeline = None
	self.setPipeline(pipeline)

    def selectUpstream(self):
	upstream = []
	for s in self.shapeEngine.selectedShapes:
	    id = s.id
	    for i in self.pipeline.graph.inverse().bfs(id).keys():
		if i not in upstream:
		    upstream.append(i)
	for id in upstream:
	    s = self.shapeEngine.shapes[id]
	    if s not in self.shapeEngine.selectedShapes:
		self.shapeEngine.selectedShapes.append(s)
		s.setSelected(True)
	self.shapeEngine.updateGL()

    def updatePipeline(self):
        self.updateVistrail()
        self.setPipeline(self.pipeline)

    def handlerDispatch(self, handler):
        handler(self.controller)

    def configureModule(self, s):
        from modules.module_registry import registry
        from modules.module_configure import DefaultModuleConfigurationWidget
        if self.pipeline:
            module = self.pipeline.modules[s.id]
            widgetType = registry.moduleWidget[module.name]
            if not widgetType:
                widgetType = DefaultModuleConfigurationWidget
            global widget
            widget = widgetType(module, self)
            widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.connect(widget, QtCore.SIGNAL('updateActions'), self.handlerDispatch)
            self.connect(widget, QtCore.SIGNAL('updatePipeline()'), self.updatePipeline)
            widget.show()

    def changePortParams(self, paramList):
        (module, portName) = self.configuringPort
        self.controller.replaceModuleParams(module, portName, paramList)

    def configurePort(self, s):
        from modules.module_registry import registry
        if self.pipeline:
            widgetType = registry.getPortConfigureWidgetType(s.port.moduleName, s.port.name)
            if widgetType:
                module = self.pipeline.modules[s.parentId]
                paramList = [tuple([p.value() for p in f.params])
                             for f in module.functions
                             if f.name==s.port.name]
                configureWidget = widgetType(paramList)
                global widget
                from modules.port_configure import StandardPortConfigureContainer
                widget = StandardPortConfigureContainer(configureWidget, self)
                widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                self.configuringPort = (module, s.port.name)
                self.connect(widget, QtCore.SIGNAL('applyConfiguration'), self.changePortParams)
                widget.show()
            
    def handleDoubleClick(self, s):
        if s:
            if issubclass(ModuleShape, s.__class__):
                self.configureModule(s)
            if issubclass(PortShape, s.__class__):
                self.configurePort(s)
            

class QQueryView(QPipelineView):

    def updateBuilderOnChangeView(self, builder):
        """updateBuilderOnChangeView(self, builder) -> None.

        Shows the stack that is appropriate for a pipeline view on builder's
        stack widget, and disallows editing of refine lineEdit.

        (updateBuilderOnChangeView gets called whenever this widget becomes
        visible on the builder's tabWidget.)"""
        builder.stackWidget.setCurrentIndex(1)
        builder.refineLineEdit.setReadOnly(True)
        builder.executeStackWidget.setCurrentIndex(1)
