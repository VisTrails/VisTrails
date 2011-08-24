###############################################################################
##
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
#   CellHelpers
#   CellResizer
#   CellResizerConfig
################################################################################
from PyQt4 import QtCore, QtGui

################################################################################

class CellResizerConfig(object):
    """
    CellResizerConfig can be used to config different parameters of
    the CellResizer widget such as shape, mask, pixmap, color, size,
    and cursor. By default, it has a black, triangular shape of size
    25x25. In order to change the shape, we have to override this
    class

    """
    def __init__(self, size=25, color=QtGui.QColor(0,0,0)):
        """ CellResizerConfig(size: int, color: QColor) -> CellResizerConfig
        Create mask and pixmap of a triangular shape with the specifc size
        and color
        
        """
        self.size = size
        self.transparentColor = QtGui.QColor(QtCore.Qt.blue)
        self.image = QtGui.QImage(size,size,QtGui.QImage.Format_RGB32)
        for i in xrange(size):
            for j in xrange(size):
                if i+j<size-1:
                    self.image.setPixel(i, j, self.transparentColor.rgb())
                else:
                    if i+j==size-1 or i==size-1 or j==size-1:
                        self.image.setPixel(i, j,
                                            QtGui.QColor(QtCore.Qt.white).rgb())
                    else:
                        self.image.setPixel(i, j, color.rgb())
        self.pixmapVar = self.maskVar = self.cursorVar = None

    def pixmap(self):
        """ pixmap() -> QPixmap
        Return the pixmap of the resizer shape
        
        """
        if not self.pixmapVar:
            self.pixmapVar = QtGui.QPixmap.fromImage(self.image)
        return self.pixmapVar

    def mask(self):
        """ mask() -> QRegion
        Return only the region of the resizer that will be shown on screen
        
        """
        if not self.maskVar:
            mask = self.pixmap().createMaskFromColor(self.transparentColor)
            self.maskVar = QtGui.QRegion(mask)
        return self.maskVar

    def cursor(self):
        """ cursor() -> QCursor
        Return the cursor that will be shown inside the resizer
        
        """
        return QtGui.QCursor(QtCore.Qt.SizeFDiagCursor)

class CellResizer(QtGui.QLabel):
    """
    CellResizer is a customized shape SizeGrip that stays on top of
    the widget, moving this size grip will end up resizing the
    corresponding cell in the table. This is different from QSizeGrip
    because it allows overlapping on top of the widget

    """
    def __init__(self, sheet, config=CellResizerConfig(), parent=None):
        """ CellResizer(sheet: SpreadsheetSheet,
                        config: subclass of CellResizerConfig,
                        parent: QWidget) -> CellResizer
        Initialize the size grip with the default triangular shape
        
        """
        QtGui.QLabel.__init__(self,sheet)
        self.setFixedSize(config.size, config.size)
        self.setPixmap(config.pixmap())
        self.setMask(config.mask())
        self.setCursor(config.cursor())
        self.setStatusTip("Left/Right-click drag to resize the underlying"
                          "cell or the whole spreadsheet ")
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sheet = sheet
        self.config = config
        self.resizeAll = False
        self.dragging = False
        self.lastPos = None
        self.row = -1
        self.col = -1
        self.hide()

    def setDragging(self,b):        
        """ setDragging(b: boolean) -> None
        Set the resizer state to busy dragging
        
        """
        self.dragging = b

    def snapTo(self,row,col):
        """ snapTo(row, col) -> None
        Assign which row and column the resizer should be controlling
        
        """
        self.row = row
        self.col = col

    def adjustPosition(self, rect):
        """ adjustPosition(rect: QRect) -> None
        Adjust resizer position to be on the bottom-right corner of the cell
        
        """
        p = self.parent().mapFromGlobal(rect.topLeft())
        self.move(p.x()+rect.width()-self.width(),
                  p.y()+rect.height()-self.height())

    def mousePressEvent(self,e):
        """ mousePressEvent(e: QMouseEvent) -> None        
        Handle Qt mouse press event to track if we need to resize
        either left or right mouse button is clicked
        
        """
        if self.col>=0:
            if e.button()==QtCore.Qt.LeftButton:
                self.resizeAll = False
                self.dragging = True
            if e.button()==QtCore.Qt.RightButton and not self.sheet.fitToWindow:
                self.resizeAll = True
                self.dragging = True
            self.lastPos = (e.globalX()-self.sheet.columnWidth(self.col),
                            e.globalY()-self.sheet.rowHeight(self.row))

    def mouseReleaseEvent(self,e):
        """ mouseReleaseEvent(e: QMouseEvent) -> None
        Handle Qt mouse release event to clean up all state
        
        """
        if (e.button()==QtCore.Qt.LeftButton or
            e.button()==QtCore.Qt.RightButton):
            self.dragging = False

    def mouseMoveEvent(self,e):
        """ mouseMoveEvent(e: QMouseEvent) -> None        
        Interactively resize the corresponding column and row when the
        mouse moves
        
        """
        if self.dragging:
            hSize = self.sheet.columnWidth(self.col)
            vSize = self.sheet.rowHeight(self.row)
            hd = e.globalX() - self.lastPos[0] - hSize
            vd = e.globalY() - self.lastPos[1] - vSize
            
            # All sections should have the same size (Right-Click)
            if self.resizeAll:
                # Resize the columns first
                dS = int(hd / (self.col+1))
                mS = hd % (self.col+1)
                for i in xrange(self.sheet.columnCount()):                    
                    if i>self.col:
                        newValue = hSize+dS
                    else:
                        newValue = self.sheet.columnWidth(i)+dS+(i<mS)
                    self.sheet.setColumnWidth(i, newValue)
                # Then resize the rows
                dS = int(vd / (self.row+1))
                mS = vd % (self.row+1)
                for i in xrange(self.sheet.rowCount()):                    
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

class CellHelpers(object):
    """
    CellHelpers is a container include CellResizer that will shows up
    whenever the Ctrl key is hold down and the mouse hovers the cell.

    """
    def __init__(self, sheet, resizerInstance=None):
        """ CellHelpers(sheet: SpreadsheetSheet,
                        resizerInstance: CellResizer) -> CellHelpers
        Initialize with  a cell resizer
        
        """
        self.sheet = sheet
        self.resizer = resizerInstance
        self.row = -1
        self.col = -1
        
    def snapTo(self, row, col):
        """ snapTo(row: int, col: int) -> None
        Assign the resizer to the correct cell
        
        """
        if row>=0 and ((row!=self.row) or (col!=self.col)):
            self.hide()
            self.row = row
            self.col = col
            if self.resizer:
                self.resizer.snapTo(row,col)
            self.adjustPosition()

    def adjustPosition(self):
        """ adjustPosition() -> None
        Adjust the resizer
        
        """
        rect = self.sheet.getCellGlobalRect(self.row, self.col)
        if self.resizer:
            self.resizer.adjustPosition(rect)

    def show(self):
        """ show() -> None
        An helper function derived from setVisible
        
        """
        self.setVisible(True)

    def hide(self):
        """ hide() -> None
        An helper function derived from setVisible
        
        """
        self.setVisible(False)

    def setVisible(self,b):
        """ setVisible(b: boolean) -> None
        Show/hide the cell helpers
        """
        if self.resizer:
            self.resizer.setVisible(b)
        if not b and self.resizer:
            self.resizer.setDragging(False)

    def isInteracting(self):
        """ isInteracting() -> boolean
        Check to see if the helper is in action with the resizer
        
        """
        if self.resizer:
            return self.resizer.dragging
        else:
            return False
