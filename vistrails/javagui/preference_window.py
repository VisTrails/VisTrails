from java.awt import Component, Dialog, Dimension
from java.awt.event import ActionListener

from javax.swing import Box, BoxLayout, DefaultListModel, JButton, JDialog
from javax.swing import JLabel, JList, JPanel, JScrollPane, JTextArea
from javax.swing import ListSelectionModel, ScrollPaneConstants, SpringLayout
from javax.swing.event import ListSelectionListener

from java.lang import Integer, RuntimeException

import springutilities
from core.packagemanager import get_package_manager
from core import debug


class SortedListModel(DefaultListModel):
    def findInsertionPoint(self, element):
        # Rewrite of Collections#indexedBinarySearch()
        low = 0;
        high = self.getSize() - 1

        while low <= high:
            mid = (low + high)/2
            midVal = self.getElementAt(mid)

            # We use Python's operators here, that may be overloaded
            if midVal < element:
                low = mid + 1
            elif element < midVal:
                high = mid - 1
            else:
                return mid # key found
        return low # key not found

    # @Override
    def addElement(self, element):
        # Sorted insert
        DefaultListModel.insertElementAt(self, element,
                                         self.findInsertionPoint(element))

    # @Override
    def set(self, index, element):
        # Might not behave as expected
        prev = DefaultListModel.remove(self, index)
        DefaultListModel.addElement(self, element)
        return prev

    # @Override
    def setElementAt(self, element, index):
        # Might not behave as expected
        DefaultListModel.remove(self, index)
        DefaultListModel.addElement(self, element)

    # @Override
    def add(self, index, element):
        # Should not be called on this implementation
        raise RuntimeException("SortedListModel#add(int, Object)")

    # @Override
    def insertElementAt(self, element, index):
        # Should not be called on this implementation
        raise RuntimeException("SortedListModel#insertElementAt(Object, int)")


class MyListSelectionListener(ListSelectionListener):
    def __init__(self, parent, which_list):
        self.parent = parent
        self.which_list = which_list

    # @Override
    def valueChanged(self, e):
        self.parent.selected(self.which_list, e.getFirstIndex())


