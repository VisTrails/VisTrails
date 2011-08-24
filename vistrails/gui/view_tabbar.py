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
""" This file describes a flexible tabbar to move the tabs around or
split it out to a dock widget

QInteractiveTabBar
"""

from PyQt4 import QtCore, QtGui

################################################################################


class QInteractiveTabBar(QtGui.QTabBar):
    """
    QInteractiveTabBar is a reduced version of StandardWidgetTabBar
    from the spreadsheet package. It lets the users move the tab
    around or even outside of the tabbar
    
    """
    def __init__(self, parent=None):
        """ QInteractiveTabBar(parent: QWidget) -> QInteractiveTabBar
        Initialize like the original QTabWidget TabBar
        
        """
        QtGui.QTabBar.__init__(self, parent)
        self.setStatusTip('Move the tabs in, out, and around'
                          ' by dragging')
        self.setDrawBase(False)
        self.editingIndex = -1
        self.editor = None        
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.startDragPos = None
        self.dragging = False
        self.targetTab = -1
        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)
        self.outerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 None)

    def indexAtPos(self, p):
        """ indexAtPos(p: QPoint) -> int Reimplement of the private
        indexAtPos to find the tab index under a point
        
        """
        if self.tabRect(self.currentIndex()).contains(p):
            return self.currentIndex()
        for i in xrange(self.count()):
            if self.isTabEnabled(i) and self.tabRect(i).contains(p):                
                return i
        return -1;

    def mousePressEvent(self, e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Handle mouse press event to see if we should start to drag tabs or not
        
        """
        QtGui.QTabBar.mousePressEvent(self, e)
        # super(QInteractiveTabBar, self).mousePressEvent(e)
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
        # super(QInteractiveTabBar, self).mouseMoveEvent(e)
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
        # super(QInteractiveTabBar, self).mouseReleaseEvent(e)
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
        for i in xrange(self.count()):
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
