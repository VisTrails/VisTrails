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
################################################################################
# This file contains classes working with cell helper widgets, i.e. toolbar,
# resizer, etc.:
#   QCellWidget
#   QCellToolBar
################################################################################
from PyQt4 import QtCore, QtGui
import datetime
import os
import tempfile
from vistrails.core import debug
import cell_rc
import celltoolbar_rc
import spreadsheet_controller
import analogy_api
from spreadsheet_config import configuration
from vistrails.core.system import strftime
from vistrails.core.modules.output_modules import FileMode

################################################################################

class QCellWidget(QtGui.QWidget):
    """
    QCellWidget is the base cell class. All types of spreadsheet cells
    should inherit from this.

    """
    save_formats = ["Images (*.png *.xpm *.jpg)",
                    "Portable Document Format (*.pdf)"]

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
        # cell can be captured if it re-implements saveToPNG
        self._capturingEnabled = (not isinstance(self, QCellWidget) and
                                  hasattr(self, 'saveToPNG'))
        self._output_module = None
        self._output_configuration = None
        self.connect(self._playerTimer,
                     QtCore.SIGNAL('timeout()'),
                     self.playNextFrame)
        if configuration.fixedCellSize:
            self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            self.setFixedSize(200, 180)

    def setAnimationEnabled(self, enabled):
        """ setAnimationEnabled(enabled: bool) -> None
        
        """
        self._capturingEnabled = enabled
        if not enabled:
            self.clearHistory()
        
    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> Bool       
        Abtract function for saving the current widget contents to an
        image file
        Returns True when succesful
        
        """
        debug.critical('saveToPNG() is unimplemented by the inherited cell')

    def saveToHistory(self):
        """ saveToHistory() -> None
        Save the current contents to the history
        
        """
        # Generate filename
        current = datetime.datetime.now()
        tmpDir = tempfile.gettempdir()
        fn = ( "hist_" + strftime(current, "%Y_%m_%d__%H_%M_%S") +
               "_" + str(current.microsecond)+".png")
        fn = os.path.join(tmpDir, fn)
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
        if (len(self._historyImages)==0):
            return
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
        self.hide()
        self._playing = True
        
    def stopPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        if not self._capturingEnabled:
            return
        self._playerTimer.stop()
        self._player.hide()
        self.show()
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

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function
        
        """
        return QtGui.QPixmap.grabWidget(self)

    def dumpToFile(self, filename):
        """ dumpToFile(filename: str, dump_as_pdf: bool) -> None
        Dumps itself as an image to a file, calling grabWindowPixmap """
        pixmap = self.grabWindowPixmap()
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            pixmap.save(filename, 'PNG')
        elif ext == '.pdf':
            self.saveToPDF(filename)
        else:
            pixmap.save(filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()

        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        pixmap = self.grabWindowPixmap()
        size = pixmap.size()
        printer.setPaperSize(QtCore.QSizeF(size.width(), size.height()),
                             QtGui.QPrinter.Point)
        painter = QtGui.QPainter()
        painter.begin(printer)
        rect = painter.viewport()
        size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
    def set_output_module(self, output_module, configuration=None):
        self._output_module = output_module
        self._output_configuration = configuration

    def has_file_output_mode(self):
        # from vistrails.core.modules.output_modules import FileMode
        if self._output_module is None:
            return False
        for mode in self._output_module.get_sorted_mode_list():
            if issubclass(mode, FileMode):
                return True
        return False

    def get_file_output_modes(self):
        modes = []
        if self._output_module is not None:
            for mode_cls in self._output_module.get_sorted_mode_list():
                if issubclass(mode_cls, FileMode):
                    modes.append(mode_cls)
        return modes

    def get_conf_file_format(self):
        if (self._output_configuration is not None and 
            'format' in self._output_configuration):
            return self._output_configuration['format']
        return None

    def save_via_file_output(self, filename, mode_cls, save_format=None):
        mode_config = self._output_module.get_mode_config(mode_cls)
        mode_config['file'] = filename
        if save_format is not None:
            mode_config['format'] = save_format
        mode = mode_cls()
        mode.compute_output(self._output_module, mode_config)
        
################################################################################

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
        self.setOrientation(QtCore.Qt.Horizontal)
        self.sheet = sheet
        self.row = -1
        self.col = -1
        self.layout().setMargin(0)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        pixmap = self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)
        self.addSaveCellAction()
        self.appendAction(QCellToolBarRemoveCell(QtGui.QIcon(pixmap), self))
        self.appendAction(QCellToolBarMergeCells(QtGui.QIcon(':celltoolbar/mergecells.png'), self))
        self.createToolBar()

    def addAnimationButtons(self):
        """ addAnimationButtons() -> None
        
        """
        self.appendAction(QCellToolBarCaptureToHistory(self))
        self.appendAction(QCellToolBarPlayHistory(self))
        self.appendAction(QCellToolBarClearHistory(self))

    def addSaveCellAction(self):
        if not hasattr(self, 'saveActionVar'):
            self.saveActionVar = QCellToolBarSelectedCell(
                    QtGui.QIcon(":/images/camera.png"),
                    "Save cell",
                    self)
            self.saveActionVar.setStatusTip("Export this cell only")

            self.connect(self.saveActionVar, QtCore.SIGNAL('triggered(bool)'),
                         self.exportCell)
        self.appendAction(self.saveActionVar)

    def exportCell(self, checked=False):
        cell = self.sheet.getCell(self.row, self.col)
        if cell.has_file_output_mode():
            modes = cell.get_file_output_modes()
            formats = []
            format_map = {}
            for mode in modes:
                for m_format in mode.get_formats():
                    if m_format not in format_map:
                        formats.append(m_format)
                        format_map[m_format] = mode
            selected_filter = None
            if cell.get_conf_file_format() is not None:
                selected_filter = '(*.%s)' % cell.get_conf_file_format()
            (filename, save_format) = \
                    QtGui.QFileDialog.getSaveFileNameAndFilter(
                        self, "Select a File to Export the Cell",
                        ".", ';;'.join(['(*.%s)' % f for f in formats]), 
                        selected_filter)
            if filename:
                save_mode = format_map[save_format[3:-1]]
                cell.save_via_file_output(filename, save_mode)
        else:
            if not cell.save_formats:
                QtGui.QMessageBox.information(
                        self, "Export cell",
                        "This cell type doesn't provide any export option")
                return
            filename = QtGui.QFileDialog.getSaveFileName(
                self, "Select a File to Export the Cell",
                ".", ';;'.join(cell.save_formats))
            if filename:
                cell.dumpToFile(filename)

    def createToolBar(self):
        """ createToolBar() -> None
        A user-defined method for customizing the toolbar. This is
        going to be an empty method here for inherited classes to
        override.
        
        """
        self.addAnimationButtons()

    def snapTo(self, row, col):
        """ snapTo(row, col) -> None
        Assign which row and column the toolbar should be snapped to
        
        """
        self.row = row
        self.col = col
        self.updateToolBar()

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

