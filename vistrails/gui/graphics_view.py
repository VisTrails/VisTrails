""" This containing a subclassed QGraphicsView that allows
zoom/pan/select inside the graphics view and supports PIP as well

QInteractiveGraphicsScene
QInteractiveGraphicsView
QPIPGraphicsView
"""

from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
import math

################################################################################

class QGraphicsItemInterface(object):
    """
    QGraphicsItem will override the default QGraphicsItem mouseRelease
    event to let it fires only 1 ItemSelectionChanged event. This is
    due to the clearSelection() in
    qgraphicsitem.cpp::QGrahpicsItem::mouseReleaseEvent
    
    """
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None        
        Make sure the current item is not selected before
        clearSelection and perform the selected again
        
        """
        if ((self.flags() & QtGui.QGraphicsItem.ItemIsSelectable) and
            event.scenePos()==event.buttonDownScenePos(QtCore.Qt.LeftButton)):
            multiSelect = event.modifiers() & QtCore.Qt.ControlModifier
            if multiSelect:
                self.setSelected(not self.isSelected())
            else:
                if self.scene():
                    for item in self.scene().selectedItems():
                        if item!=self:
                            item.setSelected(False)
                self.setSelected(True)

class QGraphicsRubberBandItem(QtGui.QGraphicsRectItem):
    """
    QGraphicsRubberBandItem try to replace QRubberBand to have a
    unified look and feel on all platform. In the end, it mimics the
    Windows look. It is just a rectangle with a 50% transparency
    
    """
    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the rubber band
        
        """
        painter.setOpacity(0.5)
        painter.fillRect(self.rect(),
                         CurrentTheme.SELECTION_BOX_BRUSH)
        painter.setOpacity(1.0)
        painter.setPen(CurrentTheme.SELECTION_BOX_PEN)
        painter.drawRect(self.rect())

class QInteractiveGraphicsScene(QtGui.QGraphicsScene):
    """
    QInteractiveGraphicsScene expands QGraphicsScene to allow panning
    freely over the view are
    
    """
    def __init__(self, parent=None):
        """ QInteractiveGraphicsScene(parent: QWidget)
                                      -> QInteractiveGraphicsScene
        Initialize the actual scene bounding rect
        """
        QtGui.QGraphicsScene.__init__(self, parent)
        self.sceneBoundingRect = QtCore.QRectF()
        
    def updateSceneBoundingRect(self):
        """ updateSceneBoundingRect() -> None        
        Compute the actual bounding rect of all shapes, then update
        the scene rect to be much wider for panning
        
        """
        self.sceneBoundingRect = QtCore.QRectF()
        for item in self.items():
            rect = item.sceneBoundingRect()
            self.sceneBoundingRect = self.sceneBoundingRect.united(rect)
        diff = abs(self.sceneBoundingRect.width()-
                   self.sceneBoundingRect.height())
        if self.sceneBoundingRect.width()<self.sceneBoundingRect.height():
            self.sceneBoundingRect.adjust(-diff/2, 0, diff/2, 0)
        else:
            self.sceneBoundingRect.adjust(0, -diff/2, 0, diff/2)
        panRect = self.sceneBoundingRect.adjusted(
            -self.sceneBoundingRect.width()*100,
            -self.sceneBoundingRect.height()*100,
            self.sceneBoundingRect.width()*100,
            self.sceneBoundingRect.height()*100)
        if panRect.width()<1e-6 and panRect.height()<1e-6:
            panRect = QtCore.QRectF(-1000,-1000,2000,2000)
        self.setSceneRect(panRect)

    def fitToView(self, view):
        """ fitToView(view: QGraphicsView) -> None
        Adjust view to fit and center the whole scene
        
        """
        view.centerOn(self.sceneBoundingRect.center())
        view.fitInView(self.sceneBoundingRect, QtCore.Qt.KeepAspectRatio)
            
    def fitToAllViews(self):
        """ fitToAllViews() -> None
        Adjust all views using this scene to fit and center the whole scene
        
        """
        for view in self.views():
            self.fitToView(view)

    def clearItems(self):
        """ clearShapes() -> None
        Remove and delete all items belonging to this scene
        
        """
        self.removeItems(self.items())

    def removeItems(self, itemList):
        """ removeItems(itemList: list [QGraphicsItem]) -> None
        Remove and delete all items in itemList
        
        """
        for item in itemList:
            if item.scene():
                self.removeItem(item)
            del item

