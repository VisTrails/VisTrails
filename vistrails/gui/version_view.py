""" This is a QGraphicsView for pipeline view, it also holds different
types of graphics items that are only available in the pipeline
view. It only handles GUI-related actions, the rest of the
functionalities are implemented at somewhere else,
e.g. core.vistrails

QGraphicsLinkItem
QGraphicsVersionItem
QVersionTreeScene
QVersionTreeView
"""

from PyQt4 import QtCore, QtGui
from core.dotty import DotLayout
from gui.graphics_view import (QInteractiveGraphicsScene,
                               QInteractiveGraphicsView,
                               QGraphicsItemInterface,
                               QGraphicsRubberBandItem)
from gui.theme import CurrentTheme
from gui.vis_diff import QVisualDiff
import math

################################################################################

class QGraphicsLinkItem(QtGui.QGraphicsPolygonItem, QGraphicsItemInterface):
    """
    QGraphicsLinkItem is a connection shape connecting two versions
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsLinkItem(parent: QGraphicsItem,
                              scene: QGraphicsScene) -> QGraphicsLinkItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsPolygonItem.__init__(self, parent, scene)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setZValue(0)
        self.setPen(CurrentTheme.LINK_PEN)
        self.startVersion = -1
        self.endVersion = -1

    def setupLink(self, v1, v2):
        """ setupLink(v1, v2: QGraphicsVersionItem) -> None
        Setup a line connecting v1 and v2 items
        
        """
        self.startVersion = min(v1.id, v2.id)
        self.endVersion = max(v1.id, v2.id)
        c1 = v1.sceneBoundingRect().center()
        c2 = v2.sceneBoundingRect().center()

        # Compute the line of the link and its normal line throught
        # the midpoint
        mainLine = QtCore.QLineF(c1.x(), c1.y(), c2.x(), c2.y())
        normalLine = mainLine.normalVector()        
        normalLine.setLength(CurrentTheme.LINK_SEGMENT_LENGTH)
        dis = (mainLine.pointAt(0.5)-mainLine.p1()+
               normalLine.p1()-normalLine.pointAt(0.5))
        normalLine.translate(dis.x(), dis.y())

        # Generate 2 segments along the main line and 3 segments along
        # the normal line
        self.lines = []        
        gapLine = QtCore.QLineF(mainLine)
        gapLine.setLength(CurrentTheme.LINK_SEGMENT_GAP)
        gapVector = gapLine.p2()-gapLine.p1()
        
        # Fist segment along the main line
        line = QtCore.QLineF(mainLine)
        line.setLength(line.length()/2-CurrentTheme.LINK_SEGMENT_GAP*2)
        self.lines.append(QtCore.QLineF(line))
        
        # Second segment along the main line
        line.translate(line.p2()-line.p1()+gapVector*4)
        self.lines.append(QtCore.QLineF(line))

        # First normal segment in front
        line = QtCore.QLineF(normalLine)
        line.translate(gapVector*(-1.0))
        self.lines.append(QtCore.QLineF(line))
        
        # Middle normal segment
        self.lines.append(QtCore.QLineF(normalLine))
        
        # Third normal segment in back
        line = QtCore.QLineF(normalLine)
        line.translate(gapVector)
        self.lines.append(QtCore.QLineF(line))

        # Create the poly line for selection and redraw
        poly = QtGui.QPolygonF()
        poly.append(self.lines[0].p1())
        poly.append(self.lines[2].p1())
        poly.append(self.lines[4].p1())
        poly.append(self.lines[1].p2())
        poly.append(self.lines[4].p2())
        poly.append(self.lines[2].p2())
        poly.append(self.lines[0].p1())
        self.setPolygon(poly)

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the link
        
        """
        if self.isSelected():
            painter.setPen(CurrentTheme.LINK_SELECTED_PEN)
        else:
            painter.setPen(CurrentTheme.LINK_PEN)
        for line in self.lines:
            painter.drawLine(line)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Do not allow link to be selected with version shape
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool():
            selectedItems = self.scene().selectedItems()
            for item in selectedItems:
                if isinstance(item, QGraphicsVersionItem):
                    return QtCore.QVariant(False)
        return QtGui.QGraphicsPolygonItem.itemChange(self, change, value)

