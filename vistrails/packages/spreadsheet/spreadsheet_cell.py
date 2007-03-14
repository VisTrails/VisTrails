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
################################################################################
# This file contains classes working with cell helper widgets, i.e. toolbar,
# resizer, etc.:
#   QCellWidget
#   QCellToolBar
################################################################################
from PyQt4 import QtCore, QtGui
import datetime
import os
from core import system

################################################################################

class QCellWidget(QtGui.QWidget):
    """
    QCellWidget is the base cell class. All types of spreadsheet cells
    should inherit from this.
    
    """

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        """ QCellWidget(parent: QWidget) -> QCellWidget
        Instantiate the cell and helper properties
        
        """
        QtGui.QWidget.__init__(self, parent, flags)
        self._historyImages = []
        self._player = QtGui.QLabel(self.parent())
        self._player.setAutoFillBackground(True)
        self._player.setFocusPolicy(QtCore.Qt.NoFocus)
        self._player.setScaledContents(True)
        self._playerTimer = QtCore.QTimer()        
        self._playerTimer.setSingleShot(True)
        self._currentFrame = 0
        self._playing = False
        self._capturingEnabled = False
        self.connect(self._playerTimer,
                     QtCore.SIGNAL('timeout()'),
                     self.playNextFrame)

    def setAnimationEnabled(self, enabled):
        """ setAnimationEnabled(enabled: bool) -> None
        
        """
        self._capturingEnabled = enabled
        if not enabled:
            self.clearHistory()
        
    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> None        
        Abtract function for saving the current widget contents to an
        image file
        
        """
        print 'saveToPNG() is unimplemented by the inherited cell'

    def saveToHistory(self):
        """ saveToHistory() -> None
        Save the current contents to the history
        
        """
        # Generate filename
        current = datetime.datetime.now()
        tmpDir = system.temporaryDirectory()
        fn = (tmpDir + "hist_" +
              current.strftime("%Y_%m_%d__%H_%M_%S") +
              "_" + str(current.microsecond)+".png")
        if self.saveToPNG(fn):
            self._historyImages.append(fn)

    def clearHistory(self):
        """ clearHistory() -> None
        Clear all history files
        
        """
        for fn in self._historyImages:
            os.remove(fn)
        self._historyImages = []

    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to clear history and delete the widget
        
        """        
        self.clearHistory()
        QtGui.QWidget.deleteLater(self)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple)
        Make sure to capture to history
        
        """
        # Capture window into history for playback
        if self._capturingEnabled:
            self.saveToHistory()

    def resizeEvent(self, e):
        """ resizeEvent(e: QEvent) -> None
        Re-adjust the player widget
        
        """
        QtGui.QWidget.resizeEvent(self, e)

        if self._player.isVisible():
            self._player.setGeometry(self.geometry())

    def setPlayerFrame(self, frame):
        """ setPlayerFrame(frame: int) -> None
        Set the player to display a particular frame number
        
        """
        if frame>=len(self._historyImages):
            frame = frame % len(self._historyImages)
        if frame>=len(self._historyImages):
            return
        self._player.setPixmap(QtGui.QPixmap(self._historyImages[frame]))

    def startPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        if not self._capturingEnabled:
            return
        self._player.setParent(self.parent())
        self._player.setGeometry(self.geometry())
        self._player.raise_()
        self._currentFrame = -1
        self.playNextFrame()
        self._player.show()
        self._playing = True
        
    def stopPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        if not self._capturingEnabled:
            return
        self._playerTimer.stop()
        self._player.hide()
        self._playing = False

    def showNextFrame(self):
        """ showNextFrame() -> None
        Display the next frame in the history
        
        """
        self._currentFrame += 1
        if self._currentFrame>=len(self._historyImages):
            self._currentFrame = 0
        self.setPlayerFrame(self._currentFrame)
        
    def playNextFrame(self):
        """ playNextFrame() -> None        
        Display the next frame in the history and start the timer for
        the frame after
        
        """
        self.showNextFrame()
        self._playerTimer.start(100)


class QCellToolBar(QtGui.QToolBar):
    """
    CellToolBar is inherited from QToolBar with some functionalities
    for interacting with CellHelpers
    
    """
    def __init__(self, sheet):
        """ CellToolBar(sheet: SpreadsheetSheet) -> CellToolBar        
        Initialize the cell toolbar by calling the user-defined
        toolbar construction function
        
        """
        QtGui.QToolBar.__init__(self,sheet)
        self.setAutoFillBackground(True)
        self.sheet = sheet
        self.row = -1
        self.col = -1
        self.createToolBar()

    def addAnimationButtons(self):
        """ addAnimationButtons() -> None
        
        """
        self.appendAction(QCellToolBarCaptureToHistory(self))
        self.appendAction(QCellToolBarPlayHistory(self))
        self.appendAction(QCellToolBarClearHistory(self))
            
    def createToolBar(self):
        """ createToolBar() -> None        
        A user-defined method for customizing the toolbar. This is
        going to be an empty method here for inherited classes to
        override.
        
        """
        pass

    def snapTo(self, row, col):
        """ snapTo(row, col) -> None
        Assign which row and column the toolbar should be snapped to
        
        """
        self.row = row
        self.col = col
        self.updateToolBar()

    def adjustPosition(self, rect):
        """ adjustPosition(rect: QRect) -> None
        Adjust the position of the toolbar to be top-left
        
        """
        self.adjustSize()
        p = self.parent().mapFromGlobal(rect.topLeft())
        self.move(p.x(), p.y())

    def updateToolBar(self):
        """ updateToolBar() -> None        
        This will get called when the toolbar widgets need to have
        their status updated. It sends out needUpdateStatus signal
        to let the widget have a change to update their own status
        
        """
        cellWidget = self.sheet.getCell(self.row, self.col)
        for action in self.actions():
            action.emit(QtCore.SIGNAL('needUpdateStatus'),
                        (self.sheet, self.row, self.col, cellWidget))

    def connectAction(self, action, widget):
        """ connectAction(action: QAction, widget: QWidget) -> None
        Connect actions to special slots of a widget
        
        """
        if hasattr(widget, 'updateStatus'):
            self.connect(action, QtCore.SIGNAL('needUpdateStatus'),
                         widget.updateStatus)
        if hasattr(widget, 'triggeredSlot'):
            self.connect(action, QtCore.SIGNAL('triggered()'),
                         widget.triggeredSlot)
        if hasattr(widget, 'toggledSlot'):
            self.connect(action, QtCore.SIGNAL('toggled(bool)'),
                         widget.toggledSlot)

    def appendAction(self, action):
        """ appendAction(action: QAction) -> QAction
        Setup and add action to the tool bar
        
        """
        action.toolBar = self
        self.addAction(action)
        self.connectAction(action, action)
        return action

    def appendWidget(self, widget):
        """ appendWidget(widget: QWidget) -> QAction
        Setup the widget as an action and add it to the tool bar

        """
        action = self.addWidget(widget)
        widget.toolBar = self
        action.toolBar = self
        self.connectAction(action, widget)
        return action

    def getSnappedWidget(self):
        """ getSnappedWidget() -> QWidget
        Return the widget being snapped by the toolbar
        
        """
        if self.row>=0 and self.col>=0:
            return self.sheet.getCell(self.row, self.col)
        else:
            return None

class QCellToolBarCaptureToHistory(QtGui.QAction):
    """
    QCellToolBarCaptureToHistory is the action to capture the
    underlying widget to history for play back. The cell type must
    support function saveToPNG(filename)
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarCaptureToHistory(parent: QWidget)
                                         -> QCellToolBarCaptureToHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera_mount.png"),
                               "&Capture image to history",
                               parent)
        self.setStatusTip("Capture the cell contents to the history for "
                          "playback later")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        self.toolBar.hide()
        cellWidget.saveToHistory()
        self.toolBar.updateToolBar()
        self.toolBar.show()
        
