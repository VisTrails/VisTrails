from javax.swing import BoxLayout, JLabel, JPanel, JTabbedPane, Box
from java.awt import Dimension

from utils import resized_icon


ICON_SIZE = Dimension(20, 20)


CONNECTED = resized_icon('gui/resources/images/connection.png', ICON_SIZE)
VIS_ON = resized_icon('gui/resources/images/eye.png', ICON_SIZE)
VIS_LOCKED = resized_icon('gui/resources/images/eye_gray.png', ICON_SIZE)


class Port(JPanel):
    def __init__(self, portname, input_ports):
        self.input_ports = input_ports

        self.setLayout(BoxLayout(self, BoxLayout.LINE_AXIS))

        self._visibility_icon = JLabel()
        self._visibility_icon.setMinimumSize(ICON_SIZE)
        self._visibility_icon.setMaximumSize(ICON_SIZE)
        self._visibility_icon.setPreferredSize(ICON_SIZE)
        self.add(self._visibility_icon)

        self._connection_icon = JLabel()
        self._connection_icon.setMinimumSize(ICON_SIZE)
        self._connection_icon.setMaximumSize(ICON_SIZE)
        self._connection_icon.setPreferredSize(ICON_SIZE)
        self.add(self._connection_icon)

        name = JLabel(portname)
        name.setEnabled(input_ports)
        self.add(name)

        self.add(Box.createHorizontalGlue())

    def _get_visibility(self):
        return self._visibile

    def _set_visibility(self, visibility):
        self._visible = visibility
        if visibility == 'on':
            self._visibility_icon.setIcon(VIS_ON)
        elif visibility == 'off':
            self._visibility_icon.setIcon(None)
        elif visibility == 'locked':
            self._visibility_icon.setIcon(VIS_LOCKED)

    port_visible = property(_get_visibility, _set_visibility)

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

    def update_module(self, module=None):
        self._input_ports.clear()
        self._output_ports.clear()

        if module:
            self._extract_ports(module, self._input_ports, True)
            self._extract_ports(module, self._output_ports, False)

    def _extract_ports(self, module, ports_list, input_ports):
        if input_ports:
            port_specs = module.destinationPorts()
            connected_ports = module.connected_input_ports
            visible_ports = module.visible_input_ports
        else:
            port_specs = module.sourcePorts()
            connected_ports = module.connected_output_ports
            visible_ports = module.visible_output_ports

        for port_spec in sorted(port_specs, key=lambda p: p.name):
            item = Port(port_spec.name, input_ports)

            item.port_connected = (
                    port_spec.name in connected_ports and
                    connected_ports[port_spec.name] > 0)

            if not port_spec.optional:
                item.port_visible = 'locked'
            elif port_spec.name in visible_ports:
                item.port_visible = 'on'
            else:
                item.port_visible = 'off'

            ports_list.add_port(item)
