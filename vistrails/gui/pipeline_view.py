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
""" This is a QGraphicsView for pipeline view, it also holds different
types of graphics items that are only available in the pipeline
view. It only handles GUI-related actions, the rest of the
functionalities are implemented at somewhere else,
e.g. core.vistrails

QGraphicsConnectionItem
QGraphicsPortItem
QGraphicsModuleItem
QPipelineScene
QPipelineView
"""

from PyQt4 import QtCore, QtGui
from core.utils import VistrailsInternalError
from core.utils.uxml import named_elements
from core.modules.module_configure import DefaultModuleConfigurationWidget
from core.modules.module_registry import registry
from core.vistrail.connection import Connection
from core.vistrail.module import Module
from core.vistrail.pipeline import Pipeline
from core.vistrail.port import PortEndPoint
from gui.graphics_view import (QInteractiveGraphicsScene,
                               QInteractiveGraphicsView,
                               QGraphicsItemInterface)
from gui.module_palette import QModuleTreeWidget
from gui.theme import CurrentTheme
from xml.dom.minidom import getDOMImplementation, parseString
import math

################################################################################

class QGraphicsPortItem(QtGui.QGraphicsRectItem):
    """
    QGraphicsPortItem is a small port shape drawing on top (a child)
    of QGraphicsModuleItem, it can either be rectangle or rounded
    
    """
    def __init__(self, parent=None, scene=None, optional=False):
        """ QGraphicsPortItem(parent: QGraphicsItem, scene: QGraphicsScene,
                              optional: bool)
                              -> QGraphicsPortItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsRectItem.__init__(self, parent, scene)
        self.setZValue(1)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setPen(CurrentTheme.PORT_PEN)
        self.setBrush(CurrentTheme.PORT_BRUSH)
        if not optional:
            self.paint = self.paintRect
        else:
            self.paint = self.paintEllipse
        self.setRect(QtCore.QRectF(0, 0,
                                   CurrentTheme.PORT_WIDTH,
                                   CurrentTheme.PORT_HEIGHT))
        self.controller = None
        self.port = None
        self.dragging = False
        self.connection = None
        self.ghosted = False

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        self.ghosted = ghosted
        if ghosted:
            self.setPen(CurrentTheme.GHOSTED_PORT_PEN)
            self.setBrush(CurrentTheme.GHOSTED_PORT_BRUSH)
        else:
            self.setPen(CurrentTheme.PORT_PEN)
            self.setBrush(CurrentTheme.PORT_BRUSH)

    def paintEllipse(self, painter, option, widget=None):
        """ paintEllipse(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the optional port
        
        """
        painter.drawEllipse(self.rect())

    def paintRect(self, painter, option, widget=None):
        """ paintRect(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the regular port
        
        """
        QtGui.QGraphicsRectItem.paint(self, painter, option, widget)

    def setupPort(self, port):
        """ setupPort(port: Port) -> None
        Update the port tooltip, signatures, etc.
        
        """
        self.port = port
        self.setToolTip(port.toolTip())

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Prepare for dragging a connection
        
        """
        if self.controller and event.buttons() & QtCore.Qt.LeftButton:
            self.dragging = True
            event.accept()
        QtGui.QGraphicsRectItem.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Apply the connection
        
        """
        if self.connection and self.connection.snapPort and self.controller:
            snapModuleId = self.connection.snapPort.parentItem().id
            if self.port.endPoint==PortEndPoint.Source:
                conn = Connection.fromPorts(self.port,
                                            self.connection.snapPort.port)
                conn.sourceId = self.parentItem().id
                conn.destinationId = snapModuleId
            else:
                conn = Connection.fromPorts(self.connection.snapPort.port,
                                            self.port)
                conn.sourceId = snapModuleId
                conn.destinationId = self.parentItem().id
            conn.id = self.controller.currentPipeline.fresh_connection_id()
            self.controller.addConnection(conn)
            return
        if self.connection:
            self.scene().removeItem(self.connection)
            self.connection = None
        self.dragging = False
        QtGui.QGraphicsRectItem.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Change the connection
        
        """
        if self.dragging:
            if not self.connection:
                self.connection = QtGui.QGraphicsLineItem(None, self.scene())
                self.connection.setPen(CurrentTheme.CONNECTION_PEN)
                self.connection.setZValue(2)
            startPos = self.sceneBoundingRect().center()
            endPos = event.scenePos()
            self.connection.snapPort = self.findSnappedPort(endPos)
            if self.connection.snapPort:
                endPos = self.connection.snapPort.sceneBoundingRect().center()
                QtGui.QToolTip.showText(event.screenPos(),
                                        self.connection.snapPort.toolTip())
                
            self.connection.prepareGeometryChange()
            self.connection.setLine(startPos.x(), startPos.y(),
                                    endPos.x(), endPos.y())
        QtGui.QGraphicsRectItem.mouseMoveEvent(self, event)

    def findModuleUnder(self, pos):
        """ findModuleUnder(pos: QPoint) -> QGraphicsItem
        Search all items under pos and return the top-most module item if any
        
        """
        itemsUnder = self.scene().items(pos)
        for item in itemsUnder:
            if type(item)==QGraphicsModuleItem:
                return item
        return None        
        
    def findSnappedPort(self, pos):
        """ findSnappedPort(pos: QPoint) -> Port        
        Search all ports of the module under mouse cursor (if any) to
        find the closest matched port
        
        """
        snapModule = self.findModuleUnder(pos)
        if snapModule and snapModule!=self.parentItem(): 
            if self.port.endPoint==PortEndPoint.Source:
                return snapModule.getDestPort(pos, self.port)
            else:
                return snapModule.getSourcePort(pos, self.port)
        else:
            return None
        
    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Do not allow port to be selected
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool():
            return QtCore.QVariant(False)
        return QtGui.QGraphicsRectItem.itemChange(self, change, value)
    
class QGraphicsConnectionItem(QtGui.QGraphicsPolygonItem,
                              QGraphicsItemInterface):
    """
    QGraphicsConnectionItem is a connection shape connecting two port items
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsConnectionItem(parent: QGraphicsItem,
                                    scene: QGraphicsScene)
                                    -> QGraphicsConnectionItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsPolygonItem.__init__(self, parent, scene)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setZValue(2)
        self.connectionPen = CurrentTheme.CONNECTION_PEN
        self.startPos = QtCore.QPointF()
        self.endPos = QtCore.QPointF()
        self.visualPolygon = QtGui.QPolygonF()
        self.connectingModules = (None, None)
        self.id = -1
        self.ghosted = False
        self.connection = None

    def setupConnection(self, startPos, endPos):
        """ setupConnection(startPos: QPointF, endPos: QPointF) -> None
        Setup curve ends and store info
        
        """
        self.startPos = startPos
        self.endPos = endPos

        # Generate the polygon passing through two points
        steps = CurrentTheme.CONNECTION_CONTROL_POINTS
        polygon = QtGui.QPolygonF()
        self.visualPolygon = QtGui.QPolygonF()
        p1 = self.startPos
        p2 = self.endPos
        r = p2-p1
        horizontal = False        
        if p2.y() > p1.y() and p2.x() > p1.x():
            horizontal = True
        p1x = p1.x()
        p1y = p1.y()
        rx = r.x()
        ry = r.y()
        points = []
        for i in range(steps):
            t = float(i)/float(steps-1)
            s = (0.5+math.sin(math.pi*(t-0.5))*0.5)
            if horizontal:
                x = p1x+rx*t
                y = p1y+ry*s
                polygon.append(QtCore.QPointF(x,y-2))
                self.visualPolygon.append(QtCore.QPointF(x,y))
                points.append(QtCore.QPointF(x, y+2))
            else:
                x = p1x+rx*s
                y = p1y+ry*t
                polygon.append(QtCore.QPointF(x-2, y))
                self.visualPolygon.append(QtCore.QPointF(x, y))
                points.append(QtCore.QPointF(x+2, y))
                
        for p in reversed(points):
            polygon.append(p)
        polygon.append(polygon.at(0))
        self.setPolygon(polygon)

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        self.ghosted = ghosted
        if ghosted:
            self.connectionPen = CurrentTheme.GHOSTED_CONNECTION_PEN
        else:
            self.connectionPen = CurrentTheme.CONNECTION_PEN

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the connection
        
        """
        if self.isSelected():
            painter.setPen(CurrentTheme.CONNECTION_SELECTED_PEN)
        else:
            painter.setPen(self.connectionPen)
        painter.drawPolyline(self.visualPolygon)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Do not allow connection to be selected with modules
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool():
            selectedItems = self.scene().selectedItems()
            for item in selectedItems:
                if type(item)==QGraphicsModuleItem:
                    return QtCore.QVariant(False)
        return QtGui.QGraphicsPolygonItem.itemChange(self, change, value)    

class QGraphicsModuleItem(QtGui.QGraphicsItem, QGraphicsItemInterface):
    """
    QGraphicsModuleItem knows how to draw a Vistrail Module into the
    pipeline view. It is usually a recntangular shape with a bold text
    in the center. It also has its input/output port shapes as its
    children. Another remark is that connections are also children of
    module shapes. Each connection belongs to its source module
    ('output port' end of the connection)
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsModuleItem(parent: QGraphicsItem, scene: QGraphicsScene)
                                -> QGraphicsModuleItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        self.paddedRect = QtCore.QRectF()
        QtGui.QGraphicsItem.__init__(self, parent, scene)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable |
                      QtGui.QGraphicsItem.ItemIsMovable)
        self.setZValue(0)
        self.labelFont = CurrentTheme.MODULE_FONT
        self.labelFontMetric = CurrentTheme.MODULE_FONT_METRIC
        self.modulePen = CurrentTheme.MODULE_PEN
        self.moduleBrush = CurrentTheme.MODULE_BRUSH
        self.labelPen = CurrentTheme.MODULE_LABEL_PEN
        self.id = -1
        self.label = ''
        self.inputPorts = {}
        self.outputPorts = {}
        self.dependingConnectionItems = []
        self.controller = None
        self.module = None
        self.ghosted = False
        self.isSpreadsheetCell = False

    def computeBoundingRect(self):
        """ computeBoundingRect() -> None
        Adjust the module size according to the text size
        
        """
        textRect = self.labelFontMetric.boundingRect(self.label)
        textRect.translate(-textRect.center().x(), -textRect.center().y())
        self.paddedRect = QtCore.QRectF(
            textRect.adjusted(-CurrentTheme.MODULE_LABEL_MARGIN[0],
                              -CurrentTheme.MODULE_LABEL_MARGIN[1],
                              CurrentTheme.MODULE_LABEL_MARGIN[2],
                              CurrentTheme.MODULE_LABEL_MARGIN[3]))

    def boundingRect(self):
        """ boundingRect() -> QRectF
        Returns the bounding box of the module
        
        """
        return self.paddedRect.adjusted(-2, -2, 2, 2)

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        self.ghosted = ghosted
        if ghosted:
            self.modulePen = CurrentTheme.GHOSTED_MODULE_PEN
            self.moduleBrush = CurrentTheme.GHOSTED_MODULE_BRUSH
            self.labelPen = CurrentTheme.GHOSTED_MODULE_LABEL_PEN
        else:
            self.modulePen = CurrentTheme.MODULE_PEN
            self.moduleBrush = CurrentTheme.MODULE_BRUSH
            self.labelPen = CurrentTheme.MODULE_LABEL_PEN
            
    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the module
        
        """
        painter.fillRect(self.paddedRect, self.moduleBrush)
        if self.isSelected():
            painter.setPen(CurrentTheme.MODULE_SELECTED_PEN)
        else:
            painter.setPen(self.modulePen)
        painter.drawRect(self.paddedRect)
        if self.isSelected():
            painter.setPen(CurrentTheme.MODULE_LABEL_SELECTED_PEN)
        else:
            painter.setPen(self.labelPen)
        painter.setFont(self.labelFont)
        painter.drawText(self.paddedRect, QtCore.Qt.AlignCenter, self.label)

    def adjustWidthToMin(self, minWidth):
        """ adjustWidthToContain(minWidth: int) -> None
        Resize the module width to at least be minWidth
        
        """
        if minWidth>self.paddedRect.width():
            diff = minWidth - self.paddedRect.width() + 1
            self.paddedRect.adjust(-diff/2, 0, diff/2, 0)

    def setupModule(self, module):
        """ setupModule(module: Module) -> None
        Set up the item to reflect the info in 'module'
        
        """
        # Update module info and visual
        self.id = module.id
        self.module = module
        self.label = module.name
        self.computeBoundingRect()
        self.resetMatrix()
        self.translate(module.center.x, -module.center.y)

        # Check to see which ports will be shown on the screen
        visibleOptionalPorts = []
        inputPorts = []
        self.optionalInputPorts = []
        for p in module.destinationPorts():
            if not p.optional:
                inputPorts.append(p)
            elif p.name in module.portVisible:
                visibleOptionalPorts.append(p)
            else:
                self.optionalInputPorts.append(p)
        inputPorts += visibleOptionalPorts
        
        visibleOptionalPorts = []
        outputPorts = []
        self.optionalOutputPorts = []
        for p in module.sourcePorts():
            if not p.optional:
                outputPorts.append(p)
            elif p.name in module.portVisible:
                visibleOptionalPorts.append(p)
            else:
                self.optionalOutputPorts.append(p)
        outputPorts += visibleOptionalPorts

        # Adjust the width to fit all ports
        maxPortCount = max(len(inputPorts), len(outputPorts))
        minWidth = (CurrentTheme.MODULE_PORT_MARGIN[0] +
                    CurrentTheme.PORT_WIDTH*maxPortCount +
                    CurrentTheme.MODULE_PORT_SPACE*(maxPortCount-1) +
                    CurrentTheme.MODULE_PORT_MARGIN[2] +
                    CurrentTheme.MODULE_PORT_PADDED_SPACE)
        self.adjustWidthToMin(minWidth)

        # Update input ports
        y = self.paddedRect.y() + CurrentTheme.MODULE_PORT_MARGIN[1]
        x = self.paddedRect.x() + CurrentTheme.MODULE_PORT_MARGIN[0]
        self.inputPorts = {}
        for port in inputPorts:
            self.inputPorts[port] = self.createPortItem(port, x, y)
            x += CurrentTheme.PORT_WIDTH + CurrentTheme.MODULE_PORT_SPACE
        self.nextInputPortPos = [x,y]

        # Update output ports
        y = (self.paddedRect.bottom() - CurrentTheme.PORT_HEIGHT
             - CurrentTheme.MODULE_PORT_MARGIN[3])
        x = (self.paddedRect.right() - CurrentTheme.PORT_WIDTH
             - CurrentTheme.MODULE_PORT_MARGIN[2])
        self.outputPorts = {}
        for port in outputPorts:            
            self.outputPorts[port] = self.createPortItem(port, x, y)
            x -= CurrentTheme.PORT_WIDTH + CurrentTheme.MODULE_PORT_SPACE
        self.nextOutputPortPos = [x, y]

        # See if this is a spreadsheet cell
        if registry.hasModule('SpreadsheetCell'):
            scDesc = registry.getDescriptorByName('SpreadsheetCell')
            thisDesc = registry.getDescriptorByName(self.module.name)
            self.isSpreadsheetCell = issubclass(thisDesc.module,
                                                scDesc.module)

    def createPortItem(self, port, x, y):
        """ createPortItem(port: Port, x: int, y: int) -> QGraphicsPortItem
        Create a item from the port spec
        
        """
        portShape = QGraphicsPortItem(self, self.scene(), port.optional)
        portShape.controller = self.controller
        portShape.setGhosted(self.ghosted)
        portShape.setupPort(port)
        portShape.translate(x, y)
        return portShape

    def getPortPosition(self, port, portDict):
        """ getPortPosition(port: Port,
                            portDict: {Port:QGraphicsPortItem})
                            -> QRectF
        Return the scene position of a port matched 'port' in portDict
        
        """
        for (p, item) in portDict.items():
            if registry.isPortSubType(port, p):
                return item.sceneBoundingRect().center()
        return None

    def getInputPortPosition(self, port):
        """ getInputPortPosition(port: Port} -> QRectF
        Just an overload function of getPortPosition to get from input ports
        
        """
        pos = self.getPortPosition(port, self.inputPorts)
        if pos==None:
            for p in self.optionalInputPorts:
                if registry.isPortSubType(port, p):
                    portShape = self.createPortItem(p,*self.nextInputPortPos)
                    self.inputPorts[port] = portShape
                    self.nextInputPortPos[0] += (CurrentTheme.PORT_WIDTH +
                                                 CurrentTheme.MODULE_PORT_SPACE)
                    return portShape.sceneBoundingRect().center()
            raise VistrailsInternalError("Error: did not find input port")
        return pos
        
    def getOutputPortPosition(self, port):
        """ getOutputPortPosition(port: Port} -> QRectF
        Just an overload function of getPortPosition to get from output ports
        
        """
        pos = self.getPortPosition(port, self.outputPorts)
        if pos==None:
            for p in self.optionalOutputPorts:
                if registry.isPortSubType(port, p):
                    portShape = self.createPortItem(p,*self.nextOutputPortPos)
                    self.outputPorts[port] = portShape
                    self.nextOutputPortPos[0] += (CurrentTheme.PORT_WIDTH +
                                                  CurrentTheme.MODULE_PORT_SPACE)
                    return portShape.sceneBoundingRect().center()
            raise VistrailsInternalError("Error: did not find output port")
        return pos

    def addConnectionItem(self, connectionItem, start):
        """ addConnectionItem(connectionItem: QGraphicsConnectionItem,
                              start: bool) -> None                              
        Add connectionItem into dependancy list to adjust it when this
        module is moved. If start=True the depending point is the
        start point, else it is the end point
        
        """
        self.dependingConnectionItems.append((connectionItem, start))

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Capture move event to also move the connections
        
        """
        if change==QtGui.QGraphicsItem.ItemPositionChange:
            oldPos = self.pos()
            newPos = value.toPointF()
            dis = newPos - oldPos
            for (connectionItem, start) in self.dependingConnectionItems:
                (srcModule, dstModule) = connectionItem.connectingModules
                if srcModule.isSelected() and dstModule.isSelected():
                    if srcModule==self:
                        connectionItem.moveBy(dis.x(), dis.y())
                else:
                    connectionItem.prepareGeometryChange()
                    if start:
                        connectionItem.setupConnection(
                            connectionItem.startPos+dis,
                            connectionItem.endPos)
                    else:
                        connectionItem.setupConnection(
                            connectionItem.startPos,
                            connectionItem.endPos+dis)
        # Do not allow connection to be selected with modules
        elif change==QtGui.QGraphicsItem.ItemSelectedChange:
            for item in self.scene().selectedItems():
                if type(item)==QGraphicsConnectionItem:
                    item.setSelected(False)
            selectedItems = self.scene().selectedItems()
            selectedId = -1
            if not self.scene().multiSelecting:
                if value.toBool():
                    for item in selectedItems:
                        if type(item)!=QGraphicsModuleItem:
                            item.setSelected(False)
                            item.update()
                    if len(selectedItems)==0:
                        selectedId = self.id
                        selectedItems.append(self)
                elif len(selectedItems)==2:
                    if selectedItems[0]==self:
                        selectedId = selectedItems[1].id
                        selectedItems = selectedItems[1:]
                    else:
                        selectedId = selectedItems[0].id
                        selectedItems = selectedItems[:1]
                else:
                    selectedItems = [m for m in selectedItems if m!=self]
            self.scene().emit(QtCore.SIGNAL('moduleSelected'),
                              selectedId, selectedItems)
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def getDestPort(self, pos, srcPort):
        """ getDestPort(self, pos: QPointF, srcPort: Port) -> QGraphicsPortItem
        Look for the destination port match 'port' and closest to pos
        
        """
        result = None
        minDis = None
        for (dstPort, dstItem) in self.inputPorts.items():
            if (registry.portsCanConnect(srcPort, dstPort) and
                dstItem.isVisible()):                
                vector = (pos - dstItem.sceneBoundingRect().center())
                dis = vector.x()*vector.x() + vector.y()*vector.y()
                if result==None or dis<minDis:
                    minDis = dis
                    result = dstItem
        return result

    def getSourcePort(self, pos, dstPort):
        """ getSourcePort(self, pos: QPointF, dstPort: Port)
                          -> QGraphicsPortItem
        Look for the source port match 'port' and closest to pos
        
        """
        result = None
        minDis = None
        for (srcPort, srcItem) in self.outputPorts.items():
            if (registry.portsCanConnect(srcPort, dstPort) and
                srcItem.isVisible()):
                vector = (pos - srcItem.sceneBoundingRect().center())
                dis = vector.x()*vector.x() + vector.y()*vector.y()
                if result==None or dis<minDis:
                    minDis = dis
                    result = srcItem
        return result

    def mouseDoubleClickEvent(self, event):
        """ mouseDoubleClickEvent(event: QGraphicsSceneMouseEvent) -> None
        Bring up the module configuration widget (if any)
        
        """
        if self.controller:
            self.controller.resendVersionWasChanged
            module = self.controller.currentPipeline.modules[self.id]
            widgetType = registry.moduleWidget[module.name]
            if not widgetType:
                widgetType = DefaultModuleConfigurationWidget
            global widget
            widget = widgetType(module, self.controller, None)
            widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            QtCore.QObject.connect(widget, QtCore.SIGNAL('doneConfigure()'),
                                   self.controller.resendVersionWasChanged)
            widget.show()
        

class QPipelineScene(QInteractiveGraphicsScene):
    """
    QPipelineScene inherits from QInteractiveGraphicsScene to keep track of the
    pipeline scenes, i.e. modules, connections, selection
    
    """

    def __init__(self, parent=None):
        """ QPipelineScene(parent: QWidget) -> QPipelineScene
        Initialize the graphics scene with no shapes
        
        """
        QInteractiveGraphicsScene.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.PIPELINE_VIEW_BACKGROUND_BRUSH)
        self.setSceneRect(QtCore.QRectF(-5000, -5000, 10000, 10000))
        self.controller = None
        self.modules = {}
        self.noUpdate = False
        self.installEventFilter(self)

    def addModule(self, module, moduleBrush=None):
        """ addModule(module: Module, moduleBrush: QBrush) -> None
        Add a module to the scene
        
        """
        moduleItem = QGraphicsModuleItem(None)
        if self.controller and self.controller.search:
            moduleQuery = (self.controller.currentVersion, module)
            matched = self.controller.search.matchModule(*moduleQuery)
            moduleItem.setGhosted(not matched)
        moduleItem.controller = self.controller
        moduleItem.setupModule(module)
        if moduleBrush:
            moduleItem.moduleBrush = moduleBrush
        self.addItem(moduleItem)
        self.modules[module.id] = moduleItem
        return moduleItem

    def addConnection(self, connection):
        """ addConnection(connection: Connection) -> None
        Add a connection to the scene
        
        """
        srcModule = self.modules[connection.source.moduleId]
        dstModule = self.modules[connection.destination.moduleId]
        srcPoint = srcModule.getOutputPortPosition(connection.source)
        dstPoint = dstModule.getInputPortPosition(connection.destination)
        connectionItem = QGraphicsConnectionItem(None)
        connectionItem.setupConnection(dstPoint, srcPoint)
        connectionItem.id = connection.id
        connectionItem.connection = connection
        connectionItem.connectingModules = (srcModule, dstModule)
        srcModule.addConnectionItem(connectionItem, False)
        dstModule.addConnectionItem(connectionItem, True)
        self.addItem(connectionItem)
        return connectionItem

    def clear(self):
        """ clear() -> None
        Clear the whole scene
        
        """
        self.modules = {}
        self.clearItems()

    def setupScene(self, pipeline):
        """ setupScene(pipeline: Pipeline) -> None
        Construct the scene to view a pipeline
        
        """
        if self.noUpdate: return
        needReset = len(self.items())==0        
        # Clean the previous scene
        self.clear()

        if pipeline:
            # Create module shapes
            for module in pipeline.modules.itervalues():
                self.addModule(module)
            # Create connection shapes
            for connection in pipeline.connections.itervalues():
                self.addConnection(connection)

        # Update bounding rects and fit to all view
        self.updateSceneBoundingRect()        

        if needReset and len(self.items())>0:
            self.fitToAllViews()

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the module palette
        
        """
        if (self.controller and self.controller.currentVersion!=-1 and
            type(event.source())==QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from the module palette
        
        """
        if (self.controller and self.controller.currentVersion!=-1 and
            type(event.source())==QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()

    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new module
        
        """
        if (self.controller and self.controller.currentVersion!=-1 and
            type(event.source())==QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                for item in data.items:
                    self.controller.resetPipelineView = False
                    self.noUpdate = True
                    module = self.controller.addModule(item.descriptor.name,
                                                       event.scenePos().x(),
                                                       -event.scenePos().y())
                    self.addModule(module).update()
                    self.noUpdate = False

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Capture 'Del', 'Backspace' for deleting modules
        """
        if (self.controller and
            event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            selectedItems = self.selectedItems()
            if len(selectedItems)>0:
                if type(selectedItems[0])==QGraphicsModuleItem:
                    self.noUpdate = True
                    idList = [m.id for m in selectedItems]
                    self.controller.deleteModuleList(idList)
                    connections = []
                    for m in selectedItems:
                        connections += [c[0] for c in m.dependingConnectionItems]
                    self.removeItems(connections)
                    for (mId, item) in self.modules.items():
                        if item in selectedItems:
                            del self.modules[mId]
                    self.removeItems(selectedItems)
                    self.updateSceneBoundingRect()
                    self.update()
                    self.noUpdate = False
                elif type(selectedItems[0])==QGraphicsConnectionItem:
                    self.controller.resetPipelineView = False
                    idList = [conn.id for conn in selectedItems]
                    self.controller.deleteConnectionList(idList)
        elif (event.key()==QtCore.Qt.Key_C and
              event.modifiers()==QtCore.Qt.ControlModifier):
            self.copySelection()
        elif (event.key()==QtCore.Qt.Key_V and
              event.modifiers()==QtCore.Qt.ControlModifier):
            self.pasteFromClipboard()
        else:
            QInteractiveGraphicsScene.keyPressEvent(self, event)

    def copySelection(self):
        """ copySelection() -> None
        Copy the current selected modules into clipboard
        
        """
        selectedItems = self.selectedItems()
        if len(selectedItems)>0:
            cb = QtGui.QApplication.clipboard()
            dom = getDOMImplementation().createDocument(None, 'network', None)
            root = dom.documentElement
            copiedConnections = {}
            modules = {}
            for item in selectedItems:
                module = item.module
                module.dumpToXML(dom,root)
                modules[module.id] = True
            for item in selectedItems:
                for (connItem, start) in item.dependingConnectionItems:
                    conn = connItem.connection
                    if ((not copiedConnections.has_key(conn)) and
                        modules.has_key(conn.sourceId) and
                        modules.has_key(conn.destinationId)):
                        conn.serialize(dom, root)
                        copiedConnections[conn] = True
            cb.setText(dom.toxml())
    def pasteFromClipboard(self):
        """ pasteFromClipboard() -> None
        Paste modules/connections from the clipboard into this pipeline view
        
        """
        if self.controller:
            cb = QtGui.QApplication.clipboard()        
            text = str(cb.text())
            if text=='': return
            dom = parseString(str(cb.text()))
            root = dom.documentElement
            modules = []
            connections = []
            for xmlmodule in named_elements(root, 'module'):
                module = Module.loadFromXML(xmlmodule)
                modules.append(module)
	
            for xmlconnection in named_elements(root, 'connect'):
                conn = Connection.loadFromXML(xmlconnection)
                connections.append(conn)
            self.controller.pasteModulesAndConnections(modules, connections)
            
    def eventFilter(self, object, e):
        """ eventFilter(object: QObject, e: QEvent) -> None        
        Catch all the set module color events through self-event
        filter. Using the standard event cause some ambiguity in
        converting between QGraphicsSceneEvent and QEvent
        
        """
        if e.type()==QModuleStatusEvent.TYPE:
            if e.moduleId>=0:
                item = self.modules[e.moduleId]
                item.setToolTip(e.toolTip)
                if e.status==0:
                    item.moduleBrush = CurrentTheme.SUCCESS_MODULE_BRUSH
                elif e.status==1:
                    item.moduleBrush = CurrentTheme.ERROR_MODULE_BRUSH
                elif e.status==2:
                    item.moduleBrush = CurrentTheme.NOT_EXECUTED_MODULE_BRUSH
                elif e.status==3:
                    item.moduleBrush = CurrentTheme.ACTIVE_MODULE_BRUSH
                elif e.status==4:
                    item.moduleBrush = CurrentTheme.COMPUTING_MODULE_BRUSH                    
                item.update()
            return True
        return False

    def setModuleSuccess(self, moduleId):
        """ setModuleSuccess(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 0, ''))
        QtCore.QCoreApplication.processEvents()

    def setModuleError(self, moduleId, error):
        """ setModuleError(moduleId: int, error: str) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 1, error))
        QtCore.QCoreApplication.processEvents()
        
    def setModuleNotExecuted(self, moduleId):
        """ setModuleNotExecuted(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 2, ''))
        QtCore.QCoreApplication.processEvents()

    def setModuleActive(self, moduleId):
        """ setModuleActive(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 3, ''))
        QtCore.QCoreApplication.processEvents()

    def setModuleComputing(self, moduleId):
        """ setModuleComputing(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 4, ''))
        QtCore.QCoreApplication.processEvents()


class QModuleStatusEvent(QtCore.QEvent):
    """
    QModuleStatusEvent is trying to handle thread-safe real-time
    module updates in the scene through post-event
    
    """
    TYPE = QtCore.QEvent.Type(QtCore.QEvent.User)
    def __init__(self, moduleId, status, toolTip):
        """ QModuleStatusEvent(type: int) -> None        
        Initialize the specific event with the module status. Status 0
        for success, 1 for error and 2 for not execute, 3 for active,
        and 4 for computing
        
        """
        QtCore.QEvent.__init__(self, QModuleStatusEvent.TYPE)
        self.moduleId = moduleId
        self.status = status
        self.toolTip = toolTip
            
class QPipelineView(QInteractiveGraphicsView):
    """
    QPipelineView inherits from QInteractiveGraphicsView that will
    handle drawing of module, connection shapes and selecting
    mechanism.
    
    """

    def __init__(self, parent=None):
        """ QPipelineView(parent: QWidget) -> QPipelineView
        Initialize the graphics view and its properties
        
        """
        QInteractiveGraphicsView.__init__(self, parent)
        self.setWindowTitle('Pipeline')
        self.setScene(QPipelineScene(self))

################################################################################

if __name__=="__main__":
    
    # Initialize the Vistrails Application and Theme
    import sys
    from gui import qt, theme
    from gui import vis_application
    vis_application.start_application()
    app = vis_application.VistrailsApplication

    # Get the pipeline
    from core.xml_parser import XMLParser    
    parser = XMLParser()
    parser.openVistrail('d:/hvo/vgc/src/vistrails/trunk/examples/vtk.xml')
    vistrail = parser.getVistrail()
    version = vistrail.tagMap['Single Renderer']
    pipeline = vistrail.getPipeline(version)

    # Now visually test QPipelineView
    pv = QPipelineView(None)
    pv.scene().setupScene(pipeline)
    pv.show()
    sys.exit(app.exec_())
