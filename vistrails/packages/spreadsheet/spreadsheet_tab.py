################################################################################
# This file contains classes controlling tabs in the spreadsheets. A tab is
# a container of a sheet:
#   SizeSpinBox
#   StandardTabDockWidget
#   StandardWidgetSheetTab
#   StandardWidgetTabBar
#   StandardWidgetTabBarEditor
#   StandardWidgetToolBar
################################################################################
from PyQt4 import QtCore, QtGui
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_sheet import StandardWidgetSheet
import spreadsheet_rc

################################################################################

class SizeSpinBox(QtGui.QSpinBox):
    """
    SizeSpinBox is just an overrided spin box that will also emit
    'editingFinished()' signal when the user interact with mouse
    
    """    
    def __init__(self, initValue=0, parent=None):
        """ SizeSpinBox(initValue: int, parent: QWidget) -> SizeSpinBox
        Initialize with a default width of 50 and a value of 0
        
        """
        QtGui.QSpinBox.__init__(self, parent)
        self.setMinimum(1)
        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setValue(initValue)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Emit 'editingFinished()' signal when the user release a mouse button
        
        """
        QtGui.QSpinBox.mouseReleaseEvent(self, event)
        self.emit(QtCore.SIGNAL("editingFinished()"))        

class StandardWidgetToolBar(QtGui.QToolBar):
    """
    StandardWidgetToolBar: The default toolbar for each sheet
    ontainer. By default, only FitToWindow and Table resizing are
    included
    
    """
    def __init__(self, parent=None):
        """ StandardWidgetToolBar(parent: QWidget) -> StandardWidgetToolBar
        Init the toolbar with default actions
        
        """
        QtGui.QToolBar.__init__(self, parent)
        self.sheetTab = parent
        self.addAction(self.fitToWindowAction())
        self.addWidget(self.rowCountSpinBox())
        self.addWidget(self.colCountSpinBox())
        self.layout().setSpacing(2)
        
    def fitToWindowAction(self):
        """ fitToWindowAction() -> QAction
        Return the fit to window action
        
        """
        if not hasattr(self, 'fitAction'):
            icon = QtGui.QIcon(':/images/fittowindow.png')
            self.fitAction = QtGui.QAction(icon, 'Fit to window', self)
            self.fitAction.setStatusTip('Stretch spreadsheet cells '
                                        'to fit the window size')
            self.fitAction.setCheckable(True)
            self.fitAction.setChecked(self.sheetTab.sheet.fitToWindow)
            self.connect(self.fitAction,
                         QtCore.SIGNAL('toggled(bool)'),
                         self.fitActionToggled)
        return self.fitAction

    def fitActionToggled(self, checked):
        """ fitActionToggled(checked: boolean) -> None
        Handle fitToWindow Action toggled
        
        """
        self.sheetTab.sheet.setFitToWindow(checked)
    
    def rowCountSpinBox(self):
        """ rowCountSpinBox() -> SizeSpinBox
        Return the row spin box widget:
        
        """
        if not hasattr(self, 'rowSpinBox'):
            self.rowSpinBox = SizeSpinBox(self.sheetTab.sheet.rowCount())
            self.rowSpinBox.setToolTip('The number of rows')
            self.rowSpinBox.setStatusTip('Change the number of rows '
                                         'of the current sheet')
            self.connect(self.rowSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.rowSpinBoxChanged)
        return self.rowSpinBox

    def colCountSpinBox(self):
        """ colCountSpinBox() -> SizeSpinBox
        Return the column spin box widget:
        
        """
        if not hasattr(self, 'colSpinBox'):
            self.colSpinBox = SizeSpinBox(self.sheetTab.sheet.columnCount())
            self.colSpinBox.setToolTip('The number of columns')
            self.colSpinBox.setStatusTip('Change the number of columns '
                                         'of the current sheet')
            self.connect(self.colSpinBox,
                         QtCore.SIGNAL('editingFinished()'),
                         self.sheetTab.colSpinBoxChanged)
        return self.colSpinBox        
        
            
class StandardWidgetSheetTab(QtGui.QWidget):
    """
    StandardWidgetSheetTab is a container of StandardWidgetSheet with
    a toolbar on top. This will be added directly to a QTabWidget for
    displaying the spreadsheet.
    
    """
    def __init__(self, tabWidget, row=2, col=3):
        """ StandardWidgetSheet(tabWidget: QTabWidget,
                                row: int,
                                col: int) -> StandardWidgetSheet
        Initialize with a toolbar and a sheet widget
                                
        """
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

    def rowSpinBoxChanged(self):
        """ rowSpinBoxChanged() -> None
        Handle the number of row changed
        
        """
        if self.toolBar.rowSpinBox.value()!=self.sheet.rowCount():
            self.sheet.setRowCount(self.toolBar.rowSpinBox.value())
            self.sheet.stretchCells()
        
    def colSpinBoxChanged(self):
        """ colSpinBoxChanged() -> None
        Handle the number of row changed
        
        """
        if self.toolBar.colSpinBox.value()!=self.sheet.columnCount():
            self.sheet.setColumnCount(self.toolBar.colSpinBox.value())
            self.sheet.stretchCells()

    ### Belows are API Wrappers to connect to self.sheet

    def isSheetTabWidget(self):
        """ isSheetTabWidget() -> boolean
        Return True if this is a sheet tab widget
        """
        return True

    def getDimension(self):
        """ getDimension() -> tuple
        Get the sheet dimensions
        
        """
        return (self.sheet.rowCount(), self.sheet.columnCount())
            
    def setDimension(self, rc, cc):
        """ setDimension(rc: int, cc: int) -> None
        Set the sheet dimensions
        
        """
        self.toolBar.rowCountSpinBox().setValue(rc)
        self.toolBar.colCountSpinBox().setValue(cc)
            
    def getCell(self, row, col):
        """ getCell(row: int, col: int) -> QWidget
        Get cell at a specific row and column.
        
        """
        return self.sheet.cellWidget(row, col)

    def getCellToolBar(self, row, col):
        """ getCellToolBar(row: int, col: int) -> QWidget
        Return the toolbar widget at cell location (row, col)
        
        """
        return self.sheet.getCellToolBar(row, col)

    def getCellRect(self, row, col):
        """ getCellRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in parent coordinates
        
        """
        return self.sheet.getCellRect(row, col)

    def getCellGlobalRect(self, row, col):
        """ getCellGlobalRect(row: int, col: int) -> QRect
        Return the rectangle surrounding the cell at location (row, col)
        in global coordinates
        
        """
        return self.sheet.getCellGlobalRect(row, col)

    def getFreeCell(self):
        """ getFreeCell() -> tuple
        Get a free cell location (row, col) on the spreadsheet 

        """
        return self.sheet.getFreeCell()

    def setCellByType(self, row, col, cellType, inputPorts):
        """ setCellByType(row: int,
                          col: int,
                          cellType: a type inherits from QWidget,
                          inpurPorts: tuple) -> None                          
        Replace the current location (row, col) with a cell of
        cellType. If the current type of that cell is the same as
        cellType, only the contents is updated with inputPorts.
        
        """
        self.sheet.setCellByType(row, col, cellType, inputPorts)

    def showHelpers(self, ctrl, globalPos):
        """ showHelpers(ctrl: boolean, globalPos: QPoint) -> None
        Show the helpers (toolbar, resizer) when the Control key
        status is ctrl and the mouse is at globalPos
        
        """
        localPos = self.sheet.viewport().mapFromGlobal(QtGui.QCursor.pos())
        row = self.sheet.rowAt(localPos.y())
        col = self.sheet.columnAt(localPos.x())
        self.sheet.showHelpers(ctrl, row, col)

    def setCellPipelineInfo(self, row, col, info):
        """ setCellPipelineInfo(row: int, col: int, info: any type) -> None        
        Provide a way for the spreadsheet to store vistrail
        information, info, for the cell (row, col)
        
        """
        if not (row,col) in self.pipelineInfo:
            self.pipelineInfo[(row,col)] = {}
        self.pipelineInfo[(row,col)] = info

    def getCellPipelineInfo(self, row, col):
        """ getCellPipelineInfo(row: int, col: int) -> any type        
        Provide a way for the spreadsheet to extract vistrail
        information, info, for the cell (row, col)
        
        """        
        if not (row,col) in self.pipelineInfo:
            return None
        return self.pipelineInfo[(row,col)]

    def getSelectedLocations(self):
        """ getSelectedLocations() -> tuple
        Return the selected locations (row, col) of the current sheet
        
        """
        indexes = self.sheet.selectedIndexes()
        return [(idx.row(), idx.column()) for idx in indexes]

class StandardWidgetTabBarEditor(QtGui.QLineEdit):
    """
    StandardWidgetTabBarEditor overrides QLineEdit to enable canceling
    edit when Esc is pressed
    
    """
    def __init__(self, text='', parent=None):
        """ StandardWidgetTabBarEditor(text: str, parent: QWidget)
                                       -> StandardWidgetTabBarEditor
        Store the original text at during initialization
        
        """
        QtGui.QLineEdit.__init__(self, text, parent)
        self.originalText = text

    def keyPressEvent(self, e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Override keyPressEvent to handle Esc key
        
        """
        if e.key()==QtCore.Qt.Key_Escape:
            e.ignore()
            self.setText(self.originalText)
            self.clearFocus()
        else:
            QtGui.QLineEdit.keyPressEvent(self, e)

