package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;

import edu.utah.sci.vistrails.javaspreadsheet.Spreadsheet.Mode;


public class Cell extends JPanel {

    private static final Color SELECTION_COLOR = new Color(51, 153, 255);

    private static final Dimension ICON_SIZE = new Dimension(64, 64);

    private static final Icon COPY = new ImageIcon("packages/javaspreadsheet/images/copy.png");
    private static final Icon MOVE = new ImageIcon("packages/javaspreadsheet/images/move.png");
    private static final Icon LOCATE_VERSION = new ImageIcon("packages/javaspreadsheet/images/locate.png");

    interface Observer {

        void cellRepainted(Cell cell);

    }

    private Observer m_Observer;
    private SpreadsheetInterface m_Interface;
    private CellInfos m_Infos;
    private JComponent m_Widget;
    private Mode m_Mode;

    private int m_LabelHeight;

    Cell(Observer observer, SpreadsheetInterface interf)
    {
        this(observer, interf, Spreadsheet.Mode.INTERACTIVE);
    }

    Cell(Observer observer, SpreadsheetInterface interf, Mode mode)
    {
        m_Observer = observer;
        m_Interface = interf;
        setLayout(null); // Manual layout management in layout()
        m_Infos = null;
        m_Widget = null;
        setSelected(false);
        m_Mode = mode;
        setup();
    }

    void setSelected(boolean selected)
    {
        setBackground(selected ? SELECTION_COLOR : null);
    }

    void setMode(Mode mode)
    {
        if(mode != m_Mode)
        {
            m_Mode = mode;
            setup();
        }
    }

    private void addLabel(String title, String text)
    {
        JLabel label = new JLabel(String.format("%s: %s", title, text));
        label.setOpaque(true);
        label.setBackground(new Color(230, 240, 230));
        add(label);
        int h = (int)label.getPreferredSize().getHeight();
        label.setBounds(0, m_LabelHeight, Integer.MAX_VALUE, h);
        m_LabelHeight += h;
    }

    private void setup()
    {
        removeAll();

        if(m_Mode == Spreadsheet.Mode.EDITING)
        {
            m_LabelHeight = 0;

            if(m_Infos != null)
            {
                addLabel("Vistrail", m_Infos.getVistrail());
                addLabel("Index", String.format("Pipeline: %d, Module: %d", m_Infos.getVersion(), m_Infos.getModule()));
                addLabel("Created by", m_Infos.getReason());
            }

            add(new CellManipulator(COPY, this, "copy"));
            add(new CellManipulator(MOVE, this, "move"));

            JButton locate_version = new JButton(LOCATE_VERSION);
            locate_version.addActionListener(new ActionListener() {

                @Override
                public void actionPerformed(ActionEvent e)
                {
                    m_Interface.select_version(m_Infos);
                }
            });
            add(locate_version);
        }

        if(m_Widget != null)
            add(m_Widget);
    }

    @Override
    public void layout()
    {
        int nb_manips = 0;
        for(int i = 0; i < getComponentCount(); ++i)
        {
            Component component = getComponent(i);
            if(component == m_Widget)
                component.setBounds(2, 2, getWidth() - 4, getHeight() - 4);
            else if(component instanceof CellManipulator || component instanceof JButton)
            {
                component.setBounds(nb_manips * ICON_SIZE.width + 20, m_LabelHeight + 20, ICON_SIZE.width, ICON_SIZE.height);
                nb_manips++;
            }
        }
    }

    public void setWidget(JComponent widget)
    {
        if(m_Widget != null)
            remove(m_Widget);
        m_Widget = widget;
        add(widget);
        layout();
    }

    public void assign(CellInfos infos)
    {
        m_Widget = null;
        m_Infos = infos;
        setup();
    }

    @Override
    public void paint(Graphics g)
    {
        super.paint(g);
        m_Observer.cellRepainted(this);
    }

    @Override
    public void setSize(Dimension size)
    {
        super.setSize(size);
        layout();
    }

    @Override
    public void setSize(int width, int height)
    {
        super.setSize(width, height);
        layout();
    }

    public CellInfos getInfos()
    {
        return m_Infos;
    }

}
