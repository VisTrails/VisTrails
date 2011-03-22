############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
""" This contains a customized pipeline view and the dialog/logic for the
Control Flow Assistant.

QReadOnlyPortSelectPipelineView
QControlFlowAssistDialog
"""

from PyQt4 import QtCore, QtGui
from gui.pipeline_view import QGraphicsConfigureItem, QGraphicsModuleItem, QGraphicsPortItem, QPipelineScene, QPipelineView
from gui.theme import CurrentTheme
from gui.utils import show_info

################################################################################

class QReadOnlyPortSelectPipelineView(QPipelineView):
    def __init__(self, parent, scene, single_output=False, include_module_ids=[]):
        """ QReadOnlyPortSelectPipelineView(parent: QPipelineView,
                                            scene: QGraphicsScene,
                                            single_output: bool,
                                            include_module_ids: list)
                                            -> QReadOnlyPortSelectPipelineView
        Create a read only pipeline view that only allows selection of ports from
        the modules in include_module_ids.  If single_output is True, only one
        output port can be selected at a time.
        
        """
        QPipelineView.__init__(self, parent)
        self.single_output = single_output
        self._shown = False
        self._selected_input_ports = []
        self._selected_output_ports = []
        # Create custom scene
        scene_copy = QPipelineScene(self)
        scene_copy.controller = scene.controller
        scene_copy.setupScene(scene.pipeline)
        scene_copy.selectAll()
        if include_module_ids:
            # Remove modules not in the include list and associated connections
            sel_modules, sel_connections = scene_copy.get_selected_item_ids()
            [scene_copy.remove_module(m_id) for m_id in sel_modules if m_id not in include_module_ids]
            [scene_copy.remove_connection(c_id) for c_id in sel_connections if c_id not in scene_copy.get_selected_item_ids()[1]]
        # Hide configure button on modules
        for item in scene_copy.selectedItems():
            if type(item) == QGraphicsModuleItem:
                for c_item in item.childItems():
                    if type(c_item) == QGraphicsConfigureItem:
                        c_item.setVisible(False)
        # Unselect everything and use the newly created scene
        scene_copy.clearSelection()
        scene_copy.updateSceneBoundingRect()
        self.setScene(scene_copy)
    
    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Toggle port selection
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            item = self.scene().itemAt(scenePos)
            if type(item) == QGraphicsPortItem:
                is_input = item.port.type == 'input'
                if self.single_output and not is_input and len(self._selected_output_ports) > 0 and item != self._selected_output_ports[0]:
                    # Deselect current output port if another port selected in single output mode
                    self._selected_output_ports[0].setPen(CurrentTheme.PORT_PEN)
                    del self._selected_output_ports[:]
                if is_input:
                    port_set = self._selected_input_ports
                else:
                    port_set = self._selected_output_ports
                if item in port_set:
                    port_set.remove(item)
                else:
                    port_set.append(item)
                self._clicked_port = item
            else:
                self._clicked_port = None
            event.accept()
        else:
            QPipelineView.mousePressEvent(self, event)
            
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Update port highlighting
        
        """
        if event.button() == QtCore.Qt.LeftButton:
            port = self._clicked_port
            if port is not None:
                if port in self._selected_input_ports or port in self._selected_output_ports:
                    port.setPen(CurrentTheme.PORT_SELECTED_PEN)
                else:
                    port.setPen(CurrentTheme.PORT_PEN)
            event.accept()
        else:
            QPipelineView.mouseReleaseEvent(self, event)
        
    def mouseDoubleClickEvent(self, event):
        """ mouseDoubleClickEvent(event: QMouseEvent) -> None
        Disallow left button double clicks
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            event.accept()
        else:
            QPipelineView.mouseDoubleClickEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Disallow left click and drag
        
        """
        buttons = self.translateButton(event)
        if buttons == QtCore.Qt.LeftButton:
            event.accept()
        else:
            QPipelineView.mouseMoveEvent(self, event)
            
    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Disallow key presses
        
        """
        event.accept()
        
    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Fit pipeline to view on first paint
        
        """
        if not self._shown:
            self._shown = True
            self.scene().fitToView(self)
        QPipelineView.paintEvent(self, event)
        
    def sizeHint(self):
        """ sizeHint() -> QSize
        Set smaller pipeline view size

        """
        return QtCore.QSize(512, 512)
    
    def getSelectedInputPorts(self):
        """ getSelectedInputPorts() -> list
        Get list of selected input port (QGraphicsPortItem) objects
        
        """
        return self._selected_input_ports
    
    def getSelectedOutputPorts(self):
        """ getSelectedOutputPorts() -> list
        Get list of selected output port (QGraphicsPortItem) objects
        
        """
        return self._selected_output_ports


class QControlFlowAssistDialog(QtGui.QDialog):
    def __init__(self, parent, selected_module_ids, selected_connection_ids, scene):
        """ QControlFlowAssistDialog(selected_module_ids: list,
                                     selected_connection_ids: list,
                                     scene: QGraphicsScene)
                                     -> None
        Creates the control flow assistant dialog
        
        """
        QtGui.QDialog.__init__(self, parent)
        self.module_ids = selected_module_ids
        self.connection_ids = selected_connection_ids
        
        self.setWindowTitle('Control Flow Assistant')
        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)
        
        # Add instruction label
        self.instructionLabel = QtGui.QLabel('Select one or more Input Ports to receive Lists, and one Output Port to produce a List')
        layout.addWidget(self.instructionLabel)
        
        # Add pipeline view
        self.pipelineView = QReadOnlyPortSelectPipelineView(self, scene, True, selected_module_ids)
        self.controller = self.pipelineView.scene().controller
        layout.addWidget(self.pipelineView)
        
        # Add ok/cancel buttons
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'), self.okClicked)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'), self.close)
    
    def getInputPortsInfo(self):
        """ getInputPortsInfo() -> list
        Gets a list of tuples from the selected input port (QGraphicsPortItem) objects
        containing: (module, portspec, incoming_connections, halfwidth)
        
        """
        return [(gport.parentItem().module, gport.port, gport.controller.get_connections_to(gport.controller.current_pipeline, [gport.parentItem().module.id], gport.port.name), (gport.parentItem().boundingRect().right()-gport.parentItem().boundingRect().left())/2) for gport in self.pipelineView.getSelectedInputPorts()]
    
    def getOutputPortsInfo(self):
        """ getOutputPortsInfo() -> list
        Gets a list of tuples from the selected output port (QGraphicsPortItem) objects
        containing: (module, portspec, outgoing_connections, halfwidth)
        
        """
        return [(gport.parentItem().module, gport.port, gport.controller.get_connections_from(gport.controller.current_pipeline, [gport.parentItem().module.id], gport.port.name), (gport.parentItem().boundingRect().right()-gport.parentItem().boundingRect().left())/2) for gport in self.pipelineView.getSelectedOutputPorts()]

    def okClicked(self):
        """ okClicked() -> None
        Verify selected ports and initiate control flow creation
        
        """
        # Verify that at least one input and one output have been chosen
        input_ports_info = self.getInputPortsInfo()
        output_ports_info = self.getOutputPortsInfo()
        if len(input_ports_info) == 0:
            show_info('No Input Ports Selected', 'No Input Ports have been selected.  You must select at least one to proceed.')
        elif len(output_ports_info) == 0:
            show_info('No Output Port Selected', 'No Output Port has been selected.  You must select one to proceed.')
        else:
            self.createControlFlow(input_ports_info, output_ports_info)
            self.close()
        
    def createControlFlow(self, input_ports_info, output_ports_info):
        """ createControlFlow(input_ports_info: list,
                              output_ports_info: list)
                              -> None
        Create a control flow from input and output port information.
        input_ports_info is a list of tuples containing: (module, portspec, incoming_connections, halfwidth)
        input_ports_info is a list of tuples containing: (module, portspec, outgoing_connections, halfwidth)
        
        """
        from core.modules.basic_modules import identifier as bm_identifier
        from packages.controlflow import identifier as cf_identifier
        
        io_modules = []
        io_connections = []
        
        # Create and connect InputPort for each of the inputs to force it to exist on group
        offset = {}
        [offset.__setitem__(module, halfwidth+65) for module, portspec, connections, halfwidth in input_ports_info]
        for input_module, input_portspec, input_connections, halfwidth in input_ports_info:
            # Remove function calls to selected input ports
            try:
                function_pos = [f.name for f in input_module.functions].index(input_portspec.name)
                self.controller.delete_method(function_pos, input_module.id)
            except:
                pass
            # Disconnect connections to selected input ports
            for connection in input_connections:
                self.connection_ids.remove(connection.id)
                self.controller.delete_connection(connection.id)
            group_inport_module = self.controller.add_module(input_module.location.x-offset[input_module], input_module.location.y, bm_identifier, 'InputPort')
            io_modules.append(group_inport_module)
            offset[input_module] += 130
            for p in group_inport_module.sourcePorts():
                if p.name == 'InternalPipe':
                    group_inport_conn = self.controller.add_connection(input_module.id, input_portspec, group_inport_module.id, p)
                    io_connections.append(group_inport_conn)
                    break
        
        # Create and connect OutputPort for desired output to force it to exist on group
        output_module, output_portspec, output_connections, halfwidth = output_ports_info[0]
        # Disconnect connections to selected output port
        for connection in output_connections:
            self.connection_ids.remove(connection.id)
            self.controller.delete_connection(connection.id)
        group_outport_module = self.controller.add_module(output_module.location.x+halfwidth+75, output_module.location.y, bm_identifier, 'OutputPort')
        io_modules.append(group_outport_module)
        for p in group_outport_module.destinationPorts():
            if p.name == 'InternalPipe':
                group_outport_conn = self.controller.add_connection(output_module.id, output_portspec, group_outport_module.id, p)
                io_connections.append(group_outport_conn)
                break
        
        # Create inner group from selected modules and their connections (plus newly created input/output connections)
        inner_group = self.controller.create_group(self.module_ids + [m.id for m in io_modules], self.connection_ids + [c.id for c in io_connections])
        self.controller.current_pipeline_view.setupScene(self.controller.current_pipeline)
        del io_modules[:]
        del io_connections[:]
        io_modules.append(inner_group)
        io_connections.extend(self.controller.get_connections_to_and_from(self.controller.current_pipeline, [inner_group.id]))
        
        # Add Map module
        map_module = self.controller.add_module(inner_group.location.x-120, inner_group.location.y, cf_identifier, 'Map')
        io_modules.append(map_module)
        
        # Get group 'self' port object
        for p in inner_group.sourcePorts():
            if p.name == 'self':
                inner_group_selfport = p
                break
        
        # Add PythonSource
        py_source_module = self.controller.add_module(inner_group.location.x, inner_group.location.y+75, bm_identifier, 'PythonSource')
        io_modules.append(py_source_module)
        group_type = '('+bm_identifier+':Group)'
        bool_type = '('+bm_identifier+':Boolean)'
        list_type = '('+bm_identifier+':List)'
        string_type = '('+bm_identifier+':String)'
        base_input_ports = []
        base_output_ports = [('output', 'InputList', list_type, 0),
                             ('output', 'InputPort', list_type, 1),
                             ('output', 'OutputPort', string_type, 2)]
        add_input_ports = [('input', 'UseCartesianProduct', bool_type, 1),
                           ('input', 'UserDefinedInputList', list_type, 2)]
        # Add List port to PythonSource module for each input port selected
        sortkey = len(base_input_ports) + len(add_input_ports)
        input_port_names_used = dict([(p[1], 1) for p in base_input_ports])
        for input_module, input_portspec, input_connections, halfwidth in input_ports_info:
            port_name = input_portspec.name
            if port_name not in input_port_names_used:
                input_port_names_used[port_name] = 1
            else:
                input_port_names_used[port_name] += 1
                port_name += '_%d' % input_port_names_used[port_name]
            add_input_ports.append(('input', port_name, list_type, sortkey))
            sortkey += 1
        # Generate the source
        source_code = '''
psrc_module = self.moduleInfo['pipeline'].modules[self.moduleInfo['moduleId']]
input_ports = [p.name for p in psrc_module.input_port_specs if p.name not in ['UseCartesianProduct', 'UserDefinedInputList']]
InputPort = input_ports
OutputPort = '%s'
custom_input_list = self.forceGetInputFromPort('UserDefinedInputList', [])
if custom_input_list:
    InputList = custom_input_list
else:
    cartesian_product = self.forceGetInputFromPort('UseCartesianProduct', False)
    if cartesian_product:
        input_lists = [self.getInputFromPort(input_ports[x]) for x in xrange(len(input_ports))]
        InputList = [[]]
        pools = map(tuple, input_lists)
        for pool in pools:
            InputList = [x+[y] for x in InputList for y in pool]
    else:
        # Dot Product
        InputList = []
        length = len(self.getInputFromPort(input_ports[0]))
        if len(input_ports) > 1:
            for p in input_ports[1:]:
                if len(self.getInputFromPort(p)) != length:
                    fail('One or more of the input lists have different lengths.')
        for x in xrange(length):
            element_list = []
            for p in input_ports:
                element_list.append(self.getInputFromPort(p)[x])
            InputList.append(element_list)
    # Compact list format used when only one input port present
    if len(input_ports) == 1:
        InputList = [x[0] for x in InputList]
print 'InputList: %%s' %% InputList
''' % output_portspec.name
        functions = [('source', [source_code])]
        self.controller.update_ports_and_functions(py_source_module.id, [], base_input_ports + add_input_ports + base_output_ports, functions)
        
        # Create connections to Map
        map_module = self.controller.current_pipeline.modules[map_module.id]
        py_source_module = self.controller.current_pipeline.modules[py_source_module.id]
        psrc_inputlist = py_source_module.get_port_spec('InputList', 'output')
        psrc_inputport = py_source_module.get_port_spec('InputPort', 'output')
        psrc_outputport = py_source_module.get_port_spec('OutputPort', 'output')
        for map_port in map_module.destinationPorts():
            # Connect Group 'self' port to Map's FunctionPort
            if map_port.name == 'FunctionPort':
                map_conn = self.controller.add_connection(inner_group.id, inner_group_selfport, map_module.id, map_port)
            # Connect PythonSource output ports to Map input ports
            elif map_port.name == 'InputList':
                map_conn = self.controller.add_connection(py_source_module.id, psrc_inputlist, map_module.id, map_port)
            elif map_port.name == 'InputPort':
                map_conn = self.controller.add_connection(py_source_module.id, psrc_inputport, map_module.id, map_port)
            elif map_port.name == 'OutputPort':
                map_conn = self.controller.add_connection(py_source_module.id, psrc_outputport, map_module.id, map_port)
            io_connections.append(map_conn)
        
        # Create and connect InputPort for each of the PythonSource inputs to force it to exist on group
        offset = 165
        for port_type, port_name, list_type, sortkey in add_input_ports:
            group_inport_module = self.controller.add_module(py_source_module.location.x-offset, py_source_module.location.y+75, bm_identifier, 'InputPort')
            if (port_type, port_name) in [('input', 'UseCartesianProduct'), ('input', 'UserDefinedInputList')]:
                self.controller.update_ports_and_functions(group_inport_module.id, [], [], [('optional', [True])])
            io_modules.append(group_inport_module)
            offset += 130
            input_portspec = py_source_module.get_port_spec(port_name, port_type)
            for p in group_inport_module.sourcePorts():
                if p.name == 'InternalPipe':
                    group_inport_conn = self.controller.add_connection(py_source_module.id, input_portspec, group_inport_module.id, p)
                    io_connections.append(group_inport_conn)
                    break
        
        # Create and connect OutputPort from Map to force it to exist on group
        group_outport_module = self.controller.add_module(map_module.location.x, map_module.location.y-75, bm_identifier, 'OutputPort')
        io_modules.append(group_outport_module)
        output_portspec = map_module.get_port_spec('Result', 'output')
        for p in group_outport_module.destinationPorts():
            if p.name == 'InternalPipe':
                group_outport_conn = self.controller.add_connection(map_module.id, output_portspec, group_outport_module.id, p)
                io_connections.append(group_outport_conn)
                break
        
        # Create outer group from PythonSource, Map, and inner Group, along with their connections and IO modules
        outer_group = self.controller.create_group([m.id for m in io_modules], [c.id for c in io_connections])
        self.controller.current_pipeline_view.setupScene(self.controller.current_pipeline)
        