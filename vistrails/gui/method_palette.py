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
from core.modules.module_registry import registry

################################################################################

class QMethodPalette(QSearchTreeWindow, QToolWindowInterface):
    """
    QModulePalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def createTreeWidget(self):
        """ createTreeWidget() -> QMethodTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle('Methods')
        return QMethodTreeWidget(self)

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
            moduleHierarchy = registry.getModuleHierarchy(module.name)
            for baseModule in moduleHierarchy:
                baseName = registry.getDescriptor(baseModule).name
                # Create the base widget item
                baseItem = QMethodTreeWidgetItem(None,
                                                 None,
                                                 self,
                                                 (QtCore.QStringList()
                                                  <<  baseName
                                                  << ''))
                methods = registry.methodPorts(baseModule)
                # Also check the local registry
                if module.registry and module.registry.hasModule(baseName):
                    methods += module.registry.methodPorts(baseModule)
                for method in methods:
                    for spec in method.spec:
                        sig = method.getSig(spec)
                        QMethodTreeWidgetItem(method,
                                              spec,
                                              baseItem,
                                              (QtCore.QStringList()
                                               << method.name
                                               << sig))
            self.expandAll()
                                          
class QMethodTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QMethodTreeWidgetItem represents module on QModuleTreeWidget
    
    """
    def __init__(self, port, spec, parent, labelList):
        """ QMethodTreeWidgetItem(port: Port,
                                  spec: tuple,
                                  parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QMethodTreeWidgetItem                               
        Create a new tree widget item with a specific parent and
        labels

        """
        self.port = port
        self.spec = spec
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
