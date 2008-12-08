############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

from PyQt4 import QtGui, QtCore
from gui.common_widgets import QToolWindowInterface, QToolWindow
import core.system
import copy
import sys
import time
import os.path
import gui.application
from core.interpreter.default import get_default_interpreter

############################################################################

class QDebugger(QToolWindow, QToolWindowInterface):
    """
    This class provides a dockable interface to the debugger tree.
    """
    def __init__(self, parent, controller):
        QToolWindow.__init__(self, parent=parent)
        self.app = gui.application.VistrailsApplication
        self.inspector = QObjectInspector()
        self.setWidget(self.inspector)
        self.controller = controller
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
        pipe = self.controller.current_pipeline
        try:
            mods_dict, mapping, mod_set, conn_set = self.vistrails_interpreter.setup_pipeline(pipe)
            
            bps = self.controller.breakpoints
            breaks = []

            for m in bps.keys():
                breaks.append(mods_dict[m])
                
            self.inspector.clear_modules()
            for m in breaks:
                m.is_breakpoint = True
                self.inspector.add_module(m, get_vals=update_vals)
                
        except:
            #  The exception is called only when an empty pipeline is sent.
            #  FIXME:  Should I make this into an exception that can be caught?
            pass

#########################################################################################
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

    def clear_modules(self):
        """
        clear_modules() -> None
        Clear the current list of module breakpoints
        """
        self.clear()
     
    def add_module(self, m, get_vals=False):
        """
        add_module(m, get_vals=False) -> None
        Add the give module, m, as a breakpoint.
        """
        item = QDebugModuleItem(self)
        classstr = str(m.__class__)
        classstr = classstr.split('.')
        classstr = classstr[len(classstr) - 1]
        classstr = classstr[0:len(classstr) - 2]
        item.setText(0, classstr)
        item.setText(1, "Module Type")
        self.add_dict(m, item)
        self.add_ports(m, item, display_vals=get_vals)
        
    def add_dict(self, m, item):
        """
        add_dict(m, item) -> None
        Add the dictionary associated with module m to be displayed as part of the
        debug information for that breakpoint.
        """
        dict_item = QDebugModuleItem(item)
        dict_item.setText(0, "__dict__")
        dict_item.setText(1, "")
        for k in m.__dict__.keys():
            d_val = QDebugModuleItem(dict_item)
            d_val.setText(0, str(k))
            d_val.setText(1, str(m.__dict__[k]))

    def add_ports(self, m, item, display_vals=False):
        """
        add_ports(m, item, display_vals=False) -> None
        Add port information from module m to the item being displayed in the debugger.
        If display_vals is True, fetch the appropriate values from the module's input ports.
        """
        ports = m.__dict__["inputPorts"]
        port_item = QDebugModuleItem(item)
        port_item.setText(0, "inputPorts")
        port_item.setText(1, "")
        for p in ports.keys():
            p_val = QDebugModuleItem(port_item)
            p_val.setText(0, str(p))
            if display_vals:
                port_value = m.getInputFromPort(p)
                p_val.setText(1, str(port_value))
            else:
                c = ports[p][0]
                typestr = str(c.obj.__class__)
                typestr = typestr.split('.')
                typestr = typestr[len(typestr)-1]
                typestr = typestr[0:len(typestr)-2]
                p_val.setText(1, typestr)            

########################################################################
# QDebugModuleItem

class QDebugModuleItem(QtGui.QTreeWidgetItem):
    """
    This class provides a unique container for adding breakpoints in a workflow
    to the debugger.
    """
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        
