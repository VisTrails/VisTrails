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
""" This common widgets using on the interface of VisTrails. These are
only simple widgets in term of coding and additional features. It
should have no interaction with VisTrail core"""
import os

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.modules.constant_configuration import StandardConstantWidget
from vistrails.core.system import systemType, set_vistrails_data_directory
################################################################################

class QToolWindow(QtGui.QDockWidget):
    """
    QToolWindow is a floating-dockable widget. It also keeps track of
    its widget window title to update the tool window accordingly
    
    """
    def __init__(self, widget=None, parent=None):
        """ QToolWindow(parent: QWidget) -> QToolWindow
        Construct a floating, dockable widget
        
        """
        QtGui.QDockWidget.__init__(self, parent)
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)  
        self.mwindow = QtGui.QMainWindow(self)
        self.centralwidget = widget
        self.mwindow.setWindowFlags(QtCore.Qt.Widget) 
        self.mwindow.setCentralWidget(widget)     
        self.setWidget(self.mwindow)
        self.createToolBar()
        if widget:
            self.setWindowTitle(widget.windowTitle())
        self.pinStatus = False
        self.monitorWindowTitle(widget)
        
        self.connect(self, QtCore.SIGNAL("topLevelChanged(bool)"),
                     self.setDefaultPinStatus)
             
    def createToolBar(self):
        self.toolbar = QtGui.QToolBar(self.mwindow)
        self.pinButton = QtGui.QAction(CurrentTheme.UNPINNED_PALETTE_ICON,
                                       "", self.toolbar,checkable=True,
                                       checked=False,
                                       toggled=self.pinStatusChanged)
        
        self.pinButton.setToolTip("Pin this on the Tab Bar")
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                             QtGui.QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.pinButton)
        self.pinAction = self.pinButton
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QtCore.QSize(16,16))
        self.mwindow.addToolBar(self.toolbar)
                   
    def setDefaultPinStatus(self, topLevel):
        # Fixes QTBUG-30276
        if self.acceptDrops():
            self.setAcceptDrops(False)
            self.setAcceptDrops(True)
        if topLevel:
            self.setPinStatus(False)
            self.pinButton.setEnabled(False)
        else:
            self.pinButton.setEnabled(True)
        
    def pinStatusChanged(self, pinStatus):
        self.pinStatus = pinStatus
        self.updateButtonIcon(pinStatus)
        
    def updateButtonIcon(self, on):
        if on:
            self.pinButton.setIcon(CurrentTheme.PINNED_PALETTE_ICON)
            self.pinButton.setToolTip("Unpin this from the the Tab Bar")
        else:
            self.pinButton.setIcon(CurrentTheme.UNPINNED_PALETTE_ICON)
            self.pinButton.setToolTip("Pin this on the Tab Bar")
            
    def setPinStatus(self, pinStatus):
        self.pinStatus = pinStatus
        self.pinButton.setChecked(pinStatus)
        self.updateButtonIcon(pinStatus)
        
    def monitorWindowTitle(self, widget):
        """ monitorWindowTitle(widget: QWidget) -> None        
        Watching window title changed on widget and use it as a window
        title on this tool window
        
        """
        if widget:
            widget.installEventFilter(self)

    def eventFilter(self, object, event):
        """ eventFilter(object: QObject, event: QEvent) -> bool
        Filter window title change event to change the tool window title
        
        """
        if event.type()==QtCore.QEvent.WindowTitleChange:
            self.setWindowTitle(object.windowTitle())
        elif event.type()==QtCore.QEvent.Close:
            object.removeEventFilter(self)
        return QtGui.QDockWidget.eventFilter(self, object, event)
        # return super(QToolWindow, self).eventFilter(object, event)                    
            
        
