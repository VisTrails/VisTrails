from PyQt4 import QtCore, QtGui

################################################################################
################################################################################
### CellResizerConfig: a triangular shape configuration of CellResizer
class CellResizerConfig(object):
    ### Create mask and pixmap for the shape    
    def __init__(self, size=25, color=QtGui.QColor(0,0,0)):
        self.size = size
        self.transparentColor = QtGui.QColor(QtCore.Qt.blue)
        self.image = QtGui.QImage(size,size,QtGui.QImage.Format_RGB32)
        for i in range(size):
            for j in range(size):
                if i+j<size-1:
                    self.image.setPixel(i, j, self.transparentColor.rgb())
                else:
                    if i+j==size-1 or i==size-1 or j==size-1:
                        self.image.setPixel(i, j, QtGui.QColor(QtCore.Qt.white).rgb())
                    else:
                        self.image.setPixel(i, j, color.rgb())
        self.pixmapVar = self.maskVar = self.cursorVar = None

    def pixmap(self):
        if not self.pixmapVar:
            self.pixmapVar = QtGui.QPixmap.fromImage(self.image)
        return self.pixmapVar

    def mask(self):
        if not self.maskVar:
            self.maskVar = QtGui.QRegion(self.pixmap().createMaskFromColor(self.transparentColor))
        return self.maskVar

    def cursor(self):
        return QtGui.QCursor(QtCore.Qt.SizeFDiagCursor)


################################################################################
################################################################################
### CellResizer: a triangular shape SizeGrip that stays on top of the
### widget, moving this size grip will end up resizing the
### corresponding column and row in the table. This is different from
### QSizeGrip because it allows overlapping on top of the widget
class CellResizer(QtGui.QLabel):

    ### Initialize the size grip with triangular shape
    def __init__(self, sheet, config=CellResizerConfig(), parent=None):
        QtGui.QLabel.__init__(self,sheet)#QtGui.QApplication.desktop().screen(0), QtCore.Qt.ToolTip)
        self.setMouseTracking(False)
        self.setFixedSize(config.size, config.size)
        self.setPixmap(config.pixmap())
        self.setMask(config.mask())
        self.setCursor(config.cursor())
        self.setStatusTip("Left/Right-click drag to resize the underlying cell or the whole spreadsheet ")
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sheet = sheet
        self.config = config
        self.resizeAll = False
        self.dragging = False
        self.lastPos = None
        self.row = -1
        self.col = -1
        self.hide()

    ### Is the resizer busy dragging?
    def setDragging(self,b):
        self.dragging = b

    ### Assign which row and column the resizer should resize
    def snapTo(self,row,col):
        self.row = row
        self.col = col

    ### Adjust resizer position to be on the bottom-right corner of the cell
    def adjustPosition(self, rect):
        p = self.parent().mapFromGlobal(rect.topLeft())
        self.move(p.x()+rect.width()-self.width(),
                  p.y()+rect.height()-self.height())

    ### Are we resizing using Left or Right Button?
    def mousePressEvent(self,e):
        if self.col>=0:
            if e.button()==QtCore.Qt.LeftButton:
                self.resizeAll = False
                self.dragging = True
                self.lastPos = QtCore.QPoint(e.globalX(),e.globalY())
            if e.button()==QtCore.Qt.RightButton and not self.sheet.fitToWindow:
                self.resizeAll = True
                self.dragging = True
                self.lastPos = QtCore.QPoint(e.globalX(),e.globalY())

    ### Clean up all states
    def mouseReleaseEvent(self,e):
        ctrl = e.modifiers()&QtCore.Qt.ControlModifier
        self.sheet.showHelpers(ctrl, self.row, self.col)
        if e.button()==QtCore.Qt.LeftButton or e.button()==QtCore.Qt.RightButton:
            self.dragging = False

    ### Interactively resize the corresponding column and row
    def mouseMoveEvent(self,e):
        if self.dragging:
            hd = e.globalX() - self.lastPos.x()
            vd = e.globalY() - self.lastPos.y()
            self.lastPos.setX(e.globalX())
            self.lastPos.setY(e.globalY())
            hSize = self.sheet.columnWidth(self.col)
            vSize = self.sheet.rowHeight(self.row)
            fit = self.sheet.fitToWindow
            
            # All sections should have the same size (Right-Click)
            if self.resizeAll:
                # Resize the columnds first
                dS = int(hd / (self.col+1))
                mS = hd % (self.col+1)
                for i in range(self.sheet.columnCount()):                    
                    if i>self.col:
                        newValue = hSize+dS
                    else:
                        newValue = self.sheet.columnWidth(i)+dS+(i<mS)
                    self.sheet.setColumnWidth(i, newValue)
                # Then resize the rows
                dS = int(vd / (self.row+1))
                mS = vd % (self.row+1)
                for i in range(self.sheet.rowCount()):                    
                    if i>self.row:
                        newValue = vSize+dS
                    else:
                        newValue = self.sheet.rowHeight(i)+dS+(i<mS)
                    self.sheet.setRowHeight(i, newValue)

            # Only resize the corresponding column and row (Left-Click)
            else:
                self.sheet.setColumnWidth(self.col, hSize+hd)
                self.sheet.setRowHeight(self.row, vSize+vd)
            rect = self.sheet.getCellRect(self.row, self.col)
            rect.moveTo(self.sheet.viewport().mapToGlobal(rect.topLeft()))
            self.adjustPosition(rect)

