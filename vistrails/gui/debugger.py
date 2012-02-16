###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from PyQt4 import QtGui, QtCore
import core.system
import copy
import sys
import time
import os.path
import gui.application
from core.interpreter.default import get_default_interpreter
from gui.vistrails_palette import QVistrailsPaletteInterface

############################################################################

class QDebugger(QtGui.QWidget, QVistrailsPaletteInterface):
    """
    This class provides a dockable interface to the debugger tree.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.app = gui.application.get_vistrails_application()
        self.inspector = QObjectInspector()
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.inspector)
        self.setLayout(layout)
        # self.setTitleBarWidget(QtGui.QLabel("Debugger"))
        self.setWindowTitle("Debugger")
        self.controller = None
        self.vistrails_interpreter = get_default_interpreter()
        self.vistrails_interpreter.debugger = self

    def set_controller(self, c):
        """
        set_controller(c) -> None
        Set the current vistrails controller to be used by the debugger
        """
        self.controller = c
        self.update()

    def update_values(self):
        """
        update_vals() -> None
        Update the debugger after an execution with any values that become
        available on its input ports.
        """
        self.update(update_vals=True)
        
    def update(self, update_vals=False):
        """
        update(update_vals=False) -> None
        Update the debugger.  If the update requires querying modules for input
        changes, update_vals should be set to True
        """
        pipeline = self.controller.current_pipeline
        if pipeline is None:
            return

        self.inspector.clear_modules()
        for module in pipeline.module_list:
            if module.is_breakpoint or module.is_watched:
                self.inspector.add_module(module)
        if update_vals:
            (module_objects, _, _) = \
                self.vistrails_interpreter.find_persistent_entities(pipeline)
            for m_id in self.inspector.modules:
                if m_id in module_objects and module_objects[m_id] is not None:
                    self.inspector.update_values(m_id, module_objects[m_id])
                elif module_objects[m_id] is None:
                    edges = pipeline.graph.edges_to(m_id)
                    self.inspector.update_inputs(m_id, module_objects, edges,
                                                  pipeline.connections)

    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        self.emit(QtCore.SIGNAL("debuggerHidden()"))
                        
###############################################################################
#  QObjectInspector

class QObjectInspector(QtGui.QTreeWidget):
    """
    This class provides the ability to track and inspect breakpoints added to a pipeline.
    It is meant to be embedded in the QDebugger object to allow debugging of workflows in
    VisTrails
    """
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.modules = {}

    def clear_modules(self):
        """
        clear_modules() -> None
        Clear the current list of module breakpoints
        """
        self.modules = {}
        self.clear()
     
    def add_module(self, m):
        """
        add_module(m : core.vistrail.module.Module) -> None
        Add the give module, m, as a breakpoint.
        """
        # !!! This uses the core.vistrail.module.Module item
        item = QDebugModuleItem(self)
        item.setText(0, "%s (%d)" % (m.name, m.id))
        item.setText(1, "Module Type")
        self.modules[m.id] = item
#         self.add_dict(m, item)
#         self.add_ports(m, item, display_vals=get_vals)
        
    def update_values(self, m_id, persistent_module):
        """
        update_values(m_id: long, 
          persistent_module : subclass of core.modules.vistrails_module.Module)
        """
        module_item = self.modules[m_id]
        module_item.takeChildren()
        self.add_dict(persistent_module, module_item)
        self.add_ports(persistent_module, module_item, True)

    def update_inputs(self, m_id, persistent_map, edges, connections):
        input_ports = {}
        for upstream_id, c_id in edges:
            if upstream_id in persistent_map and \
                    persistent_map[upstream_id] is not None:
                persistent_module = persistent_map[upstream_id]
                connection = connections[c_id]
                try:
                    output_port = \
                        persistent_module.get_output(connection.source.name)
                    input_ports[connection.destination.name] = output_port
                except ModuleError:
                    input_ports[connection.destination.name] = None
        if len(input_ports) > 0:
            module_item = self.modules[m_id]
            module_item.takeChildren()
            inputs_item = QDebugModuleItem(module_item)
            inputs_item.setText(0, "inputPorts")
            inputs_item.setText(1, "")   
            for port_name, port_val in input_ports.iteritems():
                self.create_port_item(port_name, port_val, True, 
                                      inputs_item)
                
    def add_dict(self, m, parent_item):
        """
        add_dict(m, parent_item) -> None
        Add the dictionary associated with module m to be displayed 
        as part of the debug information for that breakpoint.
        """
        dict_item = QDebugModuleItem(parent_item)
        dict_item.setText(0, "__dict__")
        dict_item.setText(1, "")
        for k in m.__dict__.keys():
            d_val = QDebugModuleItem(dict_item)
            d_val.setText(0, str(k))
            d_val.setText(1, str(m.__dict__[k]))


    def create_port_item(self, port_name, port_value, display_vals=False,
                         parent=None):
        p_item = QDebugModuleItem(parent)
        p_item.setText(0, str(port_name))
        if display_vals:
            p_item.setText(1, str(port_value))
        else:
            typestr = str(port_val.__class__)
            typestr = typestr.split('.')
            typestr = typestr[len(typestr)-1]
            typestr = typestr[0:len(typestr)-2]
            p_item.setText(1, typestr)            
            
    def add_ports(self, m, parent_item, display_vals=False):
        """
        add_ports(m, item, display_vals=False) -> None
        Add port information from module m to the item being displayed in the debugger.
        If display_vals is True, fetch the appropriate values from the module's input ports.
        """
        inputs_item = QDebugModuleItem(parent_item)
        inputs_item.setText(0, "inputPorts")
        inputs_item.setText(1, "")
        for port_name in m.inputPorts:
            try:
                port_val = m.getInputListFromPort(port_name)
                if len(port_val) == 1:
                    port_val = port_val[0]
            except ModuleError:
                port_val = None
            self.create_port_item(port_name, port_val, display_vals, 
                                  inputs_item)
        outputs_item = QDebugModuleItem(parent_item)
        outputs_item.setText(0, "outputPorts")
        outputs_item.setText(1, "")
        for port_name in m.outputPorts:
            try:
                port_val = m.get_output(port_name)
            except ModuleError:
                port_val = None
            self.create_port_item(port_name, port_val, display_vals, 
                                  outputs_item)

########################################################################
# QDebugModuleItem

class QDebugModuleItem(QtGui.QTreeWidgetItem):
    """
    This class provides a unique container for adding breakpoints in a workflow
    to the debugger.
    """
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        