class QToolWindowInterface(object):
    """
    QToolWindowInterface can be co-inherited in any class to allow the
    inherited class to switch to be contained in a window
    
    """
    def toolWindow(self):
        """ toolWindow() -> None        
        Return the tool window and set its parent to self.parent()
        while having self as its contained widget
        
        """
        if not hasattr(self, '_toolWindow'):
            self._toolWindow = QToolWindow(self, self.parent and self.parent())
        elif self._toolWindow.centralwidget!=self:
            self._toolWindow.window.setCentralWidget(self)
        return self._toolWindow

    def changeEvent(self, event):
        """ changeEvent(event: QEvent) -> None        
        Make sure to update the tool parent when to match the widget's
        real parent
        
        """
        if (event.type()==QtCore.QEvent.ParentChange and
            hasattr(self, '_toolWindow')):
            if self.parent()!=self._toolWindow:
                self._toolWindow.setParent(self.parent())

    def setToolWindowAcceptDrops(self, value):
        self.toolWindow().setAcceptDrops(value)

###############################################################################

class QDockContainer(QtGui.QMainWindow):
    """
    QDockContainer is a window that can contain dock widgets while
    still be contained in a tool window. It is just a straight
    inheritance from QMainWindow
    
    """
    def __init__(self, parent=None):
        """ QMainWindow(parent: QWidget) -> QMainWindow
        Setup window to have its widget dockable everywhere
        
        """
        QtGui.QMainWindow.__init__(self, parent)
        self.setDockNestingEnabled(True)

###############################################################################

class QSearchTreeWidget(QtGui.QTreeWidget):
    """
    QSearchTreeWidget is just a QTreeWidget with a support function to
    refine itself when searching for some text

    """
    def __init__(self, parent=None):
        """ QSearchTreeWidget(parent: QWidget) -> QSearchTreeWidget
        Set up size policy and header

        """
        QtGui.QTreeWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setRootIsDecorated(True)
        self.setDragEnabled(True)
        self.flags = QtCore.Qt.ItemIsDragEnabled

        self._search_was_empty = True

    def searchItemName(self, name):
        """ searchItemName(name: QString) -> None
        Search and refine the module tree widget to contain only items
        whose name is 'name'
        
        """
        matchedItems = []
        
        def recursiveSetVisible(item, testFunction):
            """ recursiveSetVisible
            Pass through all items of a item
            
            """
            enabled = testFunction(item)

            visible = enabled
            child = item.child
            for childIndex in xrange(item.childCount()):
                visible |= recursiveSetVisible(child(childIndex),
                                               testFunction)

            # if item is hidden or has changed visibility
            if not visible or (item.isHidden() != (not visible)):
                item.setHidden(not visible)
            
            if visible:
                f = item.flags()
                b = f & self.flags
                if enabled:
                    if not b:
                        item.setFlags(f | self.flags)
                elif b:
                    item.setFlags(f & ~self.flags)
                
            return visible

        if str(name)=='':
            testFunction = lambda x: (not hasattr(x, 'is_hidden') or
                                      not x.is_hidden)
            if not self._search_was_empty:
                self.collapseAll()
                self._search_was_empty = True
        else:
            matchedItems = set(self.findItems(name,
                                              QtCore.Qt.MatchContains |
                                              QtCore.Qt.MatchWrap |
                                              QtCore.Qt.MatchRecursive))
            testFunction = matchedItems.__contains__
            if self._search_was_empty:
                self.expandAll()
                self._search_was_empty = False
        for itemIndex in xrange(self.topLevelItemCount()):
            recursiveSetVisible(self.topLevelItem(itemIndex),
                                testFunction)
    
    def mimeData(self, itemList):
        """ mimeData(itemList) -> None        
        Setup the mime data to contain itemList because Qt 4.2.2
        implementation doesn't instantiate QTreeWidgetMimeData
        anywhere as it's supposed to. It must have been a bug...
        
        """
        data = QtGui.QTreeWidget.mimeData(self, itemList)
        data.items = itemList
        return data

    def setMatchedFlags(self, flags):
        """ setMatchedFlags(flags: QItemFlags) -> None Set the flags
        for matched item in the search tree. Parents of matched node
        will be visible with these flags off.
        
        """
        self.flags = flags
    