################################################################################
################################################################################
### CellToolBar: inherited from QToolBar with some functionalities for
### interacting with CellHelpers
class CellToolBar(QtGui.QToolBar):

    ### Init the cell tool bar to be floating like the cell resizer
    def __init__(self, sheet):
        QtGui.QToolBar.__init__(self,sheet)
        self.setAutoFillBackground(True)
        self.sheet = sheet
        self.row = -1
        self.col = -1
        self.createToolBar()

    ### An empty for inherited classes to initialize
    def createToolBar(self):
        pass

    ### When the mouse enters the widget, make sure it's a Popup
    def aenterEvent(self, e):
        if self.windowFlags()!=QtCore.Qt.Popup:
            self.setWindowFlags(QtCore.Qt.Popup)
            self.show()

    ### When the mouse leaves the widget, make sure it's a ToolTip
    def aleaveEvent(self, e):
        if self.windowFlags()!=QtCore.Qt.ToolTip:
            self.hide()
            self.setWindowFlags(QtCore.Qt.ToolTip)
            self.setVisible(self.isVisible())

    ### Snap to a specific cell for position
    def snapTo(self, row, col):
        self.row = row
        self.col = col
        self.updateToolBar()

    ### Adjust the position of the toolbar to be top-left
    def adjustPosition(self, rect):
        self.adjustSize()
        p = self.parent().mapFromGlobal(rect.topLeft())
        self.move(p.x(), p.y())

    ### Update status of all toolbar widgets
    def updateToolBar(self):
        cellWidget = self.sheet.getCell(self.row, self.col)
        for action in self.actions():
            action.emit(QtCore.SIGNAL('needUpdateStatus'),
                        (self.sheet, self.row, self.col, cellWidget))

    ### Connect action to special slots from the widget
    def connectAction(self, action, widget):
        if hasattr(widget, 'updateStatus'):
            self.connect(action, QtCore.SIGNAL('needUpdateStatus'), widget.updateStatus)
        if hasattr(widget, 'triggeredSlot'):
            self.connect(action, QtCore.SIGNAL('triggered()'), widget.triggeredSlot)
        if hasattr(widget, 'toggledSlot'):
            self.connect(action, QtCore.SIGNAL('toggled(bool)'), widget.toggledSlot)

    ### Setup and add action to the tool bar
    def appendAction(self, action):
        action.toolBar = self
        self.addAction(action)
        self.connectAction(action, action)
        return action

    ### Setup and add widget to the tool bar
    def appendWidget(self, widget):
        action = self.addWidget(widget)
        widget.toolBar = self
        action.toolBar = self
        self.connectAction(action, widget)
        return action

    ### Return the snapped widget
    def getSnappedWidget(self):
        if self.row>=0 and self.col>=0:
            return self.sheet.getCell(self.row, self.col)
        else:
            return None

################################################################################
################################################################################
### CellHelpers: a container include CellResizer and CellToolbar that
### will shows up whenever the Ctrl key is hold down and the mouse
### hovers.
class CellHelpers(object):
    
    ### Initialize with no tool bar and a cell resizer
    def __init__(self, sheet, resizerInstance=None, toolBarInstance=None):
        self.sheet = sheet
        self.resizer = resizerInstance
        self.toolBar = toolBarInstance
        self.row = -1
        self.col = -1
        
    ### Assign the resizer and toolbar to the correct cell
    def snapTo(self, row, col):
        if row>=0 and ((row!=self.row) or (col!=self.col)):
            self.hide()
            self.row = row
            self.col = col
            if self.resizer:
                self.resizer.snapTo(row,col)
            toolBar = self.sheet.getCellToolBar(row, col)
            if toolBar!=self.toolBar:
                if self.toolBar:
                    self.toolBar.hide()
                self.toolBar = toolBar
            if self.toolBar:
                self.toolBar.snapTo(row,col)
            self.adjustPosition()

    ### Adjust both the toolbar and the resizer
    def adjustPosition(self):
        rect = self.sheet.getCellGlobalRect(self.row, self.col)
        if self.resizer:
            self.resizer.adjustPosition(rect)
        if self.toolBar:
            self.toolBar.adjustPosition(rect)

    ### An helper function derived from setVisible
    def show(self):
        self.setVisible(True)

    ### An helper function derived from setVisible
    def hide(self):
        self.setVisible(False)

    ### Show/hide the helpers
    def setVisible(self,b):
        if self.resizer:
            self.resizer.setVisible(b)
        if not b and self.resizer:
            self.resizer.setDragging(False)
        if self.toolBar:
            self.toolBar.setVisible(b)

    ### Is the helper in action with the resizer
    def isInteracting(self):
        if self.resizer:
            return self.resizer.dragging
        else:
            return False
