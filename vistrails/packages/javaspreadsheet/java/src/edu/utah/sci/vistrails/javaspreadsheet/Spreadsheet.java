package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.HashMap;
import java.util.Map;

import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JPanel;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.JTabbedPane;
import javax.swing.JToolBar;


/**
 * The spreadsheet window, that contains several sheets.
 */
public class Spreadsheet extends JFrame {

    private SpreadsheetInterface m_Interface;
    private JTabbedPane m_TabbedPane;
    private Map<String, Sheet> m_Sheets;

    enum Mode {
        INTERACTIVE, EDITING
    }

    private class ModeChanger implements ActionListener {

        private Mode m_Mode;

        ModeChanger(Mode mode)
        {
            m_Mode = mode;
        }

        @Override
        public void actionPerformed(ActionEvent e)
        {
            for(Sheet sheet : m_Sheets.values())
                sheet.setMode(m_Mode);
        }
    }

    private Mode m_Mode;

    public Spreadsheet(SpreadsheetInterface interf)
    {
        super("Java Spreadsheet Window");

        m_Interface = interf;

        m_Mode = Mode.INTERACTIVE;

        m_TabbedPane = new JTabbedPane(JTabbedPane.BOTTOM);
        JPanel panel = new JPanel();
        panel.setLayout(new BorderLayout());
        setContentPane(panel);
        panel.add(m_TabbedPane, BorderLayout.CENTER);
        m_Sheets = new HashMap<String, Sheet>();
        addTab("sheet1", new Sheet("sheet1", m_Mode, m_Interface));

        JMenuBar menuBar = new JMenuBar();
        JMenu viewMenu = new JMenu("View");
        JRadioButtonMenuItem interactiveMode = new JRadioButtonMenuItem("Interactive Mode", true);
        interactiveMode.addActionListener(new ModeChanger(Mode.INTERACTIVE));
        viewMenu.add(interactiveMode);
        JRadioButtonMenuItem editingMode = new JRadioButtonMenuItem("Editing Mode");
        editingMode.addActionListener(new ModeChanger(Mode.EDITING));
        viewMenu.add(editingMode);
        ButtonGroup group = new ButtonGroup();
        group.add(interactiveMode);
        group.add(editingMode);
        menuBar.add(viewMenu);
        setJMenuBar(menuBar);

        JToolBar toolBar = new JToolBar();
        JButton clearButton = new JButton("Clear cell");
        clearButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e)
            {
                ((Sheet)m_TabbedPane.getSelectedComponent()).clearSelectedCell();
            }
        });
        toolBar.add(clearButton);
        panel.add(toolBar, BorderLayout.NORTH);

        pack();
    }

    private void addTab(String name, Sheet tab)
    {
        m_Sheets.put(name, tab);
        m_TabbedPane.addTab(name, tab);
    }

    public Sheet getSheet()
    {
        return getSheet(null);
    }

    public Sheet getSheet(SheetReference sheetref)
    {
        if(sheetref != null && sheetref.getName() != null)
        {
            Sheet sheet = m_Sheets.get(sheetref.getName());
            if(sheet == null)
            {
                sheet = new Sheet(sheetref.getName(), m_Mode, m_Interface);
                addTab(sheetref.getName(), sheet);
            }
            return sheet;
        }
        else
        {
            Sheet sheet = (Sheet)m_TabbedPane.getSelectedComponent();
            if(sheet == null)
            {
                sheet = new Sheet("sheet1", m_Mode, m_Interface);
                addTab("sheet1", sheet);
            }
            return sheet;
        }
    }

}
