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
from gui.module_documentation import QModuleDocumentation
from core.modules.module_registry import get_module_registry
from core.system import systemType
from core.utils import VistrailsInternalError
from core.packagemanager import get_package_manager
import weakref

################################################################################
                
class QModulePalette(QSearchTreeWindow, QToolWindowInterface):
    """
    QModulePalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def __init__(self, parent=None):
        QSearchTreeWindow.__init__(self, parent)
        self.packages = {}
        self.namespaces = {}

    def connect_registry_signals(self):
        registry = get_module_registry()
        self.connect(registry.signals, registry.signals.new_package_signal,
                     self.newPackage)
        self.connect(registry.signals, registry.signals.new_module_signal,
                     self.newModule)
        self.connect(registry.signals, registry.signals.deleted_module_signal,
                     self.deletedModule)
        self.connect(registry.signals, registry.signals.deleted_package_signal,
                     self.deletedPackage)        
        self.connect(registry.signals, registry.signals.show_module_signal,
                     self.showModule)
        self.connect(registry.signals, registry.signals.hide_module_signal,
                     self.hideModule)
        self.connect(registry.signals, registry.signals.module_updated_signal,
                     self.switchDescriptors)
    
    def createTreeWidget(self):
        """ createTreeWidget() -> QModuleTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle('Modules')
        return QModuleTreeWidget(self)

    def findModule(self, descriptor):
        moduleName = descriptor.name
        
        items = [x for x in
                 self.treeWidget.findItems(moduleName,
                                           QtCore.Qt.MatchExactly | 
                                           QtCore.Qt.MatchWrap | 
                                           QtCore.Qt.MatchRecursive)
                 if not x.is_top_level() and x.descriptor == descriptor]
        if len(items) <> 1:
            raise VistrailsInternalError("Expected one item (%s), got %d: %s" % 
                                         (moduleName,
                                          len(items),
                                          ";".join(x.descriptor.name 
                                                   for x in items)))
        item = items[0]
        return item

    def showModule(self, descriptor):
        item = self.findModule(descriptor)
        item.setHidden(False)

    def hideModule(self, descriptor):
        item = self.findModule(descriptor)
        item.setHidden(True)

    def switchDescriptors(self, old_descriptor, new_descriptor):
        old_item = self.findModule(old_descriptor)
        new_item = self.findModule(new_descriptor)
        old_item.set_descriptor(new_descriptor)
        new_item.set_descriptor(old_descriptor)

    def deletedModule(self, descriptor):
        """ deletedModule(descriptor: core.modules.module_registry.ModuleDescriptor)
        A module has been removed from VisTrails

        """
        if descriptor.module_abstract():
            # skip abstract and hidden modules, they're not in the tree
            return

        item = self.findModule(descriptor)
        parent = item.parent()
        parent.takeChild(parent.indexOfChild(item))
        del item.descriptor

    def deletedPackage(self, package):
        """ deletedPackage(package):
        A package has been deleted from VisTrails
        """
        item = self.packages[package.identifier]()        
        index = self.treeWidget.indexOfTopLevelItem(item)
        self.treeWidget.takeTopLevelItem(index)
        del self.packages[package.identifier]

    def newPackage(self, package_identifier, prepend=False):
        # prepend places at the front of the list of packages,
        # by default adds to the end of the list of packages
        registry = get_module_registry()
        package_name = registry.packages[package_identifier].name
        package_item = \
            QPackageTreeWidgetItem(None, QtCore.QStringList(package_name))
        self.packages[package_identifier] = weakref.ref(package_item)
        if prepend:
            self.treeWidget.insertTopLevelItem(0, package_item)
        else:
            self.treeWidget.addTopLevelItem(package_item)
        return package_item
            
    def newModule(self, descriptor, recurse=False):
        """ newModule(descriptor: core.modules.module_registry.ModuleDescriptor)
        A new module has been added to VisTrails
        
        """
        if not descriptor.module_abstract(): # and not descriptor.is_hidden:
            # skip abstract modules, they're no longer in the tree

            # NB: only looks for toplevel matches
            package_identifier = descriptor.ghost_identifier or descriptor.identifier
            if package_identifier not in self.packages:
                package_item = self.newPackage(package_identifier, True)
            else:
                package_item = self.packages[package_identifier]()

            if descriptor.namespace_hidden or not descriptor.namespace:
                parent_item = package_item
            else:
                parent_item = \
                    package_item.get_namespace(descriptor.namespace.split('|'))

            item = QModuleTreeWidgetItem(descriptor, parent_item,
                                         QtCore.QStringList(descriptor.name))
            if descriptor.is_hidden:
                item.setHidden(True)
        if recurse:
            for child in descriptor.children:
                self.newModule(child, recurse)

    def updateFromModuleRegistry(self):
        """ updateFromModuleRegistry(packageName: str) -> None
        Setup this tree widget to show modules currently inside
        module_registry.registry
        
        """

        registry = get_module_registry()
        for package in registry.package_list:
            self.newPackage(package.identifier)
        self.newModule(registry.root_descriptor, True)
        self.treeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.treeWidget.expandAll()

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
        if item and item.parent() == None:
            self.setItemExpanded(item, not self.isItemExpanded(item))

    def contextMenuEvent(self, event):
        # Just dispatches the menu event to the widget item
        item = self.itemAt(event.pos())
        if item:
            # find top level
            p = item
            while p.parent():
                p = p.parent()
            # get package identifier
            identifiers = [i for i, j in self.parent().packages.iteritems()
                           if j == weakref.ref(p)]
            if identifiers:
                identifier = identifiers[0]
                registry = get_module_registry()
                package = registry.packages[identifier]
                if package.has_contextMenuName():
                    name = package.contextMenuName(str(item.text(0)))
                    if name:
                        act = QtGui.QAction(name, self)
                        act.setStatusTip(name)
                        def callMenu():
                            if package.has_callContextMenu():
                                name = package.callContextMenu(str(item.text(0)))
                            
                        QtCore.QObject.connect(act,
                                               QtCore.SIGNAL("triggered()"),
                                               callMenu)
                        menu = QtGui.QMenu(self)
                        menu.addAction(act)
                        menu.exec_(event.globalPos())
                    return

                    
            item.contextMenuEvent(event, self)

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
        if not model.parent(index).isValid():
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
            branchOption.rect = QtCore.QRect(r.left() + i / 2,
                                             r.top() + (r.height() - i) / 2,
                                             i, i)
            branchOption.palette = option.palette
            branchOption.state = QtGui.QStyle.State_Children

            if self.treeView.isExpanded(index):
                branchOption.state |= QtGui.QStyle.State_Open
                
            style.drawPrimitive(QtGui.QStyle.PE_IndicatorBranch,
                                branchOption,
                                painter, self.treeView)

            textrect = QtCore.QRect(r.left() + i * 2,
                                    r.top(),
                                    r.width() - ((5 * i) / 2),
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
        self.set_descriptor(descriptor)

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
                              QtCore.Qt.ItemIsSelectable)
        QtGui.QTreeWidgetItem.setFlags(self, flags)
            
    def is_top_level(self):
        return self.descriptor is None

    def contextMenuEvent(self, event, widget):
        if self.is_top_level():
            return
        act = QtGui.QAction("View Documentation", widget)
        act.setStatusTip("View module documentation")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.view_documentation)
        menu = QtGui.QMenu(widget)
        menu.addAction(act)
        menu.exec_(event.globalPos())

    def view_documentation(self):
        widget = QModuleDocumentation(self.descriptor, None)
        widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        widget.exec_()

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor
        if descriptor:
            descriptor.set_widget(self)

class QNamespaceTreeWidgetItem(QModuleTreeWidgetItem):
    def __init__(self, parent, labelList):
        QModuleTreeWidgetItem.__init__(self, None, parent, labelList)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDragEnabled)
        self.namespaces = {}

    def get_namespace(self, namespace_items):
        if len(namespace_items) <= 0:
            return self
        namespace_item = namespace_items.pop(0)
        if namespace_item in self.namespaces and self.namespaces[namespace_item]():
            item = self.namespaces[namespace_item]()
        else:
            item = QNamespaceTreeWidgetItem(self,
                                            QtCore.QStringList(namespace_item))
            self.namespaces[namespace_item] = weakref.ref(item)
        return item.get_namespace(namespace_items)

    def takeChild(self, index):
        child = self.child(index)
        if hasattr(self, "namespaces"):
            if str(child.text(0)) in self.namespaces:
                del self.namespaces[str(child.text(0))]
        QModuleTreeWidgetItem.takeChild(self, index)
        if self.childCount() < 1 and self.parent():
            self.parent().takeChild(self.parent().indexOfChild(self))

class QPackageTreeWidgetItem(QNamespaceTreeWidgetItem):
    pass