class PreferenceWindow(JDialog, ActionListener):
    def __init__(self, frame):
        JDialog.__init__(self, frame, "Preferences",
                         Dialog.ModalityType.DOCUMENT_MODAL)

        top = JPanel()
        top.setLayout(BoxLayout(top, BoxLayout.LINE_AXIS))
        self.setContentPane(top)

        left = JPanel()
        left.setLayout(BoxLayout(left, BoxLayout.PAGE_AXIS))
        left.setMaximumSize(Dimension(200, Integer.MAX_VALUE))
        top.add(left)

        left.add(JLabel("Disabled packages:"))
        self.disabled_model = SortedListModel()
        self.list_disabled = JList(self.disabled_model)
        self.list_disabled.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        self.list_disabled.addListSelectionListener(
                MyListSelectionListener(self, False))
        pane = JScrollPane(self.list_disabled)
        pane.setVerticalScrollBarPolicy(
                ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS)
        left.add(pane)

        left.add(JLabel("Enabled packages:"))
        self.enabled_model = SortedListModel()
        self.list_enabled = JList(self.enabled_model)
        self.list_enabled.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        self.list_enabled.addListSelectionListener(
                MyListSelectionListener(self, True))
        pane = JScrollPane(self.list_enabled)
        pane.setVerticalScrollBarPolicy(
                ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS)
        left.add(pane)

        right = JPanel()
        right.setLayout(BoxLayout(right, BoxLayout.PAGE_AXIS))
        top.add(right)

        infos = JPanel()
        infos.setLayout(SpringLayout())
        right.add(infos)

        infos.add(JLabel("Package name:"))
        self.package_full_name = JLabel()
        infos.add(self.package_full_name)
        infos.add(JLabel("Identifier:"))
        self.package_id = JLabel()
        infos.add(self.package_id)
        infos.add(JLabel("Version:"))
        self.package_version = JLabel()
        infos.add(self.package_version);
        infos.add(JLabel("Dependencies:"))
        self.package_deps = JLabel()
        infos.add(self.package_deps);
        infos.add(JLabel("Reverse dependencies:"))
        self.package_rev_deps = JLabel()
        infos.add(self.package_rev_deps);
        infos.add(JLabel("Description:"))
        self.package_desc = JTextArea()
        self.package_desc.setLineWrap(True)
        desc_sp = JScrollPane(self.package_desc)
        desc_sp.setHorizontalScrollBarPolicy(
                ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
        desc_sp.setVerticalScrollBarPolicy(
                ScrollPaneConstants.VERTICAL_SCROLLBAR_NEVER)
        infos.add(desc_sp);
        springutilities.makeCompactGrid(infos, 0, 2, 6, 6, 6, 6);

        buttons = JPanel()
        buttons.setLayout(BoxLayout(buttons, BoxLayout.LINE_AXIS))
        right.add(buttons)

        strs = ["Enable", 'en',
                "Disable", 'dis',
                "Configure...", 'conf',
                "Reload", 'rel']
        btns = []
        buttons.add(Box.createHorizontalGlue())
        for i in xrange(0, len(strs), 2):
            b = JButton(strs[i])
            b.setEnabled(False)
            b.setActionCommand(strs[i+1])
            b.addActionListener(self)
            buttons.add(b)
            btns.append(b)
            buttons.add(Box.createHorizontalStrut(10))
        self.button_enable = btns[0]
        self.button_disable = btns[1]
        self.button_configure = btns[2]
        self.button_reload = btns[3]

        # Stub packages
        self.disabled_model.addElement("javaspreadsheet")
        self.disabled_model.addElement("obvioustest")
        self.enabled_model.addElement("vtk")

        self.populate_lists()

        self.pack()
        self.setMinimumSize(self.getSize())

    def populate_lists(self):
        """(Re)constructs the enabled and disable packages lists.

        Reads the list of enabled and available packages from the package
        manager to populate the JList's
        """
        pm = get_package_manager()
        enabled_pkgs = set(pm.enabled_package_list())

        self.enabled_model.clear()
        for pkg in enabled_pkgs:
            self.enabled_model.addElement(pkg.codepath)

        self.disabled_model.clear()
        for pkg in pm.available_package_names_list():
            if pkg not in enabled_pkgs:
                self.disabled_model.addElement(pkg)

    # @Override
    def actionPerformed(self, e):
        if e.getActionCommand() == 'en':
            pass
        elif e.getActionCommand() == 'dis':
            pass
        elif e.getActionCommand() == 'conf':
            pass
        elif e.getActionCommand() == 'rel':
            pass

    def selected(self, enabled_list, index):
        pm = get_package_manager()

        if enabled_list:
            self.list_disabled.clearSelection()
            self.button_enable.setEnabled(False)
            self.button_disable.setEnabled(True)

            codepath = self.list_enabled.getSelectedValue()
            self.update_infos(pm.get_package_by_codepath(codepath))
        else:
            self.list_enabled.clearSelection()
            self.button_disable.setEnabled(False)
            self.button_enable.setEnabled(True)

            codepath = self.list_disabled.getSelectedValue()
            self.update_infos(pm.look_at_available_package(codepath))

    def update_infos(self, pkg):
        """Update the labels to show the details of the selected package.
        """
        try:
            pkg.load()
        except Exception, e:
            msg = '<html>ERROR: Could not load package.</html>'
            self.package_full_name.setText(msg)
            self.package_id.setText(msg)
            self.package_version.setText(msg)
            self.package_deps.setText(msg)
            self.package_rev_deps.setText(msg)
            self.package_desc.setText(msg)
            debug.critical('Cannot load package', str(e))
        else:
            self.package_full_name.setText(pkg.name)
            deps = ', '.join(str(d) for d in pkg.dependencies()) or \
                'No package dependencies.'
            deps = '<html>' + deps + '</html>'
            try:
                pm = get_package_manager()
                reverse_deps = \
                    (', '.join(pm.reverse_dependencies(pkg.identifier)) or
                     'No reverse dependencies.')
                reverse_deps = '<html>' + reverse_deps + '</html>'
            except KeyError:
                reverse_deps = ("Reverse dependencies only " +
                                "available for enabled packages.")
            self.package_id.setText(pkg.identifier)
            self.package_version.setText(pkg.version)
            self.package_deps.setText(deps)
            self.package_rev_deps.setText(reverse_deps)
            self.package_desc.setText(pkg.description)
