from java.awt import Cursor, Dimension, Rectangle

from javax.swing import JTable, UIManager, JViewport
from javax.swing.event import MouseInputAdapter
from javax.swing.table import AbstractTableModel, DefaultTableCellRenderer


class RowHeaderModel(AbstractTableModel):
    """The TableModel for the row header.

    It returns the line number of each row.
    """
    def __init__(self, tableToMirror):
        self._table = tableToMirror

    # @Override
    def getRowCount(self):
        return self._table.getModel().getRowCount()

    # @Override
    def getColumnCount(self):
        return 1

    # @Override
    def getValueAt(self, row, column):
        return str(row + 1)


class RowHeaderRenderer(DefaultTableCellRenderer):
    """A simple renderer that simply returns the Cell"""
    # @Override
    def getTableCellRendererComponent(self, table, value, isSelected,
                                      hasFocus, row, column):
        self.setBackground(UIManager.getColor('TableHeader.background'))
        self.setForeground(UIManager.getColor('TableHeader.foreground'))
        self.setBorder(UIManager.getBorder('TableHeader.cellBorder'))
        self.setFont(UIManager.getFont('TableHeader.font'))
        self.setValue(value)
        return self


class JTableRowHeader(JTable):
    """A single-column JTabel showing a row header for another JTable.

    Taken from the book "Java(tm) Platform Performance, chapter 10.
    (c) 2001, Sun Microsystems, Inc
    http://java.sun.com/docs/books/performance/1st_edition/html/JPSwingModels.fm.html
    """
    def __init__(self, table):
        super(JTableRowHeader, self).__init__(RowHeaderModel(table))
        self.renderer = RowHeaderRenderer()
        self._table = table
        self.configure(table)
        self.resizing_row = None
        self.setFillsViewportHeight(True)

        resize_handler = TableRowResizer(table, self)
        self.addMouseListener(resize_handler)
        self.addMouseMotionListener(resize_handler)

    def configure(self, table):
        self.setRowHeight(table.getRowHeight())
        self.setIntercellSpacing(Dimension(0, 0))
        self.setShowHorizontalLines(False)
        self.setShowVerticalLines(False)

    # @Override
    def getPreferredScrollableViewportSize(self):
        return Dimension(32, super(JTableRowHeader, self).getPreferredSize().height)

    # @Override
    def getDefaultRenderer(self, c):
        return self.renderer

    def getRowIndexAt(self, y):
        if y < 0:
            return -1
        for row in xrange(self.getRowCount()):
            y -= self.getRowHeight(row)
            if y < 0:
                return row
        return -1

    def getHeaderRect(self, row):
        r = Rectangle()
        r.width = self.getWidth()

        if row < 0:
            r.height = 0
        elif row >= self.getRowCount():
            r.height = 0
        else:
            for i in xrange(row):
                r.y += self.getRowHeight(i)
            r.height = self.getRowHeight(row)
        return r

    # @Override
    def setRowHeight(self, a, b=None):
        if b == None:
            # JTable#setRowHeight(int height)
            if a < 6:
                a = 6
            JTable.setRowHeight(self, a)
        else:
            # JTable#setRowHeight(int row, int height
            if b < 6:
                b = 6
            JTable.setRowHeight(self, a, b)
            self._table.setRowHeight(a, b)

    # Override
    def getScrollableTracksViewportHeight(self):
        return True

    # @Override
    def doLayout(self):
        JTable.doLayout(self)

        new_height = self.getHeight()

        # We resize the rows to keep the same total height
        # If a row is being resized, we try to only affect the following ones
        if self.resizing_row is not None:
            # Total current height of the following rows
            total_height = sum([self.getRowHeight(i)
                                for i in xrange(self.resizing_row + 1,
                                                self.getRowCount())])
            # New height of the following rows
            height = self.getHeight() - sum(
                    self.getRowHeight(i)
                    for i in xrange(self.resizing_row + 1))
            factor = float(height)/total_height

            for i in xrange(self.resizing_row + 1, self.getRowCount()):
                self.setRowHeight(i, int(self.getRowHeight(i)*factor))

        total_height = sum([self.getRowHeight(i)
                            for i in xrange(self.getRowCount())])
        total_height -= 6 * self.getRowCount()
        new_height -= 6 * self.getRowCount()
        factor = float(new_height)/total_height

        for i in xrange(self.getRowCount()):
            self.setRowHeight(i, 6 + int((self.getRowHeight(i)-6)*factor))


class TableRowResizer(MouseInputAdapter):
    RESIZE_CURSOR = Cursor.getPredefinedCursor(Cursor.S_RESIZE_CURSOR)

    def __init__(self, table, row_header):
        self._table = table
        self._row_header = row_header
        self._other_cursor = self.RESIZE_CURSOR

    def _findResizingRow(self, p, row):
        if row == -1:
            return -1
        r = self._row_header.getHeaderRect(row)
        r.grow(0, -3)
        if r.contains(p):
            return -1
        mid_point = r.y + r.height/2
        if p.y < mid_point:
            row -= 1
        if row == self._row_header.getRowCount()-1:
            return -1
        return row

    # @Override
    def mousePressed(self, event):
        """Begins a row resize.
        """
        p = event.getPoint()

        # First find which header cell was hit
        row = self._row_header.getRowIndexAt(p.y)

        # The first 3 pixels can be used to resize the cell
        # The last 3 pixels are used to resize the next cell
        row = self._findResizingRow(p, row)

        if row != -1:
            self._row_header.resizing_row = row
            self._mouse_Y_offset = p.y - self._row_header.getRowHeight(row)

    # @Override
    def mouseDragged(self, event):
        resizing_row = self._row_header.resizing_row
        if resizing_row != None:
            new_height = event.getY() - self._mouse_Y_offset
            self._row_header.setRowHeight(resizing_row, new_height)

    # @Override
    def mouseMoved(self, event):
        """Changes the cursor to indicate that the row can be resized.
        """
        p = event.getPoint()
        row = self._row_header.getRowIndexAt(p.y)
        can_resize = self._findResizingRow(
                p, row) != -1
        if can_resize != (self._row_header.getCursor() == self.RESIZE_CURSOR):
            self._swapCursor()

    def _swapCursor(self):
        tmp = self._row_header.getCursor()
        self._row_header.setCursor(self._other_cursor)
        self._other_cursor = tmp

    # @Override
    def mouseReleased(self, event):
        self._row_header.resizing_row = None
