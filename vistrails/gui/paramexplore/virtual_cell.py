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
""" This file describe the virtual cell layout widget used in
Parameter Exploration Tab """

from PyQt4 import QtCore, QtGui
from core.inspector import PipelineInspector
from core.modules.module_registry import get_module_registry
from core.vistrail.action import Action
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.port import Port
from core.vistrail import module
from core.vistrail import connection
import db.services.action
# FIXME broke this as Actions have been changed around
#
# from core.vistrail.action import AddModuleAction, AddConnectionAction, \
#      DeleteConnectionAction, ChangeParameterAction
from gui.common_widgets import QToolWindowInterface
from gui.paramexplore.pe_pipeline import QAnnotatedPipelineView
from gui.theme import CurrentTheme
import copy
import string

################################################################################

def decodeConfiguration(pipeline, cells):
    """ decodeConfiguration(pipeline: Pipeline,
        cells: configuration) -> decoded cells
    Convert cells of type [{(type,id): (row, column)}) to
    (mId, row, col) in a particular pipeline

    """
    decodedCells = []
    inspector = PipelineInspector()
    inspector.inspect_spreadsheet_cells(pipeline)
    inspector.inspect_ambiguous_modules(pipeline)
    orig_pipeline = pipeline

    for id_list in inspector.spreadsheet_cells:
        pipeline = orig_pipeline
        id_iter = iter(id_list)
        m = pipeline.modules[id_iter.next()]
        m_id = m.id
        for m_id in id_iter:
            pipeline = m.pipeline
            m = pipeline.modules[m_id]
        name = m.name

        if len(id_list) == 1 and m_id in inspector.annotated_modules:
            idx = inspector.annotated_modules[m_id]
        elif tuple(id_list) in inspector.annotated_modules:
            idx = inspector.annotated_modules[tuple(id_list)]
        else:
            idx = -1
        (vRow, vCol) = cells[(name, idx)]
        if len(id_list) == 1:
            decodedCells.append((m_id, vRow, vCol))
        else:
            decodedCells.append((tuple(id_list), vRow, vCol))
    return decodedCells

def _positionPipelines(sheetPrefix, sheetCount, rowCount, colCount,
                       pipelines, config, originalPipeline, controller):
    """ _positionPipelines(sheetPrefix: str, sheetCount: int, rowCount: int,
                           colCount: int, pipelines: list of Pipeline)
                           -> list of Pipelines
    Apply the virtual cell location to a list of pipelines in a
    parameter exploration given that pipelines has multiple chunk
    of sheetCount x rowCount x colCount cells

    """

    # at this point, we know that we have the spreadsheet loaded
    from packages.spreadsheet.spreadsheet_execute import \
        assignPipelineCellLocations

    registry = get_module_registry()
    (vRCount, vCCount, cells) = config
    modifiedPipelines = []
    for pId in xrange(len(pipelines)):
        root_pipeline = copy.copy(pipelines[pId])
        col = pId % colCount
        row = (pId / colCount) % rowCount
        sheet = (pId / (colCount*rowCount)) % sheetCount

        decodedCells = decodeConfiguration(root_pipeline, cells)
        # still need to go through each separately
        for (id_list, vRow, vCol) in decodedCells:
            sheet_name = "%s %d" % (sheetPrefix, sheet)
            min_row_count = rowCount * vRCount
            min_col_count = colCount * vCCount
            real_row = row*vRCount+vRow+1
            real_col = col*vCCount+vCol+1
            root_pipeline = \
                assignPipelineCellLocations(root_pipeline, sheet_name,
                                            real_row, real_col,
                                            [id_list], min_row_count,
                                            min_col_count)

        modifiedPipelines.append(root_pipeline)
    return modifiedPipelines