class QSearchTreeWindow(QtGui.QWidget):
    """
    QSearchTreeWindow contains a search box on top of a tree widget
    for easy search and refine. The subclass has to implement
    createTreeWidget() method to return a tree widget that is also 
    needs to expose searchItemName method

    """
    def __init__(self, parent=None):
        """ QSearchTreeWindow(parent: QWidget) -> QSearchTreeWindow
        Intialize all GUI components
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Search Tree')
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)
        
        self.searchBox = QSearchBox(False, True, self)
        vLayout.addWidget(self.searchBox)

        self.treeWidget = self.createTreeWidget()
        vLayout.addWidget(self.treeWidget)
        
        self.connect(self.searchBox,
                     QtCore.SIGNAL('executeIncrementalSearch(QString)'),
                     self.treeWidget.searchItemName)
        self.connect(self.searchBox,
                     QtCore.SIGNAL('executeSearch(QString)'),
                     self.treeWidget.searchItemName)
        self.connect(self.searchBox,
                     QtCore.SIGNAL('resetSearch()'),
                     self.clearTreeWidget)
                     
    def clearTreeWidget(self):
        """ clearTreeWidget():
        Return the default search tree

        """
        self.treeWidget.searchItemName('')

    def createTreeWidget(self):
        """ createTreeWidget() -> QSearchTreeWidget
        Return a default searchable tree widget
        
        """
        return QSearchTreeWidget(self)

class QPromptWidget(QtGui.QLabel):
    """
    QPromptWidget is a widget that will display a prompt text when it
    doesn't have any child visible, or else, it will disappear. This
    is good for drag and drop prompt. The inheritance should call
    setPromptText and showPrompt in appropriate time to show/hide the
    prompt text
    """
    def __init__(self, parent=None):
        """ QPromptWidget(parent: QWidget) -> QPromptWidget
        Set up the font and alignment for the prompt
        
        """
        QtGui.QLabel.__init__(self, parent)        
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.setWordWrap(True)
        self.regularFont = self.font()
        self.promptFont = QtGui.QFont(self.font())
        self.promptFont.setItalic(True)
        self.promptText = ''
        self.promptVisible = False

    def setPromptText(self, text):
        """ setPromptText(text: str) -> None
        Set the prompt text string
        
        """
        self.promptText = text

    def showPrompt(self, show=True):
        """ showPrompt(show: boolean) -> None
        Show/Hide the prompt
        
        """
        if show!=self.promptVisible:
            self.promptVisible = show
            self.repaint(self.rect())
            
    def showPromptByChildren(self):
        """ showPromptByChildren()
        Show/Hide the prompt based on the current state of children
        
        """
        if self.promptText=='':
            self.showPrompt(False)
        else:
            self.showPrompt(self.layout()==None or
                            self.layout().count()==0)            

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Paint the prompt in the center if neccesary
        
        """
        if self.promptVisible:
            painter = QtGui.QPainter(self)
            painter.setFont(self.promptFont)
            painter.drawText(self.rect(),
                             QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap,
                             self.promptText)
            painter.end()
        QtGui.QLabel.paintEvent(self, event)
        # super(QPromptWidget, self).paintEvent(event)

class QStringEdit(QtGui.QFrame):
    """
    QStringEdit is a line edit that has an extra button to allow user
    to use a file as the value
    
    """
    def __init__(self, parent=None):
        """ QStringEdit(parent: QWidget) -> QStringEdit
        Create a hbox layout to contain a line edit and a button

        """
        QtGui.QFrame.__init__(self, parent)        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setFrame(False)
        self.lineEdit.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Expanding)
        hLayout.addWidget(self.lineEdit)
        self.setFocusProxy(self.lineEdit)

        self.fileButton = QtGui.QToolButton()
        self.fileButton.setText('...')
        self.fileButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                      QtGui.QSizePolicy.Expanding)
        self.fileButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fileButton.setAutoFillBackground(True)
        self.connect(self.fileButton, QtCore.SIGNAL('clicked()'),
                     self.insertFileNameDialog)
        hLayout.addWidget(self.fileButton)

    def setText(self, text):
        """ setText(text: QString) -> None
        Overloaded function for setting the line edit text
        
        """
        self.lineEdit.setText(text)

    def text(self):
        """ text() -> QString
        Overloaded function for getting the line edit text
        
        """
        return self.lineEdit.text()

    def selectAll(self):
        """ selectAll() -> None
        Overloaded function for selecting all the text
        
        """
        self.lineEdit.selectAll()

    def setFrame(self, frame):
        """ setFrame(frame: bool) -> None
        Show/Hide the frame of this widget
        
        """
        if frame:
            self.setFrameStyle(QtGui.QFrame.StyledPanel |
                               QtGui.QFrame.Plain)
        else:
            self.setFrameStyle(QtGui.QFrame.NoFrame)

    def insertFileNameDialog(self):
        """ insertFileNameDialog() -> None
        Allow user to insert a file name as a value to the string
        
        """
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Use Filename '
                                                     'as Value...',
                                                     self.text(),
                                                     'All files '
                                                     '(*.*)')
        if fileName:
            self.setText(fileName)
        