class QCellToolBarSelectedCell(QtGui.QAction):
    """
    QCellToolBarSelectedCell is an action only visible if the cell isn't empty.
    """
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info

        """
        (sheet, row, col, cellWidget) = info
        self.setVisible(cellWidget != None)

class QCellToolBarRemoveCell(QCellToolBarSelectedCell):
    """
    QCellToolBarRemoveCell is the action to clear the current cell

    """
    def __init__(self, icon, parent=None):
        """ QCellToolBarRemoveCell(icon: QIcon, parent: QWidget)
                                   -> QCellToolBarRemoveCell
        Setup the image, status tip, etc. of the action

        """
        QCellToolBarSelectedCell.__init__(self,
                                          icon,
                                          "&Clear the current cell",
                                          parent)
        self.setStatusTip("Clear the current cell")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        r = QtGui.QMessageBox.question(cellWidget, 'Clear cell',
                                       'Are you sure to clear the cell?',
                                       QtGui.QMessageBox.Yes |
                                       QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No)
        if (r==QtGui.QMessageBox.Yes):
            self.toolBar.sheet.deleteCell(self.toolBar.row, self.toolBar.col)

class QCellToolBarMergeCells(QtGui.QAction):
    """
    QCellToolBarMergeCells is the action to merge selected cells to a
    single cell if they are in consecutive poisitions

    """
    def __init__(self, icon, parent=None):
        """ QCellToolBarMergeCells(icon: QIcon, parent: QWidget)
                                   -> QCellToolBarMergeCells
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               icon,
                               "&Merge cells",
                               parent)
        self.setStatusTip("Merge selected cells to a single cell if "
                          "they are in consecutive poisitions")
        self.setCheckable(True)

    def triggeredSlot(self):
        """ toggledSlot() -> None
        Execute the action when the button is clicked
        
        """
        # Merge
        if self.isChecked():
            sheet = self.toolBar.sheet
            selectedCells = sorted(sheet.getSelectedLocations())
            topLeft = selectedCells[0]
            bottomRight = selectedCells[-1]
            sheet.setSpan(topLeft[0], topLeft[1],
                          bottomRight[0]-topLeft[0]+1,
                          bottomRight[1]-topLeft[1]+1)
        else:
            sheet = self.toolBar.sheet
            selectedCells = sorted(sheet.getSelectedLocations())
            for (row, col) in selectedCells:
                sheet.setSpan(row, col, 1, 1)
        sheet.clearSelection()
        self.toolBar.updateToolBar()

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        selectedCells = sorted(sheet.getSelectedLocations())

        # Will not show up if there is no cell selected
        if len(selectedCells)==0:            
            self.setVisible(False)
            
        # If there is a single cell selected, only show up if it has
        # been merged before so that user can un-merge cells
        elif len(selectedCells)==1:
            showUp = False
            if selectedCells[0]==(row, col):
                span = sheet.getSpan(row, col)
                if span[0]>1 or span[1]>1:
                    showUp = True
            if showUp:
                self.setChecked(True)
                self.setVisible(True)
            else:
                self.setVisible(False)
                
        # If there are multiple cells selected, only show up if they
        # can be merged, i.e. cells are in consecutive position and
        # none of them is already merged
        else:
            showUp = False
            validRange = False
            topLeft = selectedCells[0]
            bottomRight = selectedCells[-1]
            fullCount = (bottomRight[0]-topLeft[0]+1)*(bottomRight[1]-topLeft[1]+1)
            validRange = len(selectedCells)==fullCount
            if validRange:
                showUp = True
                for (r, c) in selectedCells:
                    span = sheet.getSpan(r, c)
                    if span[0]>1 or span[1]>1:
                        showUp = False
                        break
            if showUp:
                self.setChecked(False)
                self.setVisible(True)
            else:
                self.setVisible(False)
            
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
        
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            self.setVisible(cellWidget._capturingEnabled)
        else:
            self.setVisible(False)