class StandardWidgetTabBar(QtGui.QTabBar):
    """
    StandardWidgetTabBar: a customized QTabBar to allow double-click
    to change tab name
    
    """
    def __init__(self, parent=None):
        """ StandardWidgetTabBar(parent: QWidget) -> StandardWidgetTabBar
        Initialize like the original QTabWidget TabBar
        
        """
        QtGui.QTabBar.__init__(self, parent)
        self.setStatusTip('Move the sheet in, out and around'
                          'by dragging the tabs')
        self.setDrawBase(False)
        self.editingIndex = -1
        self.editor = None        
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'),
                     self.updateTabText)
        self.startDragPos = None
        self.dragging = False
        self.targetTab = -1
        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)
        self.outerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 None)

    def mouseDoubleClickEvent(self, e):
        """ mouseDoubleClickEvent(e: QMouseEvent) -> None
        Handle Double-Click event to start the editor
        
        """
        if e.buttons()!=QtCore.Qt.LeftButton or self.editor: return
        
        # Update the current editing tab widget
        self.editingIndex = self.currentIndex()
        
        # A hack to capture the rect of the triangular tab from commonstyle.cpp
        rect = self.tabRect(self.editingIndex)
        h = rect.height()-2
        dx = h/3 + 3
        rect.adjust(dx+1,1,-dx,-1)

        # Display the editor inplace of the tab text
        text = self.tabText(self.editingIndex)
        self.editor = StandardWidgetTabBarEditor(text, self)
        self.editor.setFont(self.font())
        self.editor.setFrame(False)
        self.editor.setGeometry(rect)
        self.editor.setAlignment(QtCore.Qt.AlignHCenter)
        self.editor.selectAll()
        self.connect(self.editor, QtCore.SIGNAL('editingFinished()'),
                     self.updateTabText)
        self.editor.show()
        self.editor.setFocus(QtCore.Qt.MouseFocusReason)

    def updateTabText(self, idx=0):
        """ updateTabText(idx: int) -> None
        Update the tab text after editing has been finished
        
        """
        if self.editingIndex>=0 and self.editor:
            self.setTabText(self.editingIndex, self.editor.text())
            self.emit(QtCore.SIGNAL('tabTextChanged(int,QString)'),
                      self.editingIndex,self.editor.text())
            self.editor.deleteLater()
            self.editingIndex = -1
            self.editor = None

    def indexAtPos(self, p):
        """ indexAtPos(p: QPoint) -> int Reimplement of the private
        indexAtPos to find the tab index under a point
        
        """
        if self.tabRect(self.currentIndex()).contains(p):
            return self.currentIndex()
        for i in range(self.count()):
            if self.isTabEnabled(i) and self.tabRect(i).contains(p):                
                return i
        return -1;

    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Handle mouse press event to see if we should start to drag tabs or not
        
        """
        QtGui.QTabBar.mousePressEvent(self, e)
        if e.buttons()==QtCore.Qt.LeftButton and self.editor==None:
            self.startDragPos = QtCore.QPoint(e.x(), e.y())

    def getGlobalRect(self, index):
        """ getGlobalRect(self, index: int)
        Get the rectangle of a tab in global coordinates
        
        """
        if index<0: return None
        rect = self.tabRect(index)
        rect.moveTo(self.mapToGlobal(rect.topLeft()))
        return rect

    def highlightTab(self, index):
        """ highlightTab(index: int)
        Highlight the rubber band of a tab
        
        """
        if index==-1:
            self.innerRubberBand.hide()
        else:
            self.innerRubberBand.setGeometry(self.tabRect(index))
            self.innerRubberBand.show()
            
    def mouseMoveEvent(self, e):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Handle dragging tabs in and out or around
        
        """
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
                        index = self.getGlobalRect(self.currentIndex())
                        self.outerRubberBand.setGeometry(index)
                        self.outerRubberBand.move(e.globalPos())
                        self.outerRubberBand.show()
                    else:
                        self.outerRubberBand.move(e.globalPos())

    def mouseReleaseEvent(self, e):
        """ mouseReleaseEvent(e: QMouseEvent) -> None
        Make sure the tab moved at the end
        
        """
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
            
    def slotIndex(self, pos):
        """ slotIndex(pos: QPoint) -> int
        Return the slot index between the slots at the cursor pos
        
        """
        p = self.mapFromGlobal(pos)
        for i in range(self.count()):
            r = self.tabRect(i)
            if self.isTabEnabled(i) and r.contains(p):
                if p.x()<(r.x()+r.width()/2):
                    return i
                else:
                    return i+1
        return -1
        
    def slotGeometry(self, idx):
        """ slotGeometry(idx: int) -> QRect
        Return the geometry between the slots at cursor pos
        
        """
        if idx<0 or self.count()==0: return None
        if idx<self.count():
            rect = self.getGlobalRect(idx)
            rect = QtCore.QRect(rect.x()-5, rect.y(), 5*2, rect.height())
            return rect
        else:
            rect = self.getGlobalRect(self.count()-1)
            rect = QtCore.QRect(rect.x()+rect.width()-5, rect.y(),
                                5*2, rect.height())
            return rect
            
