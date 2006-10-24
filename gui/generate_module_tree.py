from PyQt4 import QtCore, QtGui, QtOpenGL
from qbuildertreewidget import *
from vis_types import VistrailModuleType
import modules
import modules.module_registry

class GenerateModuleTree(QtCore.QObject):
    
    activeModuleFlags = (QtCore.Qt.ItemIsSelectable |
                         QtCore.Qt.ItemIsEnabled |
                         QtCore.Qt.ItemIsDragEnabled |
                         QtCore.Qt.ItemIsDropEnabled)

    inactiveModuleFlags = (QtCore.Qt.ItemIsSelectable |
                           QtCore.Qt.ItemIsEnabled)

    def __init__(self, palette):
        QtCore.QObject.__init__(self)
        self.palette = palette
        self.widgets = {}

    def makeWidget(self, parentWidget, name):
        labels = QtCore.QStringList()
        labels << name << "Module"
        widget = MyQTreeWidgetItem(parentWidget, labels)
        widget.index = self.palette.indexFromItem(widget, 0)
        self.palette.setItemExpanded(widget, True)
        widget.setFlags(self.activeModuleFlags)
        self.widgets[name] = widget
        self.palette.allItems.append(widget)
        return widget
        
    def generateModuleHierarchy(self):
        baseNode = modules.module_registry.registry.classTree
        baseWidget = self.makeWidget(self.palette, "Module")
        self.generateModuleTreeNode(baseWidget, baseNode)
        return baseWidget
    
    def generateModuleTreeNode(self, baseWidget, baseNode):
        for child in baseNode.children:
            subclassWidget = self.makeWidget(baseWidget,
                                             child.descriptor.name)
            self.generateModuleTreeNode(subclassWidget, child)

    def newModule(self, moduleName):
        d = modules.module_registry.registry.getDescriptorByName(moduleName)
        parentName = d.baseDescriptor.name
        self.makeWidget(self.widgets[parentName], moduleName)
