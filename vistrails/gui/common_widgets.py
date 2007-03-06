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
""" This common widgets using on the interface of VisTrails. These are
only simple widgets in term of coding and additional features. It
should have no interaction with VisTrail core"""

from PyQt4 import QtCore, QtGui
import bisect

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
        self.setWidget(widget)
        if widget:
            self.setWindowTitle(widget.windowTitle())
        self.monitorWindowTitle(widget)

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
        return QtGui.QDockWidget.eventFilter(self, object, event)

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
            self._toolWindow = QToolWindow(self, self.parent())
        elif self._toolWindow.widget()!=self:
            self._toolWindow.setWidget(self)
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

    def searchItemName(self, name):
        """ searchItemName(name: QString) -> None        
        Search and refine the module tree widget to contain only items
        whose name is 'name'
        
        """
        matchedItems = []
        
        def recursiveSetVisible(item, testFunction):
            """ recursiveSetVisible(matchedItems: QItemList) -> None
            Pass through all items of a item
            
            """
            visible = testFunction(item)
            for childIndex in range(item.childCount()):
                if recursiveSetVisible(item.child(childIndex),
                                       testFunction):
                    visible = True
            if item.isHidden()!=(not visible) or (not visible):
                item.setHidden(not visible)
            return visible

        if str(name)=='':
            testFunction = lambda x: True
        else:
            matchedItems = set(self.findItems(name,
                                              QtCore.Qt.MatchContains |
                                              QtCore.Qt.MatchWrap |
                                              QtCore.Qt.MatchRecursive))
            testFunction = lambda x: x in matchedItems
        for itemIndex in range(self.topLevelItemCount()):
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
        
        hLayout = QtGui.QHBoxLayout()
        hLayout.setMargin(0)
        hLayout.setSpacing(5)
        vLayout.addLayout(hLayout)
        
        searchLabel = QtGui.QLabel(" Search", self)
        hLayout.addWidget(searchLabel)
        self.searchText = QtGui.QLineEdit()
        searchLabel.setBuddy(self.searchText)
        hLayout.addWidget(self.searchText)

        self.treeWidget = self.createTreeWidget()
        vLayout.addWidget(self.treeWidget)
        
        self.connect(self.searchText,
                     QtCore.SIGNAL('textChanged(QString)'),
                     self.treeWidget.searchItemName)

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
        if not fileName.isEmpty():
            self.setText(fileName)
        
