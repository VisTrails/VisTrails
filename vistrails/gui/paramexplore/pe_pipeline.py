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
""" This containing a subclassed QGraphicsView that allows View the
pipeline in a specific way in the parameter exploration window
"""
from PyQt4 import QtCore, QtGui
from core.inspector import PipelineInspector
from gui.common_widgets import QToolWindowInterface
from gui.pipeline_view import QPipelineView, QGraphicsModuleItem
from gui.theme import CurrentTheme

################################################################################
class QAnnotatedPipelineView(QPipelineView, QToolWindowInterface):
    """
    QAnnotatedPipelineView subclass QPipelineView to perform some overlay
    marking on a pipeline view
    
    """
    def __init__(self, parent=None):
        """ QPipelineView(parent: QWidget) -> QPipelineView
        Initialize the graphics view and its properties
        
        """
        QPipelineView.__init__(self, parent)
        self.setWindowTitle('Annotated Pipeline')
        self.inspector = PipelineInspector()

    def sizeHint(self):
        """ sizeHint() -> QSize
        Prefer the view not so large
        
        """
        return QtCore.QSize(256, 256)

    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Paint an overlay annotation on spreadsheet cell modules
        
        """
        QPipelineView.paintEvent(self, event)
        # super(QAnnotatedPipelineView, self).paintEvent(event)
        if self.scene():
            painter = QtGui.QPainter(self.viewport())
            for mId, annotatedId in \
                    self.inspector.annotated_modules.iteritems():
                if mId not in self.scene().modules:
                    # faulty annotated_modules entry
                    continue
                item = self.scene().modules[mId]
                br = item.sceneBoundingRect()
                rect = QtCore.QRect(self.mapFromScene(br.topLeft()),
                                    self.mapFromScene(br.bottomRight()))
                QAnnotatedPipelineView.drawId(painter, rect, annotatedId)
            painter.end()

    def updateAnnotatedIds(self, pipeline):
        """ updateAnnotatedIds(pipeline: Pipeline) -> None
        Re-inspect the pipeline to get annotated ids
        
        """
        if pipeline and self.scene():
            self.inspector.inspect_ambiguous_modules(pipeline)
            self.scene().fitToView(self)

    @staticmethod
    def drawId(painter, rect, id, align=QtCore.Qt.AlignCenter):
        """ drawId(painter: QPainter, rect: QRect, id: int,
                   align: QtCore.Qt.Align) -> None
        Draw the rounded id number on a rectangular area
        
        """
        painter.save()
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(CurrentTheme.ANNOTATED_ID_BRUSH.color())
        painter.setBrush(CurrentTheme.ANNOTATED_ID_BRUSH)
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.ForceOutline)
        font.setBold(True)
        painter.setFont(font)
        fm = QtGui.QFontMetrics(font)
        size = fm.size(QtCore.Qt.TextSingleLine, str(id))
        size = max(size.width(), size.height())
        
        x = rect.left()
        if align & QtCore.Qt.AlignHCenter:
            x = rect.left() + rect.width()/2-size/2
        if align & QtCore.Qt.AlignRight:
            x = rect.left() + rect.width()-size
        y = rect.top()
        if align & QtCore.Qt.AlignVCenter:
            y = rect.top() + rect.height()/2-size/2
        if align & QtCore.Qt.AlignBottom:
            y = rect.top() + rect.height()-size
            
        newRect = QtCore.QRect(x, y, size, size)
        painter.drawEllipse(newRect)
        painter.setPen(CurrentTheme.ANNOTATED_ID_PEN)
        painter.drawText(newRect, QtCore.Qt.AlignCenter, str(id))
        painter.restore()
