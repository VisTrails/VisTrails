package edu.utah.sci.vistrails.javaspreadsheet;


public class CellLocation {

    private Integer m_Row;
    private Integer m_Column;

    public CellLocation(Integer row, Integer column)
    {
        m_Row = row;
        m_Column = column;
    }

    public Integer getRow()
    {
        return m_Row;
    }

    public Integer getColumn()
    {
        return m_Column;
    }

}