class QGraphicsVersionItem(QtGui.QGraphicsEllipseItem, QGraphicsItemInterface):
    """
    QGraphicsVersionItem is the version shape holding version id and
    label
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsVersionItem(parent: QGraphicsItem, scene: QGraphicsScene)
                                -> QGraphicsVersionItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsEllipseItem.__init__(self, parent, scene)
        self.setZValue(1)
        self.setAcceptDrops(True)
        self.versionPen = CurrentTheme.VERSION_PEN
        self.versionLabelPen = CurrentTheme.VERSION_LABEL_PEN
        self.versionBrush = CurrentTheme.VERSION_USER_BRUSH
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.id = -1
        self.label = ''
        self.dragging = False

    def setGhosted(self, ghosted=True):
        """ setGhosted(ghosted: True) -> None
        Set this version to be ghosted or not
        
        """
        if ghosted:
            self.versionPen = CurrentTheme.GHOSTED_VERSION_PEN
            self.versionLabelPen = CurrentTheme.GHOSTED_VERSION_LABEL_PEN
            self.versionBrush = CurrentTheme.GHOSTED_VERSION_USER_BRUSH
            self.setFlags(QtGui.QGraphicsItem.GraphicsItemFlags())
        else:
            self.versionPen = CurrentTheme.VERSION_PEN
            self.versionLabelPen = CurrentTheme.VERSION_LABEL_PEN
            self.versionBrush = CurrentTheme.VERSION_USER_BRUSH
            self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)

    def setupVersion(self, node, label):
        """ setupPort(node: DotNode, label: str) -> None
        Update the version dimensions and id
        
        """
        self.id = node.id
        self.label = label
        self.setRect(QtCore.QRectF(node.p.x-node.width/2,
                                   -node.p.y/2,
                                   node.width,
                                   node.height))
    def boundingRect(self):
        """ boundingRect() -> QRectF
        Add a padded space to avoid un-updated area
        """
        return self.rect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the version shape
        
        """
        if self.isSelected():
            painter.setPen(CurrentTheme.VERSION_SELECTED_PEN)
        else:
            painter.setPen(self.versionPen)
        painter.setBrush(self.versionBrush)
        painter.drawEllipse(self.rect())
        if self.isSelected():
            painter.setPen(CurrentTheme.VERSION_LABEL_SELECTED_PEN)
        else:
            painter.setPen(self.versionLabelPen)
        painter.setFont(CurrentTheme.VERSION_FONT)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.label)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        # Do not allow links to be selected with version
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange:
            selectedItems = self.scene().selectedItems()
            selectedId = -1
            if value.toBool():
                for item in selectedItems:
                    if isinstance(item, QGraphicsLinkItem):
                        item.setSelected(False)
                        item.update()
                if len(selectedItems)==0:
                    selectedId = self.id
            elif len(selectedItems)==2:
                if selectedItems[0]==self:
                    selectedId = selectedItems[1].id
                else:
                    selectedId = selectedItems[0].id
            selectByClick = self.scene().mouseGrabberItem() == self
            if not selectByClick:
                for item in self.scene().items():
                    if type(item)==QGraphicsRubberBandItem:
                        selectByClick = True
                        break
            self.scene().emit(QtCore.SIGNAL('versionSelected(int,bool)'),
                              selectedId, selectByClick)                              
        return QtGui.QGraphicsItem.itemChange(self, change, value)    

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Start dragging a version to someplaces...
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            self.dragging = True
        QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Now begin to use Qt drag and drop
        
        """
        if self.dragging:
            self.dragging = False
            data = QtCore.QMimeData()
            data.versionId = self.id
            data.controller = self.scene().controller
            drag = QtGui.QDrag(self.scene().views()[0])
            drag.setMimeData(data)
            drag.setPixmap(CurrentTheme.VERSION_DRAG_PIXMAP)
            drag.start()
        QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Cancel the drag
        
        """
        self.dragging = False
        QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, event)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Capture version-to-version drag-and-drop
        
        """
        data = event.mimeData()
        if (hasattr(data, 'versionId') and
            hasattr(data, 'controller') and
            data.versionId!=self.id):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        if (hasattr(data, 'versionId') and hasattr(data, 'controller') and
            data.controller==self.scene().controller):
            event.accept()
            visDiff = QVisualDiff(self.scene().controller.vistrail,
                                  data.versionId,
                                  self.id,
                                  self.scene().views()[0])
            visDiff.show()
        else:
            event.ignore()        

class QVersionTreeScene(QInteractiveGraphicsScene):
    """
    QVersionTree inherits from QInteractiveGraphicsScene to keep track
    of the version scenes, i.e. versions, connections, etc.
    
    """

    def __init__(self, parent=None):
        """ QVersionTree(parent: QWidget) -> QVersionTree
        Initialize the graphics scene with no shapes
        
        """
        QInteractiveGraphicsScene.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.VERSION_TREE_BACKGROUND_BRUSH)
        self.setSceneRect(QtCore.QRectF(-5000, -5000, 10000, 10000))
        self.versions = {}
        self.controller = None

    def addVersion(self, node, label, ghosted=False):
        """ addModule(node: DotNode, ghosted: bool) -> None
        Add a module to the scene
        
        """
        versionShape = QGraphicsVersionItem(None)
        versionShape.setupVersion(node, label)
        versionShape.setGhosted(ghosted)
        self.addItem(versionShape)
        self.versions[node.id] = versionShape

    def addLink(self, v1, v2):
        """ addLink(v1, v2: QGraphicsVersionItem) -> None
        Add a link to the scene
        
        """
        linkShape = QGraphicsLinkItem()
        linkShape.setupLink(v1, v2)
        self.addItem(linkShape)
        
    def clear(self):
        """ clear() -> None
        Clear the whole scene
        
        """
        self.versions = {}
        self.clearItems()

    def setupScene(self, controller):
        """ setupScene(vistrail: VistrailController) -> None
        Construct the scene to view a version tree
        
        """
        # Clean the previous scene
        self.clear()

        # Call dotty to perform graph layout
        graph = controller.refineGraph()
        layout = DotLayout()
        layout.layoutFrom(controller.vistrail, graph)

        # Put the layout to the graphics view
        for node in layout.nodes.itervalues():
            label = ''
            if controller.vistrail.inverseTagMap.has_key(node.id):
                label = controller.vistrail.inverseTagMap[node.id]
            if controller.search:
                if node.id!=0:
                    action = controller.vistrail.actionMap[node.id]
                    ghosted = not controller.search.match(action)
                else:
                    ghosted = True
            else:
                ghosted = False
            self.addVersion(node, label, ghosted)
            if node.id==controller.currentVersion:
                self.versions[node.id].setSelected(True)
            
        # Add version links
        for nodeId in graph.vertices.keys():
            eFrom = graph.edgesFrom(nodeId)
            for (v1, v2) in eFrom:
                if self.versions.has_key(nodeId) and self.versions.has_key(v1):
                    self.addLink(self.versions[nodeId], self.versions[v1])
            
        # Update bounding rects and fit to all view
        self.updateSceneBoundingRect()
        for view in self.views():
            view.resetCachedContent()

class QVersionTreeView(QInteractiveGraphicsView):
    """
    QVersionTreeView inherits from QInteractiveGraphicsView that will
    handle drawing of versions layout output from Dotty
    
    """

    def __init__(self, parent=None):
        """ QVersionTreeView(parent: QWidget) -> QVersionTreeView
        Initialize the graphics view and its properties
        
        """
        QInteractiveGraphicsView.__init__(self, parent)
        self.setWindowTitle('Version Tree')
        self.setScene(QVersionTreeScene(self))

################################################################################


if __name__=="__main__":
    
    # Initialize the Vistrails Application and Theme
    import sys
    from gui import qt, theme
    import vis_application
    vis_application.start_application()
    app = vis_application.VistrailsApplication
    theme.initializeCurrentTheme()

    # Get the vistrail
    from core.xml_parser import XMLParser
    parser = XMLParser()
    parser.openVistrail('d:/hvo/vgc/src/vistrails/trunk/examples/lung.xml')
    vistrail = parser.getVistrail()
    
    # Now visually test QVersionTreeView
    vt = QVersionTreeView(None)
    vt.scene().setupScene(vistrail)
    vt.show()
    sys.exit(vis_application.VistrailsApplication.exec_())
