package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.Point;

import javax.swing.JScrollPane;

import edu.utah.sci.vistrails.javaspreadsheet.Spreadsheet.Mode;
import edu.utah.sci.vistrails.javaspreadsheet.rowheader.JTableRowHeader;


/**
 * A sheet containing a single table.
 */
public class Sheet extends JScrollPane {

    private SpreadsheetModel m_Model;
    private SpreadsheetTable m_Table;

    Sheet(String name, Mode mode, SpreadsheetInterface interf)
    {
        m_Model = new SpreadsheetModel(name, 2, 3, mode, interf);
        m_Table = new SpreadsheetTable(m_Model);
        setViewportView(m_Table);
        setColumnHeaderView(m_Table.getTableHeader());
        setRowHeaderView(new JTableRowHeader(m_Table));
    }

    void setMode(Spreadsheet.Mode mode)
    {
        m_Model.setMode(mode);
    }

    public Cell getCell()
    {
        return getCell(null);
    }

    // TODO : Test coverage
    public Cell getCell(CellLocation location)
    {
        // Locate the requested cell
        Integer row = null, column = null;
        if(location != null)
        {
            row = location.getRow();
            column = location.getColumn();
        }

        // Should we grow the table?
        int newrowcount = m_Model.getRowCount(), newcolumncount = m_Model.getColumnCount();
        if(row != null && row >= m_Model.getRowCount())
            newrowcount = row + 1;
        if(column != null && column >= m_Model.getColumnCount())
            newcolumncount = column + 1;
        if(newrowcount != m_Model.getRowCount() || newcolumncount != m_Model.getColumnCount())
            m_Model.changeSize(newrowcount, newcolumncount);

        Point pos = findCell(m_Model, row, column);

        return (Cell)m_Model.getValueAt(pos.y, pos.x, true);
    }

    void clearSelectedCell()
    {
        m_Table.cancelCellEditing();
        m_Model.setValueAt(null, m_Table.getSelectedRow(), m_Table.getSelectedColumn());
    }

    // TODO : Test coverage
    static Point findCell(SpreadsheetModel model, Integer row, Integer column)
    {
        if(row != null && column != null)
            return new Point(column, row);
        if(row != null && column == null)
        {
            for(int c = 0; c < model.getColumnCount(); ++c)
                if(model.getValueAt(row, c, false) == null)
                    return new Point(c, row);
            return new Point(0, row);
        }
        else if(column != null && row == null)
        {
            for(int r = 0; r < model.getRowCount(); ++r)
                if(model.getValueAt(r, column, false) == null)
                    return new Point(column, r);
            return new Point(column, 0);
        }
        else
        {
            for(int r = 0; r < model.getRowCount(); ++r)
                for(int c = 0; c < model.getColumnCount(); ++c)
                    if(model.getValueAt(r, c, false) == null)
                        return new Point(c, r);
            return new Point(0, 0);
        }
    }

}