class QInteractiveGraphicsView(QtGui.QGraphicsView):
    """
    QInteractiveGraphicsView is QGraphicsView with abilities to
    zoom/span with right/mid click
    
    """
    def __init__(self, parent=None):
        """ QInteractiveGraphicsView(parent: QWidget)
                                     -> QInteractiveGraphicsView
        Initialize the graphics view with interactive options
        
        """
        QtGui.QGraphicsView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setInteractive(True)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.scaleMax = 2000
        self.scaleRatio = self.scaleMax/10
        self.currentScale = self.scaleMax/2
        self.startScroll = (0,0)
        self.lastPos = QtCore.QPoint(0,0)
        self.pipScene = None        
        self.pipFrame = None
        self.selectionBox = QGraphicsRubberBandItem(None)
        self.startSelectingPos = None

    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None        
        Handle mouse click event, use Qt rubber band for left-click
        selection and prepare for zoom/pan on right/mid click
        
        """
        scenePos = self.mapToScene(e.pos())
        item = self.scene().itemAt(scenePos)
        buttons = e.buttons()
        if buttons == QtCore.Qt.LeftButton:
            if item==None:
                if self.scene():
                    self.scene().addItem(self.selectionBox)
                    self.selectionBox.setZValue(1000)
                    
                    self.startSelectingPos = self.mapToScene(e.pos())
                    rect = QtCore.QRectF(self.startSelectingPos,
                                         QtCore.QSizeF(0,0))
                    self.selectionBox.setRect(rect)
                    self.selectionBox.setVisible(True)
            else:
                QtGui.QGraphicsView.mousePressEvent(self, e)
        else:
            if buttons & QtCore.Qt.RightButton:
                self.computeScale()
            elif buttons & QtCore.Qt.MidButton:
                self.startScroll = (self.horizontalScrollBar().value(),
                                    self.verticalScrollBar().value())
            self.lastPos = QtCore.QPoint(QtGui.QCursor.pos())
            self.setDragMode(QtGui.QGraphicsView.NoDrag)

    def mouseMoveEvent(self, e):
        """ mouseMoveEvent(e: QMouseEvent) -> None        
        Handle right click (zoom) and mid click (pan). This function
        uses QtCursor globalPos instead of e.globalX() and e.globalY()
        because of their flaky values during transformation
        
        """
        buttons = e.buttons()
        if buttons == QtCore.Qt.LeftButton:
            if self.startSelectingPos:
                dis = self.mapToScene(e.pos())-self.startSelectingPos
                rect = QtCore.QRectF(self.startSelectingPos,
                                 QtCore.QSizeF(dis.x(), dis.y()))
                self.selectionBox.prepareGeometryChange()
                self.selectionBox.setRect(rect)
                self.selectModules()
            else:
                return QtGui.QGraphicsView.mouseMoveEvent(self, e)
        elif self.lastPos:
            if buttons == QtCore.Qt.RightButton:
                globalPos = QtGui.QCursor.pos()
            
                # Set up new scale based on pixels moved
                newScale = self.currentScale + globalPos.y() - self.lastPos.y()

                # Clamp the scale
                if newScale<0: newScale = 0
                if newScale>self.scaleMax: newScale = self.scaleMax

                # Update the scale and transformation matrix
                self.currentScale = newScale
                self.updateMatrix()

                # Need to update last position
                self.lastPos = QtCore.QPoint(globalPos)
                
            elif buttons == QtCore.Qt.MidButton:
                globalPos = QtGui.QCursor.pos()
                
               # Just need to pan the scroll bar
                self.horizontalScrollBar().setValue(self.startScroll[0] -
                                                    globalPos.x() +
                                                    self.lastPos.x())
                self.verticalScrollBar().setValue(self.startScroll[1] -
                                                  globalPos.y() +
                                                  self.lastPos.y())
        else:
            return QtGui.QGraphicsView.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        """ mouseReleaseEvent(self, e: QMouseEvent) -> None
        Mark box selecting as off
        """
        if self.startSelectingPos:
            self.selectModules()
            self.startSelectingPos = None
            self.selectionBox.setVisible(False)
            self.scene().removeItem(self.selectionBox)
        self.lastPos = None
        QtGui.QGraphicsView.mouseReleaseEvent(self, e)

    def selectModules(self):
        """ selectModules() -> None
        Select all modules inside teh self.selectionBox
        
        """
        path = QtGui.QPainterPath()
        path.addRect(self.selectionBox.sceneBoundingRect())
        self.scene().setSelectionArea(path)
        
    def updateMatrix(self):
        """ updateMatrix() -> None
        Update the view matrix with the current scale
        
        """        
        matrix = QtGui.QMatrix()
        power = float(self.currentScale-self.scaleMax/2)/self.scaleRatio
        scale = pow(2.0, power)
        matrix.scale(scale, scale)
        self.setMatrix(matrix)

    def computeScale(self):
        """ computeScale() -> None
        Compute the current scale based on the view matrix
        
        """
        self.currentScale = (math.log(self.matrix().m11(), 2.0)*
                             self.scaleRatio + self.scaleMax/2)

    def setPIPScene(self, scene):
        """ setPIPScene(scene: QGraphicsScene) -> None        
        Set the Picture-In-Picture scene fo the current GraphicsView
        to 'scene'
        
        """
        self.pipScene = scene

    def setPIPEnabled(self, enabled=True):
        """ setPIPEnabled(enabled: boolean) -> None        
        Enable/Disable PIP view
        
        """
        if self.pipScene:
            if enabled:
                if self.pipFrame==None:
                    self.pipFrame = QPIPGraphicsView(self)
                    self.pipFrame.graphicsView.setScene(self.pipScene)
                    self.pipFrame.move(self.width(), 0)
                self.pipFrame.show()
                self.pipFrame.updateGeometry()
            elif self.pipFrame!=None:
                self.pipFrame.hide()

    def resizeEvent(self, event):
        """ resizeEvent(event: QResizeEvent) -> None
        Make sure the pip frame is inside the graphics view
        """
        if self.pipFrame!=None:
            self.pipFrame.updateGeometry()
        return QtGui.QGraphicsView.resizeEvent(self, event)

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Handle general key-bindings, e.g. 'R' for Reset
        """
        # Reset the view when 'R' is pressed
        if event.key()==QtCore.Qt.Key_R:
            self.scene().fitToView(self)
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """
        return QtCore.QSize(512, 512)

class QPIPGraphicsView(QtGui.QWidget):
    """
    QPIPGraphicsView is a tool window contain a
    QInteractiveGraphicsView for PIP display

    """
    def __init__(self, parent=None):
        """ QPIPGraphicsView(parent: QWidget) -> QPIPGraphicsView
        Initialize a layout with some margin and a central widget
        """
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.palette().setColor(QtGui.QPalette.Base,
                                CurrentTheme.PIP_FRAME_COLOR)
        self.setLayout(QtGui.QHBoxLayout(self))
        self.layout().setMargin(CurrentTheme.PIP_OUT_FRAME_WIDTH)
        self.graphicsView = QInteractiveGraphicsView()
        self.layout().addWidget(self.graphicsView)
        self.firstShow = True
        self.anchorCorner = [QtCore.Qt.AlignRight, QtCore.Qt.AlignTop]

    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """        
        return QtCore.QSize(*CurrentTheme.PIP_DEFAULT_SIZE)
        
    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Capture mouse press event on the frame to move the widget
        
        """
        if e.buttons() & QtCore.Qt.LeftButton:
            self.resizing = False
            self.lastPos = QtCore.QPoint(e.globalX(), e.globalY())
            gvRect = self.graphicsView.geometry()
            if ((e.x()<gvRect.left() or e.x()>gvRect.right()) and
                (e.y()<gvRect.top() or e.y()>gvRect.bottom())):
                self.direction = [1,1]
                if e.x()<gvRect.left():
                    self.direction[0] = -1
                if e.y()<gvRect.top():
                    self.direction[1] = -1
                self.resizing = True

    def mouseMoveEvent(self, e):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Move widget as the mouse moving
        
        """
        if e.buttons() & QtCore.Qt.LeftButton:
            (dx, dy) = (e.globalX()-self.lastPos.x(),
                        e.globalY()-self.lastPos.y())
            parentGeometry = self.parent().geometry()
            newGeometry = QtCore.QRect(self.geometry())
            if self.resizing:
                if self.direction[0]==1:
                    if newGeometry.right()+dx>parentGeometry.width()-1:
                        dx = parentGeometry.width()-1-newGeometry.right()
                    newGeometry.adjust(0, 0, dx, 0)
                else:
                    if newGeometry.left()+dx<0:
                        dx = -newGeometry.left()
                    newGeometry.adjust(dx, 0, 0, 0)
                    
                if self.direction[1]==1:
                    if newGeometry.bottom()+dy>parentGeometry.height()-1:
                        dy = parentGeometry.height()-1-newGeometry.bottom()
                    newGeometry.adjust(0, 0, 0, dy)
                else:
                    if newGeometry.top()+dy<0:
                        dy = -newGeometry.top()
                    newGeometry.adjust(0, dy, 0, 0)
            else:
                newGeometry.translate(dx, dy)
            if (newGeometry.left()>0 and
                newGeometry.right()<parentGeometry.width()-1):
                self.anchorCorner[0] = None
            if (newGeometry.top()>0 and
                newGeometry.bottom()<parentGeometry.height()-1):
                self.anchorCorner[1] = None
            self.updateGeometry(newGeometry)
            self.lastPos = QtCore.QPoint(e.globalX(), e.globalY())

    def updateGeometry(self, newGeometry=None):
        """ updateGeometry() -> None
        Make sure the widget is inside the parent graphics view
        
        """
        parentGeometry = self.parent().geometry()
        if newGeometry==None:
            newGeometry = QtCore.QRect(self.geometry())
            
        if self.anchorCorner[0]==None:
            if newGeometry.left()<0:
                newGeometry.moveLeft(0)
            if newGeometry.right()>=parentGeometry.width():
                newGeometry.moveRight(parentGeometry.width()-1)
            if newGeometry.left()==0:
                self.anchorCorner[0] = QtCore.Qt.AlignLeft
            if newGeometry.right()==parentGeometry.width()-1:
                self.anchorCorner[0] = QtCore.Qt.AlignRight
        else:
            if self.anchorCorner[0]==QtCore.Qt.AlignLeft:
                newGeometry.moveLeft(0)
            if self.anchorCorner[0]==QtCore.Qt.AlignRight:
                newGeometry.moveRight(parentGeometry.width()-1)
                
        if self.anchorCorner[1]==None:
            if newGeometry.top()<0:
                newGeometry.moveTop(0)
            if newGeometry.bottom()>=parentGeometry.height():
                newGeometry.moveBottom(parentGeometry.height()-1)
            if newGeometry.top()==0:
                self.anchorCorner[1] = QtCore.Qt.AlignTop
            if newGeometry.bottom()==parentGeometry.height()-1:
                self.anchorCorner[1] = QtCore.Qt.AlignBottom
        else:
            if self.anchorCorner[1]==QtCore.Qt.AlignTop:
                newGeometry.moveTop(0)
            if self.anchorCorner[1]==QtCore.Qt.AlignBottom:
                newGeometry.moveBottom(parentGeometry.height()-1)
                
        self.setGeometry(newGeometry)

    def showEvent(self, event):
        """ showEvent(event: QShowEvent) -> None
        Fit the scene to view for the show event only
        
        """
        if self.firstShow:
            self.firstShow = False
            self.graphicsView.scene().fitToView(self.graphicsView)
        return QtGui.QWidget.showEvent(self, event)        

    def enterEvent(self, event):
        """ enterEvent(event: QEnterEvent) -> None        
        Show a larger frame when the mouse enter to facilitate
        resizing
        
        """
        self.layout().setMargin(CurrentTheme.PIP_IN_FRAME_WIDTH)

    def leaveEvent(self, event):
        """ leaveEvent(event: QLeaveEvent) -> None        
        Show a smaller frame when the mouse exit the widget to get
        more view
        
        """
        self.layout().setMargin(CurrentTheme.PIP_OUT_FRAME_WIDTH)

    def sizeHint(self):
        """ sizeHint(self) -> QSize
        Return recommended size of the widget
        
        """
        return QtCore.QSize(200, 200)
        