################################################################################
        
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
            self.setVisible(cellWidget._capturingEnabled)
            newStatus = int(cellWidget._playing)
            if newStatus!=self.status:
                self.status = newStatus
                self.setIcon(self.icons[self.status])
                self.setToolTip(self.toolTips[self.status])
                self.setStatusTip(self.statusTips[self.status])
            self.setEnabled(len(cellWidget._historyImages)>0)
        else:
            self.setVisible(False)

################################################################################
            
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
            self.setVisible(cellWidget._capturingEnabled)
            self.setEnabled((len(cellWidget._historyImages)>0
                             and cellWidget._playing==False))
        else:
            self.setVisible(False)

################################################################################

class QCellContainer(QtGui.QWidget):
    """ QCellContainer is a simple QWidget containing the actual cell
    widget as a child. This also acts as a sentinel protecting the
    actual cell widget from being destroyed by sheet widgets
    (e.g. QTableWidget) where they take control of the cell widget.
    
    """
    def __init__(self, widget=None, parent=None):
        """ QCellContainer(parent: QWidget) -> QCellContainer
        Create an empty container
        
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)
        self.containedWidget = None
        self.setWidget(widget)
        self.toolBar = None

    def setWidget(self, widget):
        """ setWidget(widget: QWidget) -> None
        Set the contained widget of this container
        
        """
        if widget!=self.containedWidget:
            if self.containedWidget:
                self.layout().removeWidget(self.containedWidget)
                self.containedWidget.deleteLater()
                self.toolBar = None
            if widget:
                widget.setParent(self)
                self.layout().addWidget(widget)
                widget.show()
            self.containedWidget = widget

    def widget(self):
        """ widget() -> QWidget
        Return the contained widget
        
        """
        return self.containedWidget

    def takeWidget(self):
        """ widget() -> QWidget
        Take the contained widget out without deleting
        
        """
        widget = self.containedWidget
        if self.containedWidget:
            self.layout().removeWidget(self.containedWidget)
            self.containedWidget.setParent(None)
            self.containedWidget = None
        self.toolBar = None
        return widget

################################################################################

class QCellPresenter(QtGui.QLabel):
    """
    QCellPresenter represents a cell in the Editing Mode. It has an
    info bar on top and control dragable icons on the bottom
    
    """
    def __init__(self, parent=None):
        """ QCellPresenter(parent: QWidget) -> QCellPresenter
        Create the layout of the widget
        
        """        
        QtGui.QLabel.__init__(self, parent)        
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setMargin(0)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.cellWidget = None

        layout = QtGui.QGridLayout(self)
        layout.setSpacing(2)
        layout.setMargin(self.margin())
        layout.setRowStretch(1, 1)
        self.setLayout(layout)
        
        self.info = QPipelineInfo()
        layout.addWidget(self.info, 0, 0, 1, 2)        

        self.manipulator = QCellManipulator()
        layout.addWidget(self.manipulator, 1, 0, 1, 2)

    def assignCellWidget(self, cellWidget):
        """ updateFromCellWidget(cellWidget: QWidget) -> None
        Assign a cell widget to this presenter
        
        """
        self.cellWidget = cellWidget
        if cellWidget:
            if hasattr(cellWidget, 'grabWindowPixmap'):
                bgPixmap = cellWidget.grabWindowPixmap()
            else:
                bgPixmap = QtGui.QPixmap.grabWidget(cellWidget)
            self.info.show()
        else:
            self.info.hide()
            bgPixmap = QtGui.QPixmap.grabWidget(self)
        self.thumbnail = QtGui.QPixmap(bgPixmap)
        painter = QtGui.QPainter(bgPixmap)
        painter.fillRect(bgPixmap.rect(),
                         QtGui.QBrush(QtGui.QColor(175, 198, 229, 196)))
        painter.end()
        self.setPixmap(bgPixmap)

    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a sheet cell to the presenter
        
        """
        self.manipulator.assignCell(sheet, row, col)
        self.assignCellWidget(sheet.getCell(row, col))
        info = sheet.getCellPipelineInfo(row, col)
        self.info.updateInfo(info)
        
    def releaseCellWidget(self):
        """ releaseCellWidget() -> QWidget
        Return the ownership of self.cellWidget to the caller
        
        """
        cellWidget = self.cellWidget
        self.assignCellWidget(None)
        self.manipulator.assignCell(None, -1, -1)
        if cellWidget:
            cellWidget.setParent(None)
        return cellWidget

    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to delete the cell widget if it exists
        
        """
        if (self.cellWidget):
            self.cellWidget.deleteLater()
        QtGui.QLabel.deleteLater(self)

################################################################################

class QInfoLineEdit(QtGui.QLineEdit):
    """
    QInfoLineEdit is wrapper for a transparent, un-frame, read-only
    line edit
    
    """
    def __init__(self, parent=None):
        """ QInfoLineEdit(parent: QWidget) -> QInfoLineEdit
        Initialize the line edit
        
        """
        QtGui.QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setFrame(False)
        pal = QtGui.QPalette(self.palette())
        pal.setBrush(QtGui.QPalette.Base,
                     QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPalette(pal)


class QInfoLabel(QtGui.QLabel):
    """
    QInfoLabel is wrapper for a transparent, bolded label
    
    """
    def __init__(self, text='', parent=None):
        """ QInfoLabel(text: str, parent: QWidget) -> QInfoLabel
        Initialize the line edit
        
        """
        QtGui.QLabel.__init__(self, text, parent)
        font = QtGui.QFont(self.font())
        font.setBold(True)
        self.setFont(font)

################################################################################
    
class QPipelineInfo(QtGui.QFrame):
    """
    QPipelineInfo displays information about the executed pipeline of
    a cell. It has 3 static lines: Vistrail name, (pipeline name,
    pipeline id) and the cell type
    
    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        pal = QtGui.QPalette(self.palette())
        color = QtGui.QColor(pal.brush(QtGui.QPalette.Base).color())
        color.setAlpha(196)
        pal.setBrush(QtGui.QPalette.Base, QtGui.QBrush(color))
        self.setPalette(pal)
        
        topLayout = QtGui.QVBoxLayout(self)
        topLayout.setSpacing(0)
        topLayout.setMargin(0)
        self.setLayout(topLayout)

        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

        layout = QtGui.QGridLayout()
        layout.setSpacing(2)
        layout.setMargin(2)
        topLayout.addLayout(layout)

        self.edits = []
        texts = ['Vistrail', 'Index', 'Created by']
        for i in xrange(len(texts)):
            label = QInfoLabel(texts[i])
            layout.addWidget(label, i, 0, 1, 1)
            edit = QInfoLineEdit()
            self.edits.append(edit)
            layout.addWidget(edit, i, 1, 1, 1)

        topLayout.addStretch()
        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

    def updateInfo(self, info):
        """ updateInfo(info: (dict, pid)) -> None
        Update the information of a pipeline info
        
        """
        if info!=None and info[0]['locator']!=None:
            self.edits[0].setText(str(info[0]['locator'].name))
            self.edits[1].setText('(Pipeline: %d, Module: %d)'
                                  % (info[0]['version'], info[0]['moduleId']))
            self.edits[2].setText(str(info[0]['reason']))
        else:
            for edit in self.edits:
                edit.setText('N/A')