class StandardTabDockWidget(QtGui.QDockWidget):
    """
    StandardTabDockWidget inherits from QDockWidget to contain a sheet
    widget floating around that can be merge back to tab controller
    
    """
    def __init__(self, title, tabWidget, tabBar, tabController):
        """ StandardTabDockWidget(title: str,
                                  tabWidget: QTabWidget,
                                  tabBar: QTabBar,
                                  tabController: StandardWidgetTabController)
                                  -> StandardTabDockWidget
        Initialize the dock widget to override the floating button
        
        """
        QtGui.QDockWidget.__init__(self, title, tabBar,
                                   QtCore.Qt.FramelessWindowHint)
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
        self.windowRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                  None)
        tabWidget.setParent(self)
        self.setWidget(tabWidget)
        tabWidget.show()
        self.resize(tabWidget.size())

    def findFloatingButton(self):
        """ findFloatingButton() -> QAbstractButton        
        Hack to find the private Floating Button. Since there is only
        one button exists, we just need to find QAbstractButton
        
        """
        for c in self.children():
            if type(c)==QtGui.QAbstractButton:
                return c
        return None

    def eventFilter(self, q, e):
        """ eventFilter(q: QObject, e: QEvent) -> depends on event type
        Event filter the floating button to makes it merge to the tab controller
        
        """
        if q and q==self.floatingButton:
            if (e.type()==QtCore.QEvent.MouseButtonRelease and
                e.button()&QtCore.Qt.LeftButton):
                if self.isMaximized():
                    self.showNormal()
                else:
                    self.showMaximized()
                return False
        return QtGui.QDockWidget.eventFilter(self, q, e)

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle movement of the dock widget to snap to the tab controller
        
        """
        if e.type()==QtCore.QEvent.MouseButtonPress:
            # Click on the title bar
            if e.y()<self.widget().y() and e.buttons()&QtCore.Qt.LeftButton:
                self.startDragPos = QtCore.QPoint(e.globalPos().x(),
                                                  e.globalPos().y())
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
                    rect = QtCore.QRect(self.startDragPos+e.globalPos(),
                                        self.size())
                    self.windowRubberBand.setGeometry(rect)
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

spreadsheetRegistry.registerSheet('StandardWidgetSheetTab',
                                  StandardWidgetSheetTab)
