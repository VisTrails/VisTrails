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
from core.system import systemType

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

    def deletedModule(self, descriptor):
        """ deletedModule(descriptor: core.modules.module_registry.ModuleDescriptor)
        A module has been removed from VisTrails

        """
        moduleName = descriptor.name

        items = [x
                 for x in
                 self.treeWidget.findItems(moduleName,
                                           QtCore.Qt.MatchExactly |
                                           QtCore.Qt.MatchWrap |
                                           QtCore.Qt.MatchRecursive)
                 if not x.is_top_level()]
        assert len(items) == 1
        item = items[0]

        parent = item.parent()
        parent.takeChild(parent.indexOfChild(item))

    def deletedPackage(self, package_name):
        """ deletedPackage(package_name):
        A package has been deleted from VisTrails
        """
        
        items = self.treeWidget.findItems(package_name,
                                          QtCore.Qt.MatchExactly |
                                          QtCore.Qt.MatchWrap)
        assert len(items) == 1
        item = items[0]

        index = self.treeWidget.indexOfTopLevelItem(item)
        self.treeWidget.takeTopLevelItem(index)

    def newModule(self, descriptor):
        """ newModule(descriptor: core.modules.module_registry.ModuleDescriptor)
        A new module has been added to VisTrails
        
        """
        moduleName = descriptor.name
        packageName = registry.get_module_package(moduleName)

        # NB: only looks for toplevel matches
        packageItems = self.treeWidget.findItems(packageName,
                                                 QtCore.Qt.MatchExactly |
                                                 QtCore.Qt.MatchWrap)
        assert(len(packageItems)<=1)
        if packageItems==[]:
            # didn't find a top-level package item, so let's create one
            parentItem = QModuleTreeWidgetItem(None,
                                               None,
                                               QtCore.QStringList(packageName))
            self.treeWidget.insertTopLevelItem(0, parentItem)
        else:
            parentItem = packageItems[0]

        # Determines where to attach the new item
        direct_parent = registry.getModuleHierarchy(moduleName)[1]
        parent_descriptor = registry.getDescriptor(direct_parent)

        # if module package is different, attach to toplevel of this package.

        if parent_descriptor.module_package() == packageName:
            # if module package is the same, then find the parent in this package

            # filtering is necessary for cases where module name is
            # the same as top-level
            lst = [x
                   for x in
                   self.treeWidget.findItems(parent_descriptor.name,
                                             QtCore.Qt.MatchExactly |
                                             QtCore.Qt.MatchWrap |
                                             QtCore.Qt.MatchRecursive)
                   if not x.is_top_level()]

            assert len(lst) == 1
            parentItem = lst[0]
        
        desc = registry.getDescriptorByName(moduleName)
        item = QModuleTreeWidgetItem(desc,
                                     parentItem,
                                     QtCore.QStringList(moduleName))
        self.treeWidget.setCurrentItem(item)

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
        self.setRootIsDecorated(False)
        self.delegate = QModuleTreeWidgetItemDelegate(self, self)
        self.setItemDelegate(self.delegate)
        self.connect(self,
                     QtCore.SIGNAL('itemPressed(QTreeWidgetItem *,int)'),
                     self.onItemPressed)

    def onItemPressed(self, item, column):
        """ onItemPressed(item: QTreeWidgetItem, column: int) -> None
        Expand/Collapse top-level item when the mouse is pressed
        
        """
        if item and item.parent()==None:
            self.setItemExpanded(item, not self.isItemExpanded(item))
        
    def updateFromModuleRegistry(self):
        """ updateFromModuleRegistry(packageName: str) -> None
        Setup this tree widget to show modules currently inside
        module_registry.registry
        
        """
        parentItems = {}
        
        def createModuleItem(module):
            """ createModuleItem(registry: ModuleRegistry,
                                 parentItem: QModuleTreeWidgetItem,
                                 module: Tree) -> QModuleTreeWidgetItem
            Traverse a module to create items recursively. Then return
            its module item
            
            """
            labels = QtCore.QStringList(module.descriptor.name)
            packageName = module.descriptor.module_package()
            parentItem = parentItems[packageName]
            moduleItem = QModuleTreeWidgetItem(module.descriptor,
                                               parentItem,
                                               labels)
            parentItems[packageName] = moduleItem
            for child in module.children:
                createModuleItem(child)
            parentItems[packageName] = parentItem

        for packageName in registry.packageModules.iterkeys():
            item = QModuleTreeWidgetItem(None,
                                         self,
                                         QtCore.QStringList(packageName))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDragEnabled)
            parentItems[packageName] = item
        module = registry.classTree
        createModuleItem(module)
        self.expandAll()