class QVirtualCellWindow(QtGui.QFrame, QToolWindowInterface):
    """
    QVirtualCellWindow contains a caption, a virtual cell
    configuration
    
    """
    def __init__(self, parent=None):
        """ QVirtualCellWindow(parent: QWidget) -> QVirtualCellWindow
        Initialize the widget

        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setWindowTitle('Spreadsheet Virtual Cell')
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setMargin(2)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)
        
        label = QtGui.QLabel('Arrange the cell(s) below to construct'
                             ' a virtual cell')
        font = QtGui.QFont(label.font())
        label.setFont(font)
        label.setWordWrap(True)        
        vLayout.addWidget(label)

        hLayout = QtGui.QVBoxLayout()
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        vLayout.addLayout(hLayout)
        self.config = QVirtualCellConfiguration()
        self.config.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                  QtGui.QSizePolicy.Maximum)
        hLayout.addWidget(self.config)
        hPadWidget = QtGui.QWidget()
        hLayout.addWidget(hPadWidget)
        hPadWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Ignored)

        vPadWidget = QtGui.QWidget()
        vLayout.addWidget(vPadWidget)
        vPadWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)

        self.inspector = PipelineInspector()
        self.pipeline = None

    def updateVirtualCell(self, pipeline):        
        """ updateVirtualCell(pipeline: QPipeline) -> None
        Setup the virtual cells given a pipeline
        
        """
        self.pipeline = pipeline
        if self.pipeline:
            self.inspector.inspect_spreadsheet_cells(self.pipeline)
            self.inspector.inspect_ambiguous_modules(self.pipeline)
            cells = []
            for id_list in self.inspector.spreadsheet_cells:
                pipeline = self.pipeline
                id_iter = iter(id_list)
                m = pipeline.modules[id_iter.next()]
                m_id = m.id
                for m_id in id_iter:
                    pipeline = m.pipeline
                    m = pipeline.modules[m_id]
                    
                name = m.name
                if len(id_list) == 1 and \
                        m_id in self.inspector.annotated_modules:
                    cells.append((name, self.inspector.annotated_modules[m_id]))
                elif tuple(id_list) in self.inspector.annotated_modules:
                    cells.append((name, self.inspector.annotated_modules[ \
                                tuple(id_list)]))
                else:
                    cells.append((name, -1))
            self.config.configVirtualCells(cells)
        else:

            self.config.clear()

    def getConfiguration(self):
        """ getConfiguration() -> info (see below)
        Return the current configuration of the virtual cell. The
        information is:
        info = (rowCount, columnCount,
                {(type,id): (row, column)})
        """
        return self.config.getConfiguration()
                
    def setConfiguration(self, info):
        """ setConfiguration(info) -> None (see below)
        Set the configuration of the virtual cell. The
        information is:
        info = {(type, id): (row, column)}
          or
        info = (rowCount, columnCount,
                {(type, id): (row, column)})
        The second form is allowed so that the output of
        getConfiguration could be passed directly to
        setConfiguration (the dimensions aren't used).
        """
        self.config.setConfiguration(info)

    def positionPipelines(self, sheetPrefix, sheetCount, rowCount, colCount,
                          pipelines, controller):
        """ positionPipelines(sheetPrefix: str, sheetCount: int, rowCount: int,
                              colCount: int, pipelines: list of Pipeline)
                              -> list of Pipelines
        Apply the virtual cell location to a list of pipelines in a
        parameter exploration given that pipelines has multiple chunk
        of sheetCount x rowCount x colCount cells
        
        """
        return _positionPipelines(sheetPrefix, sheetCount, rowCount, colCount, 
                                  pipelines, self.getConfiguration(), 
                                  self.pipeline, controller)

class QVirtualCellConfiguration(QtGui.QWidget):
    """
    QVirtualCellConfiguration is a widget provide a virtual layout of
    the spreadsheet cell. Given a number of cells want to layout, it
    will let users interactively select where to put a cell in a table
    layout to construct a virtual cell out of that.
    
    """
    def __init__(self, parent=None):
        """ QVirtualCellConfiguration(parent: QWidget)
                                      -> QVirtualCellConfiguration
        Initialize the widget

        """
        QtGui.QWidget.__init__(self, parent)
        self.rowCount = 1
        self.colCount = 1
        gridLayout = QtGui.QGridLayout(self)
        gridLayout.setSpacing(0)
        self.setLayout(gridLayout)
        label = QVirtualCellLabel('')
        self.layout().addWidget(label, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        self.cells = [[label]]
        self.numCell = 1

    def clear(self):
        """ clear() -> None
        Remove and delete all widgets in self.gridLayout
        
        """
        while True:
            item = self.layout().takeAt(0)
            if item==None:
                break
            self.disconnect(item.widget(),
                            QtCore.SIGNAL('finishedDragAndDrop'),
                            self.compressCells)
            item.widget().deleteLater()
            del item
        self.cells = []
        self.numCell = 0

    def configVirtualCells(self, cells):
        """ configVirtualCells(cells: [(str, int)]) -> None        
        Given a list of cell types and ids, this will clear old
        configuration and start a fresh one.
        
        """
        self.clear()
        self.numCell = len(cells)
        row = []
        for i in xrange(self.numCell):
            label = QVirtualCellLabel(*cells[i])
            row.append(label)
            self.layout().addWidget(label, 0, i, 1, 1, QtCore.Qt.AlignCenter)
            self.connect(label, QtCore.SIGNAL('finishedDragAndDrop'),
                         self.compressCells)
        self.cells.append(row)

        for r in xrange(self.numCell-1):
            row = []
            for c in xrange(self.numCell):
                label = QVirtualCellLabel()
                row.append(label)
                self.layout().addWidget(label, r+1, c, 1, 1,
                                        QtCore.Qt.AlignCenter)
                self.connect(label, QtCore.SIGNAL('finishedDragAndDrop'),
                             self.compressCells)
            self.cells.append(row)

    def compressCells(self):
        """ compressCells() -> None
        Eliminate all blank cells
        
        """
        # Check row by row first
        visibleRows = []
        for r in xrange(self.numCell):
            row = self.cells[r]
            hasRealCell = [True for label in row if label.type]!=[]
            if hasRealCell:                
                visibleRows.append(r)

        # Move rows up
        for i in xrange(len(visibleRows)):
            for c in xrange(self.numCell):
                label = self.cells[visibleRows[i]][c]
                if label.type==None:
                    label.type = ''
                self.cells[i][c].setCellData(label.type, label.id)

        # Now check column by column        
        visibleCols = []
        for c in xrange(self.numCell):
            hasRealCell = [True
                           for r in xrange(self.numCell)
                           if self.cells[r][c].type]!=[]
            if hasRealCell:
                visibleCols.append(c)
                    
        # Move columns left
        for i in xrange(len(visibleCols)):
            for r in xrange(self.numCell):
                label = self.cells[r][visibleCols[i]]
                if label.type==None:
                    label.type = ''
                self.cells[r][i].setCellData(label.type, label.id)

        # Clear redundant rows
        for i in xrange(self.numCell-len(visibleRows)):
            for label in self.cells[i+len(visibleRows)]:
                label.setCellData(None, -1)
                
        # Clear redundant columns
        for i in xrange(self.numCell-len(visibleCols)):
            for r in xrange(self.numCell):
                self.cells[r][i+len(visibleCols)].setCellData(None, -1)

    def getConfiguration(self):
        """ getConfiguration() -> info (see below)
        Return the current configuration of the virtual cell. The
        information is:
        info = (rowCount, columnCount,
                {(type, id): (row, column)})
        """
        result = {}
        rCount = 0
        cCount = 0
        for r in xrange(self.numCell):
            for c in xrange(self.numCell):
                cell = self.cells[r][c]
                if cell.type:
                    result[(cell.type, cell.id)] = (r, c)
                    if r+1>rCount: rCount = r+1
                    if c+1>cCount: cCount = c+1
        return (rCount, cCount, result)

    def setConfiguration(self, info):
        """ setConfiguration(info) -> None (see below)
        Set the configuration of the virtual cell. The
        information is:
        info = {(type, id): (row, column)}
          or
        info = (rowCount, columnCount,
                {(type, id): (row, column)})
        The second form is allowed so that the output of
        getConfiguration could be passed directly to
        setConfiguration (the dimensions aren't used).
        """
        if type(info) == type({}):
            result = info
        else:
            rCount, cCount, result = info
        # Reset the layout of the virtual cell to default state
        config_cells = []
        for cell_type, cell_id in result.iterkeys():
            config_cells.append((cell_type, cell_id))
        self.configVirtualCells(config_cells)
        # Unset the 0th row types/ids, since they're auto-set for the default state
        for c in xrange(len(config_cells)):
            self.cells[0][c].setCellData('', -1)
        # Set the new types/ids
        for cell_type, cell_id in config_cells:
            row, col = result[(cell_type, cell_id)]
            self.cells[row][col].setCellData(cell_type, cell_id)
        # Compress to properly reset newly empty cells
        self.compressCells()

class QVirtualCellLabel(QtGui.QLabel):
    """
    QVirtualCellLabel is a label represent a cell inside a cell. It
    has rounded shape with a caption text
    
    """
    def __init__(self, label=None, id=-1, parent=None):
        """ QVirtualCellLabel(text: QString, id: int,
                              parent: QWidget)
                              -> QVirtualCellLabel
        Construct the label image

        """
        QtGui.QLabel.__init__(self, parent)
        self.setMargin(2)
        self.cellType = None
        self.setCellData(label, id)
        self.setAcceptDrops(True)
        self.setFrameStyle(QtGui.QFrame.Panel)
        self.palette().setColor(QtGui.QPalette.WindowText,
                                CurrentTheme.HOVER_SELECT_COLOR)

    def formatLabel(self, text):
        """ formatLabel(text: str) -> str
        Convert Camel Case to end-line separator
        
        """
        if text=='':
            return 'Empty'
        lines = []
        prev = 0
        lt = len(text)
        for i in xrange(lt):
            if (not (text[i] in string.lowercase)
                and (i==lt-1 or
                     text[i+1] in string.lowercase)):
                if i>0:
                    lines.append(text[prev:i])
                prev = i
        lines.append(text[prev:])
        return '\n'.join(lines)

    def setCellData(self, cellType, cellId):
        """ setCellData(cellType: str, cellId: int) -> None Create an
        image based on the cell type and id. Then assign it to the
        label. If cellType is None, the cell will be drawn with
        transparent background. If cellType is '', the cell will be
        drawn with the caption 'Empty'. Otherwise, the cell will be
        drawn with white background containing cellType as caption and
        a small rounded shape on the lower right painted with cellId
        
        """
        self.type = cellType
        self.id = cellId
        size = QtCore.QSize(*CurrentTheme.VIRTUAL_CELL_LABEL_SIZE)
        image = QtGui.QImage(size.width() + 12,
                             size.height()+ 12,
                             QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(0)

        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.ForceOutline)
        painter = QtGui.QPainter()
        painter.begin(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.type==None:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtCore.Qt.NoBrush)
        else:
            if self.type=='':
                painter.setPen(QtCore.Qt.gray)
                painter.setBrush(QtCore.Qt.NoBrush)
            else:
                painter.setPen(QtCore.Qt.black)
                painter.setBrush(QtCore.Qt.lightGray)
        painter.drawRoundRect(QtCore.QRectF(0.5, 0.5, image.width()-1,
                                            image.height()-1), 25, 25)

        painter.setFont(font)
        if self.type!=None:
            painter.drawText(QtCore.QRect(QtCore.QPoint(6, 6), size),
                             QtCore.Qt.AlignCenter | QtCore.Qt.TextWrapAnywhere,
                                self.formatLabel(self.type))
            # Draw the lower right corner number if there is an id
            if self.id>=0 and self.type:
                QAnnotatedPipelineView.drawId(painter, image.rect(), self.id,
                                              QtCore.Qt.AlignRight |
                                              QtCore.Qt.AlignBottom)

        painter.end()

        self.setPixmap(QtGui.QPixmap.fromImage(image))

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Start the drag and drop when the user click on the label
        
        """
        if self.type:
            mimeData = QtCore.QMimeData()
            mimeData.cellData = (self.type, self.id)

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(self.pixmap().rect().center())
            drag.setPixmap(self.pixmap())
            
            self.setCellData('', -1)
            
            drag.start(QtCore.Qt.MoveAction)
            if mimeData.cellData!=('', -1):
                self.setCellData(*mimeData.cellData)
            self.emit(QtCore.SIGNAL('finishedDragAndDrop'))

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the other cell info
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellData'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            self.highlight()
        else:
            event.ignore()

    def dropEvent(self, event):        
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to set the current cell
        
        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellData'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()            
            if (self.type,self.id)!=(mimeData.cellData[0],mimeData.cellData[1]):
                oldCellData = (self.type, self.id)
                self.setCellData(*mimeData.cellData)
                mimeData.cellData = oldCellData
        else:
            event.ignore()
        self.highlight(False)

    def dragLeaveEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Un highlight the current cell
        
        """
        self.highlight(False)

    def highlight(self, on=True):
        """ highlight(on: bool) -> None
        Highlight the cell as if being selected
        
        """
        if on:
            self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Plain)
        else:
            self.setFrameStyle(QtGui.QFrame.Panel)
                
################################################################################

if __name__=="__main__":        
    import sys
    import gui.theme
    app = QtGui.QApplication(sys.argv)
    gui.theme.initializeCurrentTheme()
    vc = QVirtualCellConfiguration()
    vc.configVirtualCells(['VTKCell', 'ImageViewerCell', 'RichTextCell'])
    vc.show()
    sys.exit(app.exec_())
