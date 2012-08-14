package edu.utah.sci.vistrails.javaspreadsheet.rowheader;

import java.awt.Cursor;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.event.MouseEvent;

import javax.swing.event.MouseInputAdapter;


class TableRowResizer extends MouseInputAdapter {

    private static final Cursor RESIZE_CURSOR = Cursor.getPredefinedCursor(Cursor.S_RESIZE_CURSOR);
    private JTableRowHeader m_RowHeader;
    private Cursor m_OtherCursor;
    private int m_MouseYOffset;

    TableRowResizer(JTableRowHeader row_header)
    {
        m_RowHeader = row_header;
        m_OtherCursor = RESIZE_CURSOR;
    }

    private int findResizingRow(Point p, int row)
    {
        if(row == -1)
            return -1;
        Rectangle r = m_RowHeader.getHeaderRect(row);
        r.grow(0, -3);
        if(r.contains(p))
            return -1;
        int mid_point = r.y + r.height/2;
        if(p.y < mid_point)
            row -= 1;
        if(row == m_RowHeader.getRowCount() - 1)
            return -1;
        return row;
    }

    /**
     * Begins a row resize.
     */
    @Override
    public void mousePressed(MouseEvent event)
    {
        Point p = event.getPoint();

        // First find which header cell was hit
        int row = m_RowHeader.getRowIndexAt(p.y);

        // The first 3 pixels can be used to resize the cell
        // The last 3 pixels are used to resize the next cell
        row = findResizingRow(p, row);

        if(row != -1)
        {
            m_RowHeader.setResizingRow(row);
            m_MouseYOffset = p.y - m_RowHeader.getRowHeight(row);
        }
    }

    @Override
    public void mouseDragged(MouseEvent event)
    {
        int resizing_row = m_RowHeader.getResizingRow();
        if(resizing_row != -1)
        {
            int new_height = event.getY() - m_MouseYOffset;
            m_RowHeader.setRowHeight(resizing_row, new_height);
        }
    }

    /**
     * Changes the cursor to indicate that the row can be resized.
     */
    @Override
    public void mouseMoved(MouseEvent event)
    {
        Point p = event.getPoint();
        int row = m_RowHeader.getRowIndexAt(p.y);
        boolean can_resize = findResizingRow(p, row) != -1;
        if(can_resize != (m_RowHeader.getCursor() == RESIZE_CURSOR))
            swapCursor();
    }

    void swapCursor()
    {
        Cursor tmp = m_RowHeader.getCursor();
        m_RowHeader.setCursor(m_OtherCursor);
        m_OtherCursor = tmp;
    }

    @Override
    public void mouseReleased(MouseEvent event)
    {
        m_RowHeader.setResizingRow(-1);
    }

}