###############################################################################

class MultiLineWidget(StandardConstantWidget):
    def __init__(self, contents, contentType, parent=None):
        """__init__(contents: str, contentType: str, parent: QWidget) ->
                                             StandardConstantWidget
        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'
        
        """
        StandardConstantWidget.__init__(self, parent)

    def update_parent(self):
        pass
     
    def keyPressEvent(self, event):
        """ keyPressEvent(event) -> None       
        If this is a string line edit, we can use Ctrl+Enter to enter
        the file name

        """
        k = event.key()
        s = event.modifiers()
        if ((k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return) and
            s & QtCore.Qt.ShiftModifier):
            event.accept()
            if self.contentIsString and self.multiLines:
                fileNames = QtGui.QFileDialog.getOpenFileNames(self,
                                                               'Use Filename '
                                                               'as Value...',
                                                               self.text(),
                                                               'All files '
                                                               '(*.*)')
                fileName = fileNames.join(',')
                if fileName:
                    self.setText(fileName)
                    return
        QtGui.QLineEdit.keyPressEvent(self,event)
        
###############################################################################

class QSearchEditBox(QtGui.QComboBox):
    def __init__(self, incremental=True, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Fixed)
        regexp = QtCore.QRegExp("\S.*")
        self.setDuplicatesEnabled(False)
        validator = QtGui.QRegExpValidator(regexp, self)
        self.setValidator(validator)
        self.addItem('Clear Recent Searches')
        item = self.model().item(0, 0)
        font = QtGui.QFont(item.font())
        font.setItalic(True)
        item.setFont(font)
        self.is_incremental = incremental

    def keyPressEvent(self, e):
        if e.key() in (QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter):
            if self.currentText():
                if not self.is_incremental:
                    self.emit(QtCore.SIGNAL('executeSearch(QString)'),  
                              self.currentText())
                self.insertItem(0, self.currentText())
            else:
                self.emit(QtCore.SIGNAL('resetText()'))
            return
        QtGui.QComboBox.keyPressEvent(self, e)
        
###############################################################################