################################################################################

class QCellManipulator(QtGui.QFrame):
    """
    QCellManipulator contains several dragable icons that allow users
    to move/copy or perform some operation from one cell to
    another. It also inclues a button for update the pipeline under
    the cell to be a new version on the pipeline. It is useful for the
    parameter exploration talks back to the builder
    
    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)

        layout.addStretch()

        bLayout = QtGui.QHBoxLayout()
        layout.addLayout(bLayout)                

        bInfo = [(':/images/copy_cell.png',
                  'Drag to copy this cell to another place',
                  'copy', 'Copy'),
                 (':/images/move_cell.png',
                  'Drag to move this cell to another place',
                  'move', 'Move'),
                 (':/images/create_analogy.png',
                  'Drag to create an analogy between this cell and another one',
                  'create_analogy', 'Create\nAnalogy'),
                 (':/images/apply_analogy.png',
                  'Drag to apply the current analogy to this cell and put it '
                  'at another place', 'apply_analogy', 'Apply\nAnalogy')]
        
        self.buttons = []
        
        bLayout.addStretch()
        for b in bInfo:
            button = QCellDragLabel(QtGui.QPixmap(b[0]))
            button.setToolTip(b[1])
            button.setStatusTip(b[1])
            button.action = b[2]
            vLayout = QtGui.QVBoxLayout()
            vLayout.addWidget(button)
            label = QtGui.QLabel(b[3])
            label.setAlignment(QtCore.Qt.AlignCenter)
            vLayout.addWidget(label)
            bLayout.addLayout(vLayout)
            self.buttons.append(button)
            self.buttons.append(label)

        self.updateButton = QtGui.QToolButton()
        self.updateButton.setIconSize(QtCore.QSize(64, 64))
        self.updateButton.setIcon(QtGui.QIcon(QtGui.QPixmap(            
            ':/images/update.png')))
        self.updateButton.setAutoRaise(True)
        self.updateButton.setToolTip('Add this cell as a new version')
        self.updateButton.setStatusTip(self.updateButton.toolTip())
        self.updateButton.setText('Create Version')
        self.updateButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.connect(self.updateButton, QtCore.SIGNAL('clicked(bool)'),
                     self.updateVersion)
        self.buttons.append(self.updateButton)

        self.locateButton = QtGui.QToolButton()
        self.locateButton.setIconSize(QtCore.QSize(64, 64))
        self.locateButton.setIcon(QtGui.QIcon(QtGui.QPixmap(            
            ':/images/locate.png')))
        self.locateButton.setAutoRaise(True)
        self.locateButton.setToolTip('Select this pipeline in the version tree ')
        self.locateButton.setStatusTip(self.locateButton.toolTip())
        self.locateButton.setText('Locate Version')
        self.locateButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.connect(self.locateButton, QtCore.SIGNAL('clicked(bool)'),
                     self.locateVersion)
        self.buttons.append(self.locateButton)

        
        uLayout = QtGui.QHBoxLayout()
        uLayout.addStretch()
        uLayout.addWidget(self.locateButton)
        uLayout.addWidget(self.updateButton)
        uLayout.addStretch()
        layout.addLayout(uLayout)
            
        bLayout.addStretch()

        layout.addStretch()

        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)
        
    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a cell to the manipulator, so it knows where to drag
        and drop
        
        """
        self.cellInfo = (sheet, row, col)
        for b in self.buttons:
            if hasattr(b, 'updateCellInfo'):
                b.updateCellInfo(self.cellInfo)
            if sheet and sheet.getCell(row, col)!=None:
                widget = sheet.getCell(row, col)
                b.setVisible(not isinstance(widget, QCellPresenter) or
                             widget.cellWidget is not None)
            else:
                b.setVisible(False)
        self.updateButton.setVisible(False)
        if sheet:
            info = sheet.getCellPipelineInfo(row, col)
            if info:
                self.updateButton.setVisible(len(info[0]['actions'])>0)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the other cell info
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellInfo'):
            if (mimeData.cellInfo==self.cellInfo or
                mimeData.cellInfo[0]==None or
                self.cellInfo[0]==None):
                event.ignore()
            else:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
                self.highlight()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves
        
        """
        self.highlight(False)
        
    def dropEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves
        
        """
        self.highlight(False)
        mimeData = event.mimeData()
        action = mimeData.action
        cellInfo = mimeData.cellInfo
        manipulator = mimeData.manipulator
        if action in ['move', 'copy', 'create_analogy', 'apply_analogy']:
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            
            if action=='move':
                self.cellInfo[0].swapCell(self.cellInfo[1], self.cellInfo[2],
                                          cellInfo[0], cellInfo[1], cellInfo[2])
                manipulator.assignCell(*self.cellInfo)
                self.assignCell(*cellInfo)
                
            if action=='copy':
                cellInfo[0].copyCell(cellInfo[1], cellInfo[2],
                                     self.cellInfo[0], self.cellInfo[1],
                                     self.cellInfo[2])
                
            if action=='create_analogy':
                p1Info = cellInfo[0].getPipelineInfo(cellInfo[1], cellInfo[2])
                p2Info = self.cellInfo[0].getPipelineInfo(self.cellInfo[1],
                                                          self.cellInfo[2])
                if p1Info!=None and p2Info!=None:
                    analogy = analogy_api.SpreadsheetAnalogy()
                    analogy.createAnalogy(p1Info, p2Info)

            if action=='apply_analogy':
                p1Info = cellInfo[0].getPipelineInfo(cellInfo[1], cellInfo[2])
                analogy = analogy_api.SpreadsheetAnalogy()
                newPipeline = analogy.applyAnalogy(p1Info)
                if newPipeline:
                    self.cellInfo[0].executePipelineToCell(newPipeline,
                                                           self.cellInfo[1],
                                                           self.cellInfo[2],
                                                           'Apply Analogy')

        else:
            event.ignore()
                    
        
    def highlight(self, on=True):
        """ highlight(on: bool) -> None
        Highlight the cell as if being selected
        
        """
        if on:
            self.innerRubberBand.setGeometry(self.rect())
            self.innerRubberBand.show()
        else:
            self.innerRubberBand.hide()

    def updateVersion(self):
        """ updateVersion() -> None        
        Use the performed action of this cell to add back a new
        version to the version tree
        
        """
        spreadsheetController = spreadsheet_controller.spreadsheetController
        builderWindow = spreadsheetController.getBuilderWindow()
        if builderWindow:
            info = self.cellInfo[0].getCellPipelineInfo(self.cellInfo[1],
                                                        self.cellInfo[2])
            if info:
                info = info[0]
                view = builderWindow.ensureVistrail(info['locator'])
                if view:
                    controller = view.controller
                    controller.change_selected_version(info['version'])
                    controller.perform_param_changes(info['actions'])
                    # controller.performBulkActions(info['actions'])

    def locateVersion(self):
        """ locateVersion() -> None        
        Select the version node on the version that has generated this cell
        
        """
        spreadsheetController = spreadsheet_controller.spreadsheetController
        builderWindow = spreadsheetController.getBuilderWindow()
        if builderWindow:
            info = self.cellInfo[0].getCellPipelineInfo(self.cellInfo[1],
                                                        self.cellInfo[2])
            if info:
                info = info[0]
                view = builderWindow.ensureVistrail(info['locator'])
                if view:
                    view.version_selected(info['version'], True)
                    view.version_view.select_current_version()
                    builderWindow.view_changed(view)
                    w = view.window()
                    # this has no effect
                    w.qactions['history'].trigger()
                    # so we need to use this one
                    view.history_selected()
                    view.activateWindow()

