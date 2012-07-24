"""The ports pane, displaying the ports of a specific module instance.

It is a component of the module info panel.
"""

from itertools import izip

from java.awt import Color, Dimension, Font
from java.awt.event import MouseAdapter
from javax.swing import BoxLayout, JLabel, JPanel, JTabbedPane, Box, JButton,\
    SwingUtilities

from core import debug
from javagui.modules import get_widget_class
from javagui.utils import resized_icon


ICON_SIZE = Dimension(20, 20)


CONNECTED = resized_icon('gui/resources/images/connection.png', ICON_SIZE)
VIS_ON = resized_icon('gui/resources/images/eye.png', ICON_SIZE)
VIS_LOCKED = resized_icon('gui/resources/images/eye_gray.png', ICON_SIZE)


class ClickListener(MouseAdapter):
    def __init__(self, action):
        super(ClickListener, self).__init__()
        self._action = action

    # @Override
    def mouseClicked(self, event):
        if SwingUtilities.isLeftMouseButton(event):
            self._action()


class MissingWidget(JLabel):
    """A missing widget, i.e. that we couldn't get from the module.
    """
    def __init__(self, value):
        JLabel.__init__(self, "(missing widget)")
        self.setOpaque(True)
        self.setBackground(Color(255, 91, 91))
        self.setFont(Font('Dialog', Font.BOLD, 14))

        self.value = value

    def contents(self):
        return self.value


class InputPortValue(JPanel):
    def __init__(self, port_spec, controller, module, function=None):
        self._port_spec = port_spec
        self._controller = controller
        self._module = module
        self._function = function

        self.setLayout(BoxLayout(self, BoxLayout.LINE_AXIS))
        self.add(JButton("-"))
        # TODO : '+' button
        # TODO : border

        box = JPanel()
        box.setLayout(BoxLayout(box, BoxLayout.PAGE_AXIS))
        self.add(box)

        self._widgets = []
        if function is not None:
            params = function.parameters
        else:
            params = [None] * len(port_spec.descriptors())
        for desc, param in izip(port_spec.descriptors(), params):
            line = JPanel()
            line.setLayout(BoxLayout(line, BoxLayout.LINE_AXIS))
            box.add(line)
            # TODO : Aliases
            label = JLabel(desc.name)
            line.add(label)
            try:
                widget_class = get_widget_class(desc.module)
                widget = widget_class(self, param)
            except:
                widget = MissingWidget(param.strValue)
            self._widgets.append(widget)
            line.add(widget)

    def value_changed(self, new_value):
        str_values = [str(w.contents()) for w in self._widgets]
        if self._function:
            real_id = self._function.real_id
            should_replace = True
        else:
            real_id = -1
            should_replace = False
        self._controller.update_function(
                self._module,
                self._port_spec.name,
                str_values,
                real_id,
                [''] * len(self._widgets), # Aliases
                [], # Query methods
                should_replace)


class Port(JPanel):
    def __init__(self, portname, input_ports, module, ports_pane):
        self._port_name = portname
        self._input_ports = input_ports
        self._module = module
        self._ports_pane = ports_pane

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))

        first_line = JPanel()
        first_line.setLayout(BoxLayout(first_line, BoxLayout.LINE_AXIS))

        self._visibility_icon = JLabel()
        self._visibility_icon.setMinimumSize(ICON_SIZE)
        self._visibility_icon.setMaximumSize(ICON_SIZE)
        self._visibility_icon.setPreferredSize(ICON_SIZE)
        self._visibility_icon.addMouseListener(
                ClickListener(self._toggle_visibility))
        first_line.add(self._visibility_icon)

        self._connection_icon = JLabel()
        self._connection_icon.setMinimumSize(ICON_SIZE)
        self._connection_icon.setMaximumSize(ICON_SIZE)
        self._connection_icon.setPreferredSize(ICON_SIZE)
        first_line.add(self._connection_icon)

        name = JLabel(portname)
        name.setEnabled(input_ports)
        first_line.add(name)

        first_line.add(Box.createHorizontalGlue())
        self.add(first_line)

    def add_value(self, value_widget):
        self.add(value_widget)

    def _get_visibility(self):
        return self._visible
    def _set_visibility(self, visibility):
        self._visible = visibility
        if visibility == 'on':
            self._visibility_icon.setIcon(VIS_ON)
        elif visibility == 'off':
            self._visibility_icon.setIcon(None)
        elif visibility == 'locked':
            self._visibility_icon.setIcon(VIS_LOCKED)
    port_visible = property(_get_visibility, _set_visibility)

    def _toggle_visibility(self):
        if self._input_ports:
            visible_ports = self._module.visible_input_ports
        else:
            visible_ports = self._module.visible_output_ports

        if self._visible == 'off':
            self.port_visible = 'on'
            visible_ports.add(self._port_name)
        elif self._visible == 'on' and not self._connected:
            self.port_visible = 'off'
            visible_ports.discard(self._port_name)
        else:
            return

        self.repaint()
        self._ports_pane.ports_changed(self._module)

    def _get_connected(self):
        return self._connected

    def _set_connected(self, connect):
        self._connected = connect
        if connect:
            self._connection_icon.setIcon(CONNECTED)
        else:
            self._connection_icon.setIcon(None)

    port_connected = property(_get_connected, _set_connected)


class PortsList(JPanel):
    def __init__(self, input_ports):
        self._input_ports = input_ports

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))

    def clear(self):
        self.removeAll()

    def add_port(self, item):
        self.add(item)


class JPortsPane(JTabbedPane):
    def __init__(self):
        super(JPortsPane, self).__init__()
        self.controller = None

        self._input_ports = PortsList(True)
        self.addTab("Input ports", self._input_ports)

        self._output_ports = PortsList(False)
        self.addTab("Output ports", self._output_ports)

        self._ports = dict()

    def update_module(self, module=None):
        self._input_ports.clear()
        self._output_ports.clear()

        if module:
            self._extract_ports(module, self._input_ports, True)
            self._extract_ports(module, self._output_ports, False)

        self._input_ports.repaint()
        self._input_ports.revalidate()
        self._output_ports.repaint()
        self._output_ports.revalidate()

    def _extract_ports(self, module, ports_list, input_ports):
        if input_ports:
            port_specs = module.destinationPorts()
            connected_ports = module.connected_input_ports
            visible_ports = module.visible_input_ports
        else:
            port_specs = module.sourcePorts()
            connected_ports = module.connected_output_ports
            visible_ports = module.visible_output_ports

        self._ports[input_ports] = dict()

        for port_spec in sorted(port_specs, key=lambda p: p.name):
            item = Port(port_spec.name, input_ports, module, self)

            # Connected status
            item.port_connected = (
                    port_spec.name in connected_ports and
                    connected_ports[port_spec.name] > 0)

            # Visibility
            if not port_spec.optional:
                item.port_visible = 'locked'
            elif port_spec.name in visible_ports:
                item.port_visible = 'on'
            else:
                item.port_visible = 'off'

            ports_list.add_port(item)
            self._ports[input_ports][port_spec.name] = port_spec, item

        if input_ports:
            for function in module.functions:
                if not function.is_valid:
                    debug.critical("function '%s' not valid" % function.name)
                    continue
                port_spec, item = self._ports[input_ports][function.name]
                subitem = InputPortValue(port_spec, self.controller,
                                         module, function)
                item.add_value(subitem)

    def ports_changed(self, module):
        self.controller.current_pipeline_view.ports_changed(module.id)
