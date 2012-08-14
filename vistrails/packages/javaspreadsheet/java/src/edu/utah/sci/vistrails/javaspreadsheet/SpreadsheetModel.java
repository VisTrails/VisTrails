package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.Point;
import java.util.HashMap;
import java.util.Map;

import javax.swing.table.DefaultTableModel;

import edu.utah.sci.vistrails.javaspreadsheet.Spreadsheet.Mode;


class SpreadsheetModel extends DefaultTableModel implements Cell.Observer {

    private String m_Name;
    private int m_NbRows;
    private int m_NbColumns;
    private SpreadsheetInterface m_Interface;
    private Map<Point, Cell> m_Cells;
    private Map<Cell, Point> m_CellPositions;
    private Mode m_Mode;

    SpreadsheetModel(String name, int rows, int columns, Mode mode, SpreadsheetInterface interf)
    {
        m_Name = name;
        m_NbRows = rows;
        m_NbColumns = columns;
        m_Interface = interf;
        m_Cells = new HashMap<Point, Cell>();
        m_CellPositions = new HashMap<Cell, Point>();
        m_Mode = mode;
    }

    void setMode(Mode mode)
    {
        try {
            if(mode != m_Mode)
            {
                m_Mode = mode;
                for(Cell cell : m_Cells.values())
                    cell.setMode(mode);
            }
        }
        catch(Exception e)
        {
            e.printStackTrace(System.err);
        }
    }

    @Override
    public int getRowCount()
    {
        return m_NbRows;
    }

    @Override
    public int getColumnCount()
    {
        return m_NbColumns;
    }

    @Override
    public Object getValueAt(int row, int column)
    {
        return getValueAt(row, column, false);
    }

    public Object getValueAt(int row, int column, boolean create)
    {
        Point pos = new Point(column, row);
        Cell cell = m_Cells.get(pos);
        if(cell == null && create)
        {
            cell = new Cell(this, m_Interface, m_Mode);
            m_Cells.put(pos, cell);
            m_CellPositions.put(cell, pos);
            fireTableCellUpdated(row, column);
        }
        return cell;
    }

    @Override
    public void setValueAt(Object value, int row, int column)
    {
        Point pos = new Point(column, row);

        {
            Cell old_cell = m_Cells.get(pos);
            if(old_cell != null)
                m_CellPositions.remove(old_cell);
        }

        if(value != null)
        {
            Point old_pos = m_CellPositions.remove(value);
            if(old_pos != null)
            {
                m_Cells.remove(old_pos);
                fireTableCellUpdated(old_pos.y, old_pos.x);
            }

            m_Cells.put(pos, (Cell)value);
            m_CellPositions.put((Cell)value, pos);
        }
        else
            m_Cells.remove(pos);
        fireTableCellUpdated(row, column);
    }

    // TODO : Test coverage
    @Override
    public String getColumnName(int column)
    {
        String name = "";
        column += 1;
        while(column > 0)
        {
            column -= 1;
            name = (char)((column % 26) + 'A') + name;
            column /= 26;
        }
        return name;
    }

    @Override
    public void cellRepainted(Cell cell)
    {
        Point pos = m_CellPositions.get(cell);
        fireTableCellUpdated(pos.y, pos.x);
    }

    boolean swapCells(Point loc1, Point loc2)
    {
        Cell prev1 = m_Cells.get(loc1);
        Cell prev2 = m_Cells.get(loc2);
        setValueAt(prev2, loc1.y, loc1.x);
        setValueAt(prev1, loc2.y, loc2.x);
        return true;
    }

    boolean copyCell(Point src_loc, Point dst_loc)
    {
        Cell cell = m_Cells.get(src_loc);
        if(cell == null)
            return false;
        return m_Interface.executePipelineToCell(cell.getInfos(), m_Name, dst_loc);
    }

    void changeSize(int newrowcount, int newcolumncount)
    {
        m_NbRows = newrowcount;
        m_NbColumns = newcolumncount;
        fireTableStructureChanged();
    }

    Point getCellPosition(Cell cell)
    {
        return m_CellPositions.get(cell);
    }

}