class QCellToolBarPlayHistory(QtGui.QAction):
    """
    QCellToolBarPlayHistory is the action to play the history as an
    animation
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarPlayHistory(parent: QWidget)
                                    -> QCellToolBarPlayHistory
        Setup the image, status tip, etc. of the action
        
        """
        self.icons = [QtGui.QIcon(":/images/player_play.png"),
                      QtGui.QIcon(":/images/player_pause.png")]
        self.toolTips = ["&Play the history",
                         "Pa&use the history playback"]
        self.statusTips = ["Playback all image files kept in the history",
                           "Pause the playback"]
        QtGui.QAction.__init__(self, self.icons[0], self.toolTips[0], parent)
        self.setStatusTip(self.statusTips[0])
        self.status = 0

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        if self.status==0:            
            cellWidget.startPlayer()
        else:
            cellWidget.stopPlayer()
        self.toolBar.updateToolBar()

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            newStatus = int(cellWidget._playing)
            if newStatus!=self.status:
                self.status = newStatus
                self.setIcon(self.icons[self.status])
                self.setToolTip(self.toolTips[self.status])
                self.setStatusTip(self.statusTips[self.status])
            self.setEnabled(len(cellWidget._historyImages)>0)                

class QCellToolBarClearHistory(QtGui.QAction):
    """
    QCellToolBarClearHistory is the action to reset cell history
    
    """
    def __init__(self, parent=None):
        """ QCellToolBarClearHistory(parent: QWidget)
                                     -> QCellToolBarClearHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/noatunloopsong.png"),
                               "&Clear this cell history",
                               parent)
        self.setStatusTip("Clear the cell history and its temporary "
                          "image files on disk")        
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.clearHistory()
        self.toolBar.updateToolBar()
        
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            self.setEnabled((len(cellWidget._historyImages)>0
                             and cellWidget._playing==False))
