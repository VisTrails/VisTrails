package edu.utah.sci.vistrails.javaspreadsheet.rowheader;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Rectangle;

import javax.swing.JTable;
import javax.swing.UIManager;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellRenderer;


public class JTableRowHeader extends JTable {

    private static class RowHeaderModel extends AbstractTableModel {

        private JTable m_TableToMirror;

        public RowHeaderModel(JTable table)
        {
            m_TableToMirror = table;
        }

        @Override
        public int getRowCount()
        {
            return m_TableToMirror.getModel().getRowCount();
        }

        @Override
        public int getColumnCount()
        {
            return 1;
        }

        @Override
        public String getValueAt(int row, int column)
        {
            return String.valueOf(row + 1);
        }

    }

    private static class RowHeaderRenderer extends DefaultTableCellRenderer {

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
        {
            setBackground(UIManager.getColor("TableHeader.background"));
            setForeground(UIManager.getColor("TableHeader.foreground"));
            setBorder(UIManager.getBorder("TableHeader.cellBorder"));
            setFont(UIManager.getFont("TableHeader.font"));
            setValue(value);
            return this;
        }

    }

    private RowHeaderRenderer m_Renderer;
    private JTable m_Table;
    private int m_ResizingRow;

    public JTableRowHeader(JTable table)
    {
        super(new RowHeaderModel(table));
        m_Renderer = new RowHeaderRenderer();
        m_Table = table;
        configure();
        m_ResizingRow = -1;
        setFillsViewportHeight(true);

        TableRowResizer resize_handler = new TableRowResizer(this);
        addMouseListener(resize_handler);
        addMouseMotionListener(resize_handler);
    }

    private void configure()
    {
        setRowHeight(m_Table.getRowHeight());
        setIntercellSpacing(new Dimension(0, 0));
        setShowHorizontalLines(false);
        setShowVerticalLines(false);
    }

    @Override
    public Dimension getPreferredScrollableViewportSize()
    {
        return new Dimension(32, super.getPreferredSize().height);
    }

    @Override
    public TableCellRenderer getDefaultRenderer(Class<?> columnClass)
    {
        return m_Renderer;
    }

    int getRowIndexAt(int y)
    {
        if(y < 0)
            return -1;
        for(int row = 0; row < getRowCount(); ++row)
        {
            y -= getRowHeight(row);
            if(y < 0)
                return row;
        }
        return -1;
    }

    Rectangle getHeaderRect(int row)
    {
        Rectangle r = new Rectangle();
        r.width = getWidth();

        if(row < 0)
            r.height = 0;
        else if(row >= getRowCount())
            r.height = 0;
        else
        {
            for(int i = 0; i < row; ++i)
                r.y += getRowHeight(i);
            r.height = getRowHeight(row);
        }
        return r;
    }

    @Override
    public void setRowHeight(int rowHeight)
    {
        if(rowHeight < 6)
            rowHeight = 6;
        super.setRowHeight(rowHeight);
    }

    @Override
    public void setRowHeight(int row, int rowHeight)
    {
        if(rowHeight < 6)
            rowHeight = 6;
        super.setRowHeight(row, rowHeight);
        m_Table.setRowHeight(row, rowHeight);
    }

    @Override
    public boolean getScrollableTracksViewportHeight()
    {
        return true;
    }

    @Override
    public void doLayout()
    {
        super.doLayout();

        int new_height = getHeight();

        // We resize the rows to keep the same total height
        // If a row is being resized, we try to only affect the following ones
        if(m_ResizingRow != -1)
        {
            int total_height = 0;
            for(int i = m_ResizingRow + 1; i < getRowCount(); ++i)
                total_height += getRowHeight(i);

            // New height of the following rows
            int height = getHeight();
            for(int i = 0; i < m_ResizingRow + 1; ++i)
                height -= getRowHeight(i);
            float factor = ((float)height)/total_height;

            for(int i = m_ResizingRow + 1; i < getRowCount(); ++i)
                setRowHeight(i, (int)(getRowHeight(i) * factor));
        }

        int total_height = 0;
        for(int i = 0; i < getRowCount(); ++i)
            total_height += getRowHeight(i);
        total_height -= 6 * getRowCount();
        new_height -= 6 * getRowCount();
        float factor = ((float)new_height)/total_height;

        for(int i = 0; i < getRowCount(); ++i)
            setRowHeight(i, 6 + (int)((getRowHeight(i) - 6) * factor));
    }

    int getResizingRow()
    {
        return m_ResizingRow;
    }

    void setResizingRow(int row)
    {
        m_ResizingRow = row;
    }

}
