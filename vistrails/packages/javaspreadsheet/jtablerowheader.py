from java.awt import Dimension

from javax.swing import JTable, UIManager
from javax.swing.table import AbstractTableModel, DefaultTableCellRenderer


class RowHeaderModel(AbstractTableModel):
    """The TableModel for the row header.

    It returns the line number of each row.
    """
    def __init__(self, tableToMirror):
        self.table = tableToMirror

    # @Override
    def getRowCount(self):
        return self.table.getModel().getRowCount()

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
        self.configure(table)

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