class QSearchBox(QtGui.QWidget):
    """ 
    QSearchBox contains a search combo box with a clear button and
    a search icon.

    """
    def __init__(self, refine=True, incremental=True, parent=None):
        """ QSearchBox(parent: QWidget) -> QSearchBox
        Intialize all GUI components
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Search')
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(2)
        self.setLayout(hLayout)

        self.searchEdit = QSearchEditBox(incremental, self)
        #TODO: Add separator!
        self.searchEdit.clearEditText()

        if refine:
            self.actionGroup = QtGui.QActionGroup(self)
            self.searchAction = QtGui.QAction('Search', self)
            self.searchAction.setCheckable(True)
            self.actionGroup.addAction(self.searchAction)
            self.refineAction = QtGui.QAction('Refine', self)
            self.refineAction.setCheckable(True)
            self.actionGroup.addAction(self.refineAction)
            self.searchAction.setChecked(True)

            self.searchMenu = QtGui.QMenu()
            self.searchMenu.addAction(self.searchAction)
            self.searchMenu.addAction(self.refineAction)

            self.searchButton = QtGui.QToolButton(self)
            self.searchButton.setIcon(CurrentTheme.QUERY_ARROW_ICON)
            self.searchButton.setAutoRaise(True)
            self.searchButton.setPopupMode(QtGui.QToolButton.InstantPopup)
            self.searchButton.setMenu(self.searchMenu)
            hLayout.addWidget(self.searchButton)
            self.connect(self.searchAction, QtCore.SIGNAL('triggered()'),
                         self.searchMode)
            self.connect(self.refineAction, QtCore.SIGNAL('triggered()'),
                         self.refineMode)
        else:
            self.searchLabel = QtGui.QLabel(self)
            pix = CurrentTheme.QUERY_VIEW_ICON.pixmap(QtCore.QSize(16,16))
            self.searchLabel.setPixmap(pix)
            self.searchLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.searchLabel.setMargin(4)
            hLayout.addWidget(self.searchLabel)
        
        hLayout.addWidget(self.searchEdit)

        self.resetButton = QtGui.QToolButton(self)
        self.resetButton.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.resetButton.setIconSize(QtCore.QSize(12,12))
        self.resetButton.setAutoRaise(True)
        self.resetButton.setEnabled(False)
        hLayout.addWidget(self.resetButton)
        self.manualResetEnabled = False

        self.connect(self.resetButton, QtCore.SIGNAL('clicked()'),
                     self.resetSearch)
        self.connect(self.searchEdit, QtCore.SIGNAL('activated(int)'),
                     self.executeSearch)
        self.connect(self.searchEdit, QtCore.SIGNAL('resetText'),
                     self.resetSearch)
        self.connect(self.searchEdit, QtCore.SIGNAL('executeSearch(QString)'),
                     self.executeTextSearch)
        if incremental:
            self.connect(self.searchEdit, 
                         QtCore.SIGNAL('editTextChanged(QString)'),
                         self.executeIncrementalSearch)
        else:
            self.connect(self.searchEdit,
                         QtCore.SIGNAL('editTextChanged(QString)'),
                         self.resetToggle)

    def resetSearch(self):
        """
        resetSearch() -> None
        Emit a signal to clear the search.

        """
        self.searchEdit.clearEditText()
        self.resetButton.setEnabled(False)
        self.manualResetEnabled = False
        self.emit(QtCore.SIGNAL('resetSearch()'))

    def clearSearch(self):
        """ clearSearch() -> None
        Clear the edit text without emitting resetSearch() signal
        This is for when the search is rest from the version view and
        the signal are already taken care of

        """
        self.searchEdit.clearEditText()
        self.resetButton.setEnabled(False)
        self.manualResetEnabled = False

    def searchMode(self):
        """
        searchMode() -> None

        """
        self.emit(QtCore.SIGNAL('refineMode(bool)'), False) 
    
    def refineMode(self):
        """
        refineMode() -> None

        """
        self.emit(QtCore.SIGNAL('refineMode(bool)'), True) 

    def resetToggle(self, text):
        self.resetButton.setEnabled((str(text) != '') or 
                                    self.manualResetEnabled)

    def executeIncrementalSearch(self, text):
        """
        executeIncrementalSearch(text: QString) -> None
        The text is changing, so update the search.

        """
        self.resetButton.setEnabled((str(text)!='') or
                                    self.manualResetEnabled)
        self.emit(QtCore.SIGNAL('executeIncrementalSearch(QString)'), text)

    def executeTextSearch(self, text):
        self.emit(QtCore.SIGNAL('executeSearch(QString)'),
                  text)

    def executeSearch(self, index):
        """
        executeSearch(index: int) -> None
        The text is finished changing or a different item was selected.

        """
        count = self.searchEdit.count() 
        if index == count-1: 
            for i in xrange(count-1): 
                self.searchEdit.removeItem(0) 
            self.resetSearch() 
        else: 
            self.resetButton.setEnabled(True) 
            self.emit(QtCore.SIGNAL('executeSearch(QString)'),  
                      self.searchEdit.currentText())

    def getCurrentText(self):
        return str(self.searchEdit.currentText())

    def setManualResetEnabled(self, boolVal):
        self.manualResetEnabled = boolVal
        self.resetButton.setEnabled((self.getCurrentText() != '') or
                                    self.manualResetEnabled)

###############################################################################

class QTabBarDetachButton(QtGui.QAbstractButton):
    """QTabBarDetachButton is a special button to be added to a tab
    
    """
    def __init__(self, parent):
        QtGui.QAbstractButton.__init__(self)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.setToolTip("Detach Tab")
        self.setIcon(CurrentTheme.DETACH_TAB_ICON)
        self.activePixmap = self.icon().pixmap(self.sizeHint(),
                                               mode=QtGui.QIcon.Active)
        self.normalPixmap = self.icon().pixmap(self.sizeHint(),
                                               mode=QtGui.QIcon.Normal)
        
        self.resize(self.sizeHint())
        
    def sizeHint(self):
        self.ensurePolished()
        size = QtCore.QSize()
        if not self.icon().isNull():
            iconSize = self.style().pixelMetric(QtGui.QStyle.PM_SmallIconSize, 
                                                None, self)
            sz = self.icon().actualSize(QtCore.QSize(iconSize, iconSize))
            size = max(sz.width(), sz.height())
        
        return QtCore.QSize(size, size)
    
    def enterEvent(self, event):
        if self.isEnabled():
            icon = QtGui.QIcon(self.activePixmap)
            self.setIcon(icon)
            self.update()
        else:
            icon = QtGui.QIcon(self.normalPixmap)
            self.setIcon(icon)
        QtGui.QAbstractButton.enterEvent(self, event)
        
    def leaveEvent(self, event):
        icon = QtGui.QIcon(self.normalPixmap)
        self.setIcon(icon)
        if self.isEnabled():
            self.update()
        QtGui.QAbstractButton.leaveEvent(self, event)
        
    def closePosition(self):
        tb = self.parent()
        if isinstance(tb, QtGui.QTabBar):
            close_position = self.style().styleHint(QtGui.QStyle.SH_TabBar_CloseButtonPosition,
                                                  None, tb)
            return close_position
        return -1
    
    def otherPosition(self):
        tb = self.parent()
        if isinstance(tb, QtGui.QTabBar):
            close_position = self.closePosition()
            if close_position == QtGui.QTabBar.LeftSide:
                position = QtGui.QTabBar.RightSide
            else:
                position = QtGui.QTabBar.LeftSide
            return position
        return -1
            
    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        opt = QtGui.QStyleOptionToolButton()
        opt.init(self)
        opt.state |= QtGui.QStyle.State_AutoRaise
        if (self.isEnabled() and self.underMouse() and 
            not self.isChecked() and not self.isDown()):
            opt.state |= QtGui.QStyle.State_Raised
        if self.isChecked():
            opt.state |= QtGui.QStyle.State_On
        if self.isDown():
            opt.state |= QtGui.QStyle.State_Sunken
        tb = self.parent()
        if isinstance(tb, QtGui.QTabBar):
            index = tb.currentIndex()
            position = self.otherPosition()
            if tb.tabButton(index, position) == self:
                opt.state |= QtGui.QStyle.State_Selected
            opt.icon = self.icon()
            opt.subControls = QtGui.QStyle.SC_None
            opt.activeSubControls = QtGui.QStyle.SC_None
            opt.features = QtGui.QStyleOptionToolButton.None
            opt.arrowType = QtCore.Qt.NoArrow
            size = self.style().pixelMetric(QtGui.QStyle.PM_SmallIconSize, 
                                                None, self)
            opt.iconSize = QtCore.QSize(size,size)
            self.style().drawComplexControl(QtGui.QStyle.CC_ToolButton, opt, p, 
                                            self)

###############################################################################

class QMouseTabBar(QtGui.QTabBar):
    """QMouseTabBar is a QTabBar that emits a signal when a tab
    receives a mouse event. For now only doubleclick events are
    emitted."""
    #signals
    tabDoubleClicked = pyqtSignal(int,QtCore.QPoint)
    
    def __init__(self, parent=None):
        QtGui.QTabBar.__init__(self, parent)
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            tab_idx = self.tabAt(event.pos())
            if tab_idx != -1:
                self.tabDoubleClicked.emit(tab_idx, event.pos())
        QtGui.QTabBar.mouseDoubleClickEvent(self, event)

###############################################################################

class QDockPushButton(QtGui.QPushButton):
    """QDockPushButton is a button to be used inside QDockWidgets. It will 
    set the minimum height on Mac so it looks nice on both Mac and Windows"""
    def __init__(self, text, parent=None):
        QtGui.QPushButton.__init__(self, text, parent) 
        if systemType in ['Darwin']:
            self.setMinimumHeight(32)

class QPathChooserToolButton(QtGui.QToolButton):
    """
    QPathChooserToolButton is a toolbar button that opens a browser for
    paths.  The lineEdit is updated with the pathname that is selected.
    
    emits pathChanged when the path is changed

    """
    pathChanged = pyqtSignal()

    def __init__(self, parent=None, lineEdit=None, toolTip=None,
                 defaultPath=None):
        """
        PathChooserToolButton(parent: QWidget, 
                              lineEdit: StandardConstantWidget) ->
                 PathChooserToolButton

        """
        QtGui.QToolButton.__init__(self, parent)
        self.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        self.setIconSize(QtCore.QSize(12,12))
        if toolTip is None:
            toolTip = 'Open a path chooser'
        self.defaultPath = defaultPath
        self.setToolTip(toolTip)
        self.setAutoRaise(True)
        self.lineEdit = lineEdit
        self.connect(self,
                     QtCore.SIGNAL('clicked()'),
                     self.runDialog)

    def setPath(self, path):
        """
        setPath() -> None

        """
        if self.lineEdit and path:
            self.lineEdit.setText(path)
            self.pathChanged.emit()
    
    def getDefaultText(self):
        return self.lineEdit.text() or self.defaultPath

    def openChooser(self):
        path = QtGui.QFileDialog.getOpenFileName(self,
                                                 'Select Path...',
                                                 self.getDefaultText(),
                                                 'All files '
                                                 '(*.*)')
        return self.setDataDirectory(path)

    def runDialog(self):
        path = self.openChooser()
        self.setPath(path)

    def setDataDirectory(self, path):
        if path:
            absPath = os.path.abspath(str(QtCore.QFile.encodeName(path)))
            dirName = os.path.dirname(absPath)
            set_vistrails_data_directory(dirName)
            return absPath
        return path

class QFileChooserToolButton(QPathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None, toolTip=None,
                 defaultPath=None):
        if toolTip is None:
            toolTip = "Open a file chooser dialog"
        QPathChooserToolButton.__init__(self, parent, lineEdit, toolTip,
                                        defaultPath)

    def openChooser(self):
        path = QtGui.QFileDialog.getOpenFileName(self,
                                                 'Select File...',
                                                 self.getDefaultText(),
                                                 'All files '
                                                 '(*.*)')
        return self.setDataDirectory(path)

class QDirectoryChooserToolButton(QPathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None, toolTip=None,
                 defaultPath=None):
        if toolTip is None:
            toolTip = "Open a directory chooser dialog"
        QPathChooserToolButton.__init__(self, parent, lineEdit, toolTip,
                                       defaultPath)

    def openChooser(self):
        path = QtGui.QFileDialog.getExistingDirectory(self,
                                                      'Select Directory...',
                                                      self.getDefaultText())
        return self.setDataDirectory(path)

class QOutputPathChooserToolButton(QPathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None, toolTip=None,
                 defaultPath=None):
        if toolTip is None:
            toolTip = "Open a path chooser dialog"
        QPathChooserToolButton.__init__(self, parent, lineEdit, toolTip,
                                       defaultPath)
    
    def openChooser(self):
        path = QtGui.QFileDialog.getSaveFileName(self,
                                                 'Select Output Location...',
                                                 self.getDefaultText(),
                                                 'All files (*.*)')
        return self.setDataDirectory(path)
    
    
