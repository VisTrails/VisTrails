package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.Transferable;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.IOException;

import javax.swing.Icon;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.TransferHandler;


public class CellManipulator extends JLabel implements MouseListener {

    static class Command {

        private String m_Command;
        private Cell m_Cell;

        public Command(String command, Cell cell)
        {
            m_Command = command;
            m_Cell = cell;
        }

        public String getCommand()
        {
            return m_Command;
        }

        public Cell getSource()
        {
            return m_Cell;
        }

    }

    static final DataFlavor MANIPULATOR_DATA = new DataFlavor(
            Command.class,
            "X-Vistrails-Spreadsheet-Manipulator; class=<edu.utah.sci.vistrails.javaspreadsheet.CellManipulator.Command>");

    private class CellManipulatorTransferable implements Transferable {

        @Override
        public Object getTransferData(DataFlavor flavor) throws UnsupportedFlavorException, IOException
        {
            if(flavor.equals(MANIPULATOR_DATA))
                return new Command(m_Command, m_Cell);
            else
                return null;
        }

        @Override
        public DataFlavor[] getTransferDataFlavors()
        {
            return new DataFlavor[] {MANIPULATOR_DATA};
        }

        @Override
        public boolean isDataFlavorSupported(DataFlavor flavor)
        {
            return flavor.equals(MANIPULATOR_DATA);
        }

    }

    private class CellManipulatorTransferHandler extends TransferHandler {

        @Override
        public int getSourceActions(JComponent c)
        {
            return TransferHandler.COPY;
        }

        @Override
        protected Transferable createTransferable(JComponent c)
        {
            return new CellManipulatorTransferable();
        }

    }

    private Cell m_Cell;
    private String m_Command;

    CellManipulator(Icon icon, Cell cell, String command)
    {
        super(icon);
        m_Cell = cell;
        m_Command = command;

        setTransferHandler(new CellManipulatorTransferHandler());
        addMouseListener(this);
    }

    @Override
    public void mousePressed(MouseEvent event)
    {
        getTransferHandler().exportAsDrag(this, event, TransferHandler.COPY);
    }

    @Override
    public void mouseClicked(MouseEvent event) {}
    @Override
    public void mouseReleased(MouseEvent event) {}
    @Override
    public void mouseEntered(MouseEvent event) {}
    @Override
    public void mouseExited(MouseEvent event) {}

}