class QModuleTreeWidgetItemDelegate(QtGui.QItemDelegate):
    """    
    QModuleTreeWidgetItemDelegate will override the original
    QTreeWidget paint function to draw buttons for top-level item
    similar to QtDesigner. This mimics
    Qt/tools/designer/src/lib/shared/sheet_delegate, which is only a
    private class from QtDesigned.
    
    """
    def __init__(self, view, parent):
        """ QModuleTreeWidgetItemDelegate(view: QTreeView,
                                          parent: QWidget)
                                          -> QModuleTreeWidgetItemDelegate
        Create the item delegate given the tree view
        
        """
        QtGui.QItemDelegate.__init__(self, parent)
        self.treeView = view
        self.isMac = systemType in ['Darwin']

    def paint(self, painter, option, index):
        """ painter(painter: QPainter, option QStyleOptionViewItem,
                    index: QModelIndex) -> None
        Repaint the top-level item to have a button-look style
        
        """
        model = index.model()
        if model.parent(index).isValid()==False:
            buttonOption = QtGui.QStyleOptionButton()            
            buttonOption.state = option.state
            if self.isMac:
                buttonOption.state |= QtGui.QStyle.State_Raised
            buttonOption.state &= ~QtGui.QStyle.State_HasFocus

            buttonOption.rect = option.rect
            buttonOption.palette = option.palette
            buttonOption.features = QtGui.QStyleOptionButton.None

            style = self.treeView.style()
            
            style.drawControl(QtGui.QStyle.CE_PushButton,
                              buttonOption,
                              painter,
                              self.treeView)

            branchOption = QtGui.QStyleOption()
            i = 9 ### hardcoded in qcommonstyle.cpp
            r = option.rect
            branchOption.rect = QtCore.QRect(r.left() + i/2,
                                             r.top() + (r.height() - i)/2,
                                             i, i)
            branchOption.palette = option.palette
            branchOption.state = QtGui.QStyle.State_Children

            if self.treeView.isExpanded(index):
                branchOption.state |= QtGui.QStyle.State_Open
                
            style.drawPrimitive(QtGui.QStyle.PE_IndicatorBranch,
                                branchOption,
                                painter, self.treeView)

            textrect = QtCore.QRect(r.left() + i*2,
                                    r.top(),
                                    r.width() - ((5*i)/2),
                                    r.height())
            text = option.fontMetrics.elidedText(
                model.data(index,
                           QtCore.Qt.DisplayRole).toString(),
                QtCore.Qt.ElideMiddle, 
                textrect.width())
            style.drawItemText(painter,
                               textrect,
                               QtCore.Qt.AlignCenter,
                               option.palette,
                               self.treeView.isEnabled(),
                               text)
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        """ sizeHint(option: QStyleOptionViewItem, index: QModelIndex) -> None
        Take into account the size of the top-level button
        
        """
        return (QtGui.QItemDelegate.sizeHint(self, option, index) +
                QtCore.QSize(2, 2))



class QModuleTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QModuleTreeWidgetItem represents module on QModuleTreeWidget
    
    """
    
    def __init__(self, descriptor, parent, labelList):
        """ QModuleTreeWidgetItem(descriptor: ModuleDescriptor
                                    (or None for top-level),
                                  parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QModuleTreeWidget                                  
        Create a new tree widget item with a specific parent and
        labels

        """
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
        self.descriptor = descriptor
        if descriptor:
            descriptor.set_widget(self)
        # Real flags store the widget's flags prior to masking related
        # to abstract modules, etc.
        self._real_flags = self.flags()

        # This is necessary since we override setFlags
        self.setFlags(self._real_flags)

    def added_input_port(self):
        self.setFlags(self._real_flags)

    def added_output_port(self):
        self.setFlags(self._real_flags)

    def setFlags(self, flags):
        self._real_flags = flags
        d = self.descriptor
        if d is None:
            # toplevel moduletree widgets are never draggable
            flags = flags & ~QtCore.Qt.ItemIsDragEnabled
        elif d.module_abstract():
            # moduletree widgets for abstract modules are never
            # draggable or enabled
            flags = flags & ~(QtCore.Qt.ItemIsDragEnabled |
                              QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
        QtGui.QTreeWidgetItem.setFlags(self, flags)
            
    def is_top_level(self):
        return self.descriptor is None
