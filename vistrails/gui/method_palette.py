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
""" This file contains widgets related to the method palette
displaying a list of all functions available in a module

QMethodPalette
QMethodTreeWidget
QMethodTreeWidgetItem
"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import (QSearchTreeWindow,
                                QSearchTreeWidget,
                                QToolWindowInterface)
from core.modules.module_registry import get_module_registry, \
    ModuleRegistryException
from core.vistrail.port import PortEndPoint
from gui.port_documentation import QPortDocumentation
################################################################################

class QMethodPalette(QSearchTreeWindow, QToolWindowInterface):
    """
    QModulePalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def __init__(self, parent=None):
        QSearchTreeWindow.__init__(self, parent)
        
    def createTreeWidget(self):
        """ createTreeWidget() -> QMethodTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle('Methods')
        return QMethodTreeWidget(self)

    def updateModule(self, module):
        self.module = module
        self.treeWidget.updateModule(module)

class QMethodTreeWidget(QSearchTreeWidget):
    """
    QMethodTreeWidget is a subclass of QSearchTreeWidget to display all
    methods available of a module
    
    """
    def __init__(self, parent=None):
        """ QModuleMethods(parent: QWidget) -> QModuleMethods
        Set up size policy and header

        """
        QSearchTreeWidget.__init__(self, parent)
        self.header().setStretchLastSection(True)
        self.setHeaderLabels(QtCore.QStringList() << 'Method' << 'Signature')

    def updateModule(self, module):
        """ updateModule(module: Module) -> None        
        Setup this tree widget to show functions of module
        
        """
        self.clear()

        if module:
            registry = get_module_registry()
            try:
                descriptor = module.module_descriptor
            except ModuleRegistryException, e:
                # FIXME handle this the same way as
                # vistrail_controller:change_selected_version
                raise
            moduleHierarchy = registry.get_module_hierarchy(descriptor)

            base_items = {}
            # Create the base widget item for each descriptor
            for descriptor in moduleHierarchy:
                baseName = descriptor.name
                base_package = descriptor.identifier
                baseItem = QMethodTreeWidgetItem(None,
                                                 None,
                                                 self,
                                                 (QtCore.QStringList()
                                                  <<  baseName
                                                  << ''))
                base_items[descriptor] = baseItem

            method_specs = {}
            # do this in reverse to ensure proper overloading
            # !!! NOTE: we have to use ***all*** input ports !!!
            # because a subclass can overload a port with a 
            # type that isn't a method
            for descriptor in reversed(moduleHierarchy):
                method_specs.update((name, (descriptor, spec))
                                    for name, spec in \
                                        registry.module_ports('input', 
                                                              descriptor))

            # add local registry last so that it takes precedence
            method_specs.update((spec.name, (descriptor, spec))
                                for spec in module.port_spec_list
                                if spec.type == 'input')

            for _, (desc, method_spec) in sorted(method_specs.iteritems()):
                if registry.is_method(method_spec):
                    baseItem = base_items[desc]
                    sig = method_spec.short_sigstring
                    QMethodTreeWidgetItem(module,
                                          method_spec,
                                          baseItem,
                                          (QtCore.QStringList()
                                           << method_spec.name
                                           << sig))

            self.expandAll()
            self.resizeColumnToContents(0)
                                          
    def contextMenuEvent(self, event):
        # Just dispatches the menu event to the widget item
        item = self.itemAt(event.pos())
        if item:
            item.contextMenuEvent(event, self)

class QMethodTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QMethodTreeWidgetItem represents method on QMethodTreeWidget
    
    """
    def __init__(self, module, spec, parent, labelList):
        """ QMethodTreeWidgetItem(module: Module
                                  spec: PortSpec,
                                  parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QMethodTreeWidgetItem                               
        Create a new tree widget item with a specific parent and
        labels

        """
        self.module = module
        self.spec = spec
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)

    def contextMenuEvent(self, event, widget):
        if self.module is None:
            return
        act = QtGui.QAction("View Documentation", widget)
        act.setStatusTip("View method documentation")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.view_documentation)
        menu = QtGui.QMenu(widget)
        menu.addAction(act)
        menu.exec_(event.globalPos())
        
    def view_documentation(self):
        registry = get_module_registry()
        descriptor = registry.get_descriptor_by_name(self.module.package,
                                                     self.module.name,
                                                     self.module.namespace)
        widget = QPortDocumentation(descriptor,
                                    PortEndPoint.Destination,
                                    self.spec.name)
        widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        widget.exec_()
