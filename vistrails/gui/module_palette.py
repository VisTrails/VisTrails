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
""" This file contains widgets related to the module palette
displaying a list of all modules in Vistrails

QModulePalette
QModuleTreeWidget
QModuleTreeWidgetItem
"""

from PyQt4 import QtCore, QtGui
from gui.common_widgets import (QSearchTreeWindow,
                                QSearchTreeWidget,
                                QToolWindowInterface)
from core.modules.module_registry import registry

################################################################################

class QModulePalette(QSearchTreeWindow, QToolWindowInterface):
    """
    QModulePalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def createTreeWidget(self):
        """ createTreeWidget() -> QModuleTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle('Modules')
        return QModuleTreeWidget(self)

    def newModule(self, descriptor):
        """ newModule(descriptor: ModuleDescriptor) -> None
        A new module has been added to Vistrail
        
        """
        print 'Unhandled module addition'

class QModuleTreeWidget(QSearchTreeWidget):
    """
    QModuleTreeWidget is a subclass of QSearchTreeWidget to display all
    Vistrails Module
    
    """
    def __init__(self, parent=None):
        """ QModuleTreeWidget(parent: QWidget) -> QModuleTreeWidget
        Set up size policy and header

        """
        QSearchTreeWidget.__init__(self, parent)
        self.header().hide()
        
    def updateFromModuleRegistry(self):
        """ updateFromModuleRegistry() -> None        
        Setup this tree widget to show modules currently inside
        module_registry.registry
        
        """
        def createModuleItem(parentItem, module):
            """ createModuleItem(parentItem: QModuleTreeWidgetItem,
                                 module: Tree) -> QModuleTreeWidgetItem                                 
            Traverse a module to create items recursively. Then return
            its module item
            
            """
            labels = QtCore.QStringList()
            labels << module.descriptor.name
            moduleItem = QModuleTreeWidgetItem(module.descriptor,
                                               parentItem,
                                               labels)
            for child in module.children:
                createModuleItem(moduleItem, child)
            
        module = registry.classTree
        createModuleItem(self, module)
        self.expandAll()

class QModuleTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QModuleTreeWidgetItem represents module on QModuleTreeWidget
    
    """
    def __init__(self, descriptor, parent, labelList):
        """ QModuleTreeWidgetItem(parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QModuleTreeWidget                                  
        Create a new tree widget item with a specific parent and
        labels

        """
        self.descriptor = descriptor
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
        
