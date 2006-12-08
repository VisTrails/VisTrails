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
        
