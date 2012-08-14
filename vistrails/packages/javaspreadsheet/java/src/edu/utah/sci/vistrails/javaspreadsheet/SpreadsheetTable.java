package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.AlphaComposite;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.io.IOException;

import javax.swing.AbstractCellEditor;
import javax.swing.DropMode;
import javax.swing.JPanel;
import javax.swing.JTable;
import javax.swing.TransferHandler;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableCellRenderer;


class SpreadsheetTable extends JTable {

    private static class TranslucentCellOverlay extends JPanel {

        static final Color OVERLAY_COLOR = new Color(113, 159, 203);

        public TranslucentCellOverlay(Component component, Dimension size)
        {
            super(new BorderLayout());
            if(component != null)
                add(component);
            setSize(size);
        }

        @Override
        public void paint(Graphics g)
        {
            super.paint(g);
            Graphics2D g2 = (Graphics2D)g.create();
            g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.5f));
            g2.setColor(OVERLAY_COLOR);
            g2.fillRect(0, 0, getWidth(), getHeight());
            g2.dispose();
        }
    }

    private class Renderer extends DefaultTableCellRenderer {

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
        {
            Dimension new_size = getCellSize(row, column);
            if(value instanceof Cell)
            {
                Cell cell = (Cell)value;
                if(!cell.getSize().equals(new_size))
                    cell.setSize(new_size);
                cell.setSelected(false);
            }

            DropLocation drop_location = getDropLocation();
            if(drop_location != null && !drop_location.isInsertRow() && !drop_location.isInsertColumn() && (drop_location.getRow() == row) && (drop_location.getColumn() == column))
                return new TranslucentCellOverlay((Component)value, new_size);
            return (Component)value;
        }
    }

    private class Editor extends AbstractCellEditor implements TableCellEditor {

        private Cell m_Cell = null;

        @Override
        public Object getCellEditorValue()
        {
            return m_Cell;
        }

        @Override
        public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column)
        {
            if(value instanceof Cell)
            {
                Cell cell = (Cell)value;
                Dimension new_size = getCellSize(row, column);
                if(!cell.getSize().equals(new_size))
                    cell.setSize(new_size);
                cell.setSelected(true);
                m_Cell = cell;
                return m_Cell;
            }
            return null;
        }
    }

    private class TableTransferHandler extends TransferHandler {

        @Override
        public boolean canImport(TransferSupport support)
        {
            if(!support.isDrop())
                return false;
            else if(!support.isDataFlavorSupported(CellManipulator.MANIPULATOR_DATA))
                return false;
            return true;
        }

        @Override
        public boolean importData(TransferSupport support)
        {
            if(!canImport(support))
                return false;

            try
            {
                CellManipulator.Command data = (CellManipulator.Command)support.getTransferable().getTransferData(CellManipulator.MANIPULATOR_DATA);

                JTable.DropLocation target = (JTable.DropLocation)support.getDropLocation();
                Point target_loc = new Point(target.getColumn(), target.getRow());
                manipulatorAction(data.getCommand(), data.getSource(), target_loc);

                return true;
            } catch(UnsupportedFlavorException e)
            {
                return false;
            } catch(IOException e)
            {
                return false;
            }
        }
    }

    private Renderer m_Renderer;
    private Editor m_Editor;

    SpreadsheetTable(SpreadsheetModel model)
    {
        super(model);
        m_Renderer = new Renderer();
        m_Editor = new Editor();
        setRowHeight(100);
        getTableHeader().setReorderingAllowed(false);
        setDropMode(DropMode.USE_SELECTION);
        setTransferHandler(new TableTransferHandler());
    }

    @Override
    public TableCellRenderer getDefaultRenderer(Class<?> columnClass)
    {
        return m_Renderer;
    }

    @Override
    public TableCellEditor getDefaultEditor(Class<?> columnClass)
    {
        return m_Editor;
    }

    private Dimension getCellSize(int row, int column)
    {
        return new Dimension(getColumnModel().getColumn(column).getWidth(), getRowHeight(row));
    }

    void manipulatorAction(String command, Cell source, Point target_loc)
    {
        if(command.equals("copy"))
        {
            m_Editor.cancelCellEditing();
            SpreadsheetModel model = (SpreadsheetModel)getModel();
            model.copyCell(model.getCellPosition(source), target_loc);
        }
        else if(command.equals("move"))
        {
            m_Editor.cancelCellEditing();
            SpreadsheetModel model = (SpreadsheetModel)getModel();
            model.swapCells(model.getCellPosition(source), target_loc);
        }
    }

    void cancelCellEditing()
    {
        m_Editor.cancelCellEditing();
    }

}