################################################################################

class QCellDragLabel(QtGui.QLabel):
    """
    QCellDragLabel is a pixmap label allowing users to drag it to
    another cell manipulator
    
    """
    def __init__(self, pixmap, parent=None):
        """ QCellDragLabel(pixmap: QPixmap, parent: QWidget) -> QCellDragLabel
        Construct the pixmap label
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.setMargin(0)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(64, 64)
        self.cursorPixmap = pixmap.scaled(self.size())

        self.startPos = None
        self.cellInfo = (None, -1, -1)
        self.action = None
        
    def updateCellInfo(self, cellInfo):
        """ updateCellInfo(cellInfo: tuple) -> None
        Update cellInfo for mime data while dragging
        
        """
        self.cellInfo = cellInfo

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Store the start position for drag event
        
        """
        self.startPos = QtCore.QPoint(event.pos())
        QtGui.QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Prepare to drag
        
        """
        p = event.pos() - self.startPos
        if p.manhattanLength()>=QtGui.QApplication.startDragDistance():
            drag = QtGui.QDrag(self)
            data = QtCore.QMimeData()
            data.cellInfo = self.cellInfo
            data.action = self.action
            data.manipulator = self.parent()
            drag.setMimeData(data)
            drag.setHotSpot(self.cursorPixmap.rect().center())
            drag.setPixmap(self.cursorPixmap)            
            drag.start(QtCore.Qt.MoveAction)
