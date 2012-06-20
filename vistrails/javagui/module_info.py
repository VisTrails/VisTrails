from java.lang import Integer
from javax.swing import Box, BoxLayout, JComponent, JLabel, JPanel, JTextField
from java.awt import Dimension
from com.vlsolutions.swing.docking import DockKey, Dockable


class JModuleInfo(JComponent, Dockable):
    def __init__(self):
        super(JModuleInfo, self).__init__()

        self._key = DockKey('module_info')

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))

        name_line = JPanel()
        name_line.setLayout(BoxLayout(name_line, BoxLayout.LINE_AXIS))
        name_line.add(JLabel("Name:"))
        self._name_input = JTextField()
        self._name_input.setMaximumSize(Dimension(
                Integer.MAX_VALUE,
                self._name_input.getPreferredSize().height))
        #self._name_input.add***Listener(self)
        name_line.add(self._name_input)
        self.add(name_line)

        type_line = JPanel()
        type_line.setLayout(BoxLayout(type_line, BoxLayout.LINE_AXIS))
        type_line.add(JLabel("Type: "))
        self._type_label = JLabel()
        type_line.add(self._type_label)
        type_line.add(Box.createHorizontalGlue())
        self.add(type_line)

        pkg_line = JPanel()
        pkg_line.setLayout(BoxLayout(pkg_line, BoxLayout.LINE_AXIS))
        pkg_line.add(JLabel("Package: "))
        self._pkg_label = JLabel()
        pkg_line.add(self._pkg_label)
        pkg_line.add(Box.createHorizontalGlue())
        self.add(pkg_line)

        self.add(Box.createVerticalGlue())

    def update_module(self, module=None):
        # TODO : update self._type_label, self._pkg_label and self._name_input
        pass

    # @Override
    def getDockKey(self):
        return self._key

    # @Override
    def getComponent(self, *args):
        if len(args) == 0:
            return self
        else:
            return JComponent.getComponent(self, *args)
