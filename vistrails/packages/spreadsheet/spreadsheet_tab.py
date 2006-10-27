from PyQt4 import QtCore, QtGui
from spreadsheet_sheet import *
import spreadsheet_rc
from spreadsheet_registry import spreadsheetRegistry

################################################################################
################################################################################
### SizeSpinBox: this is just an overrided spin box that will also
### emit 'editingFinished()' signal when the user interact with mouse
class SizeSpinBox(QtGui.QSpinBox):
    def __init__(self, initValue=0, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        self.setMinimum(1)
        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setValue(initValue)

    def mouseReleaseEvent(self, event):
        QtGui.QSpinBox.mouseReleaseEvent(self, event)
        self.emit(QtCore.SIGNAL("editingFinished()"))
        

################################################################################
################################################################################
### StandardWidgetToolBar: The default toolbar for each sheet
### container. By default, only FitToWindow and Table resizing are
### included
class StandardWidgetToolBar(QtGui.QToolBar):

    ### Init with default actions
    def __init__(self, parent=None):
        QtGui.QToolBar.__init__(self, parent)
        self.sheetTab = parent
        self.addAction(self.fitToWindowAction())
        self.addWidget(self.rowCountSpinBox())
        self.addWidget(self.colCountSpinBox())
        self.layout().setSpacing(2)
        
    ### Return the fit to window action
    def fitToWindowAction(self):
        if not hasattr(self, 'fitAction'):
            self.fitAction = QtGui.QAction(QtGui.QIcon(':/images/fittowindow.png'),
                                   'Fit to window', self)
            self.fitAction.setStatusTip('Stretch spreadsheet cells to fit the window size')
            self.fitAction.setCheckable(True)
            self.fitAction.setChecked(self.sheetTab.sheet.fitToWindow)
            self.connect(self.fitAction,
                         QtCore.SIGNAL('toggled(bool)'),
                         self.fitActionToggled)
        return self.fitAction

    ### Handle fitToWindow Action toggled
    def fitActionToggled(self, checked):
        self.sheetTab.sheet.setFitToWindow(checked)
    
    ### Return the row spin box widget:
    def rowCountSpinBox(self):
        if not hasattr(self, 'rowSpinBox'):
            self.rowSpinBox = SizeSpinBox(self.sheetTab.sheet.rowCount())
            self.rowSpinBox.setToolTip('The number of rows')
            self.rowSpinBox.setStatusTip('Change the number of rows of the current sheet')
            self.connect(self.rowSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.rowSpinBoxChanged)
        return self.rowSpinBox

    ### Return the row spin box widget:
    def colCountSpinBox(self):
        if not hasattr(self, 'colSpinBox'):
            self.colSpinBox = SizeSpinBox(self.sheetTab.sheet.columnCount())
            self.colSpinBox.setToolTip('The number of columns')
            self.colSpinBox.setStatusTip('Change the number of columns of the current sheet')
            self.connect(self.colSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.colSpinBoxChanged)
        return self.colSpinBox        
        
            
################################################################################
################################################################################
### StandardWidgetSheetTab: a container of StandardWidgetSheet with a
### toolbar on top. This will be added directly to a QTabWidget for
### displaying the spreadsheet.
class StandardWidgetSheetTab(QtGui.QWidget):

    ### Init with the initial vertical layout
    def __init__(self, tabWidget, row=2, col=3):
        QtGui.QWidget.__init__(self, None)
        self.type = 'StandardWidgetSheetTab'
        self.tabWidget = tabWidget
        self.sheet = StandardWidgetSheet(row, col, self)
        self.sheet.setFitToWindow(True)
        self.toolBar = StandardWidgetToolBar(self)
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setSpacing(0)
        self.vLayout.setMargin(0)
        self.vLayout.addWidget(self.toolBar, 0)
        self.vLayout.addWidget(self.sheet, 1)
        self.setLayout(self.vLayout)
        self.pipelineInfo = {}

    ### Handle the number of row changed
    def rowSpinBoxChanged(self):
        if self.toolBar.rowSpinBox.value()!=self.sheet.rowCount():
            self.sheet.setRowCount(self.toolBar.rowSpinBox.value())
            self.sheet.stretchCells()
        
    ### Handle the number of row changed
    def colSpinBoxChanged(self):
        if self.toolBar.colSpinBox.value()!=self.sheet.columnCount():
            self.sheet.setColumnCount(self.toolBar.colSpinBox.value())
            self.sheet.stretchCells()

    ### Belows are API Wrappers to connect to self.sheet

    ### Return True if this is a sheet tab widget
    def isSheetTabWidget(self):
        return True

    ### Get the sheet dimensions
    def getDimension(self):
        return (self.sheet.rowCount(), self.sheet.columnCount())
            
    ### Set the sheet dimensions
    def setDimension(self, rc, cc):
        self.toolBar.rowCountSpinBox().setValue(rc)
        self.toolBar.colCountSpinBox().setValue(cc)
            
    ### Get cell at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCell(self, row, col):
        return self.sheet.cellWidget(row, col)

    ### Get cell toolbar at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellToolBar(self, row, col):
        return self.sheet.getCellToolBar(row, col)

    ### Get the cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellRect(self, row, col):
        return self.sheet.getCellRect(row, col)

    ### Get the global cell rectangle at a specific row and column
    ### Just a wrapper to interact with a general spreadsheet
    def getCellGlobalRect(self, row, col):
        return self.sheet.getCellGlobalRect(row, col)

    ### Get a free cell on the spreadsheet
    def getFreeCell(self):
        return self.sheet.getFreeCell()

    ### Create a cell based on celltype, location and input ports
    def setCellByType(self, row, col, cellType, inputPorts):
        self.sheet.setCellByType(row, col, cellType, inputPorts)

    ### Show the helpers at a location p
    def showHelpers(self, ctrl, globalPos):
        localPos = self.sheet.viewport().mapFromGlobal(QtGui.QCursor.pos())
        row = self.sheet.rowAt(localPos.y())
        col = self.sheet.columnAt(localPos.x())
        self.sheet.showHelpers(ctrl, row, col)

    ### Set information about a vistrail cell
    def setCellPipelineInfo(self, row, col, info):
        if not (row,col) in self.pipelineInfo:
            self.pipelineInfo[(row,col)] = {}
        self.pipelineInfo[(row,col)] = info

    ### Get information about a vistrail cell
    def getCellPipelineInfo(self, row, col):
        if not (row,col) in self.pipelineInfo:
            return None
        return self.pipelineInfo[(row,col)]

    ### Return the selected locations (row, col) of the current sheet
    def getSelectedLocations(self):
        indexes = self.sheet.selectedIndexes()
        return [(idx.row(), idx.column()) for idx in indexes]

################################################################################
################################################################################
### StandardWidgetTabBarEditor: override QLineEdit to enable
### canceling edit when Esc is pressed
class StandardWidgetTabBarEditor(QtGui.QLineEdit):

    ### Store the original text at during initialization
    def __init__(self, text='', parent=None):
        QtGui.QLineEdit.__init__(self, text, parent)
        self.originalText = text

    ### Override keyPressEvent to handle Esc key
    def keyPressEvent(self, e):
        if e.key()==QtCore.Qt.Key_Escape:
            e.ignore()
            self.setText(self.originalText)
            self.clearFocus()
        else:
            QtGui.QLineEdit.keyPressEvent(self, e)

################################################################################
################################################################################
### StandardWidgetTabBar: a customized QTabBar to allow
### double-click to change tab nam
class StandardWidgetTabBar(QtGui.QTabBar):

    ### Initialize like the original QTabWidget TabBar
    def __init__(self, parent=None):
        QtGui.QTabBar.__init__(self, parent)
        self.setStatusTip('Move the sheet in, out and around  by dragging the tabs')
        self.setDrawBase(False)
        self.editingIndex = -1
        self.editor = None        
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'), self.updateTabText)
        self.startDragPos = None
        self.dragging = False
        self.targetTab = -1
        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.outerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, None)

    ### Handle Double-Click event
    def mouseDoubleClickEvent(self, e):
        if e.buttons()!=QtCore.Qt.LeftButton or self.editor: return
        
        # Update the current editing tab widget
        self.editingIndex = self.currentIndex()
        
        # A hack to capture the rect of the triangular tab from commonstyle.cpp
        rect = self.tabRect(self.editingIndex)
        h = rect.height()-2
        dx = h/3 + 3
        rect.adjust(dx+1,1,-dx,-1)

        # Display the editor inplace of the tab text
        self.editor = StandardWidgetTabBarEditor(self.tabText(self.editingIndex), self)
        self.editor.setFont(self.font())
        self.editor.setFrame(False)
        self.editor.setGeometry(rect)
        self.editor.setAlignment(QtCore.Qt.AlignHCenter)
        self.editor.selectAll()
        self.connect(self.editor, QtCore.SIGNAL('editingFinished()'), self.updateTabText)
        self.editor.show()
        self.editor.setFocus(QtCore.Qt.MouseFocusReason)

    ### Update the tab text after editing has been finished
    def updateTabText(self, idx=0):
        if self.editingIndex>=0 and self.editor:
            self.setTabText(self.editingIndex, self.editor.text())
            self.emit(QtCore.SIGNAL('tabTextChanged(int,QString)'),
                      self.editingIndex,self.editor.text())
            self.editor.deleteLater()
            self.editingIndex = -1
            self.editor = None

    ### Reimplement of the private indexAtPos to find the tab index under a point
    def indexAtPos(self, p):
        if self.tabRect(self.currentIndex()).contains(p):
            return self.currentIndex()
        for i in range(self.count()):
            if self.isTabEnabled(i) and self.tabRect(i).contains(p):                
                return i
        return -1;

    ### Handle mouse press event to see if we should start to drag tabs or not
    def mousePressEvent(self, e):
        QtGui.QTabBar.mousePressEvent(self, e)
        if e.buttons()==QtCore.Qt.LeftButton and self.editor==None:
            self.startDragPos = QtCore.QPoint(e.x(), e.y())

    ### Get the rectangle of a tab in global coordinates
    def getGlobalRect(self, index):
        if index<0: return None
        rect = self.tabRect(index)
        rect.moveTo(self.mapToGlobal(rect.topLeft()))
        return rect

    ### Highlight the rubber band of a tab
    def highlightTab(self, index):
        if index==-1:
            self.innerRubberBand.hide()
        else:
            self.innerRubberBand.setGeometry(self.tabRect(index))
            self.innerRubberBand.show()
            
    ### Handle dragging action
    def mouseMoveEvent(self, e):
        QtGui.QTabBar.mouseMoveEvent(self, e)
        if self.startDragPos:
            # We already move more than 4 pixels
            if (self.startDragPos-e.pos()).manhattanLength()>=4:
                self.startDragPos = None
                self.dragging = True
        if self.dragging:
            t = self.indexAtPos(e.pos())
            if t!=-1:
                if t!=self.targetTab:                    
                    self.targetTab = t
                    self.outerRubberBand.hide()
                    self.highlightTab(t)
            else:
                self.highlightTab(-1)
                if t!=self.targetTab:
                    self.targetTab = t
                if self.count()>0:
                    if not self.outerRubberBand.isVisible():
                        self.outerRubberBand.setGeometry(self.getGlobalRect(self.currentIndex()))
                        self.outerRubberBand.move(e.globalPos())
                        self.outerRubberBand.show()
                    else:
                        self.outerRubberBand.move(e.globalPos())

    ### Make sure the tab moved at the end
    def mouseReleaseEvent(self, e):
        QtGui.QTabBar.mouseReleaseEvent(self, e)
        if self.dragging:
            if self.targetTab!=-1 and self.targetTab!=self.currentIndex():
                self.emit(QtCore.SIGNAL('tabMoveRequest(int,int)'),
                          self.currentIndex(),
                          self.targetTab)
            elif self.targetTab==-1:
                self.emit(QtCore.SIGNAL('tabSplitRequest(int,QPoint)'),
                          self.currentIndex(),
                          e.globalPos())
            self.dragging = False
            self.targetTab = -1
            self.highlightTab(-1)
            self.outerRubberBand.hide()
    ### Return the slot index between the slots at the cursor pos
    def slotIndex(self, pos):
        p = self.mapFromGlobal(pos)
        for i in range(self.count()):
            r = self.tabRect(i)
            if self.isTabEnabled(i) and r.contains(p):
                if p.x()<(r.x()+r.width()/2):
                    return i
                else:
                    return i+1
        return -1
        
    ### Return the geometry between the slots at cursor pos
    def slotGeometry(self, idx):
        if idx<0 or self.count()==0: return None
        if idx<self.count():
            rect = self.getGlobalRect(idx)
            rect = QtCore.QRect(rect.x()-5, rect.y(), 5*2, rect.height())
            return rect
        else:
            rect = self.getGlobalRect(self.count()-1)
            rect = QtCore.QRect(rect.x()+rect.width()-5, rect.y(), 5*2, rect.height())
            return rect
            

################################################################################
################################################################################
### StandardTabDockWidget: inherited from QDockWidget to contain
### a sheet widget floating around that can be merge back to tab controller
class StandardTabDockWidget(QtGui.QDockWidget):

    ### Initialize the dock widget to override the floating button
    def __init__(self, title, tabWidget, tabBar, tabController):
        QtGui.QDockWidget.__init__(self, title, tabBar, QtCore.Qt.FramelessWindowHint)
        self.tabBar = tabBar
        self.tabController = tabController
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                         QtGui.QDockWidget.DockWidgetFloatable)
        self.setFloating(True)
        self.floatingButton = self.findFloatingButton()
        if self.floatingButton:
            self.floatingButton.blockSignals(True)
            self.floatingButton.installEventFilter(self)
        self.startDragPos = None
        self.startDragging = False
        self.windowRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, None)
        tabWidget.setParent(self)
        self.setWidget(tabWidget)
        tabWidget.show()
        self.resize(tabWidget.size())

    ### Hack to find the private Floating Button
    ### Since there is only one button exists, we just need to find QAbstractButton
    def findFloatingButton(self):
        for c in self.children():
            if type(c)==QtGui.QAbstractButton:
                return c
        return None

    ### Event filter the floating button to makes it merge to the tab controller
    def eventFilter(self, q, e):
        if q and q==self.floatingButton:
            if (e.type()==QtCore.QEvent.MouseButtonRelease and
                e.button()&QtCore.Qt.LeftButton):
                if self.isMaximized():
                    self.showNormal()
                else:
                    self.showMaximized()
                return False
        return QtGui.QDockWidget.eventFilter(self, q, e)

    ### Handle movement of the dock widget to snap to the tab controller
    def event(self, e):
        if e.type()==QtCore.QEvent.MouseButtonPress:
            # Click on the title bar
            if e.y()<self.widget().y() and e.buttons()&QtCore.Qt.LeftButton:
                self.startDragPos = QtCore.QPoint(e.globalPos().x(),e.globalPos().y())
        elif e.type()==QtCore.QEvent.MouseMove:
            if not (e.buttons()&QtCore.Qt.LeftButton):
                self.windowRubberBand.hide()
                self.setMouseTracking(False)
                return QtGui.QDockWidget.event(self, e)
            if (not self.startDragging and
                self.startDragPos and
                (self.startDragPos-e.globalPos()).manhattanLength()>=4):
                self.startDragging = True
                self.windowRubberBand.setGeometry(self.geometry())
                self.startDragPos = self.pos()-e.globalPos()
                self.windowRubberBand.show()
                self.setMouseTracking(True)
            if self.startDragging:
                tb = QtGui.QApplication.widgetAt(e.globalPos())
                if tb==self.tabBar:
                    idx = tb.slotIndex(e.globalPos())
                    if idx>=0:
                        self.windowRubberBand.setGeometry(tb.slotGeometry(idx))
                else:
                    self.windowRubberBand.setGeometry(QtCore.QRect(self.startDragPos+e.globalPos(),
                                                                   self.size()))
        elif e.type()==QtCore.QEvent.MouseButtonRelease and self.startDragging:
            self.setMouseTracking(False)
            self.windowRubberBand.hide()
            self.startDragPos = None
            self.startDragging = False
            tb = QtGui.QApplication.widgetAt(e.globalPos())
            if tb==self.tabBar:
                idx = tb.slotIndex(e.globalPos())
                if idx>=0:
                    self.hide()
                    self.tabController.mergeTab(self, idx)
                    return False
            else:
                self.move(self.windowRubberBand.pos())
        elif (e.type()==QtCore.QEvent.MouseButtonDblClick and
              e.button()&QtCore.Qt.LeftButton):
            self.hide()
            self.tabController.mergeTab(self, self.tabController.count())
            return False
            
        return QtGui.QDockWidget.event(self, e)

spreadsheetRegistry.registerSheet('StandardWidgetSheetTab', StandardWidgetSheetTab)
