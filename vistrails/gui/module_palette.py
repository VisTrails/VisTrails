###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
""" This file contains widgets related to the module palette
displaying a list of all modules in Vistrails

QModulePalette
QModuleTreeWidget
QModuleTreeWidgetItem
"""
from __future__ import division

import os
import traceback
from PyQt4 import QtCore, QtGui
from vistrails.core import get_vistrails_application
from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.system import systemType
from vistrails.core.utils import VistrailsInternalError
from vistrails.gui.common_widgets import (QSearchTreeWindow,
                                QSearchTreeWidget)
from vistrails.gui.module_documentation import QModuleDocumentation
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

class QModulePalette(QSearchTreeWindow, QVistrailsPaletteInterface):
    """
    QModulePalette just inherits from QSearchTreeWindow to have its
    own type of tree widget

    """
    def __init__(self, parent=None):
        QSearchTreeWindow.__init__(self, parent)
        self.setContentsMargins(0,5,0,0)
        self.packages = {}
        self.namespaces = {}
        self.addButtonsToToolBar()

    def addButtonsToToolBar(self):
        self.expandAction = QtGui.QAction(CurrentTheme.EXPAND_ALL_ICON,
                                           "Expand All", self.toolWindow().toolbar,
                                           triggered=self.expandAll)

        self.collapseAction = QtGui.QAction(CurrentTheme.COLLAPSE_ALL_ICON,
                                           "Collapse All", self.toolWindow().toolbar,
                                           triggered=self.collapseAll)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.collapseAction)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.expandAction)

    def expandAll(self):
        self.treeWidget.expandAll()

    def collapseAll(self):
        self.treeWidget.collapseAll()

    def link_registry(self):
        self.updateFromModuleRegistry()
        self.connect_registry_signals()


    def connect_registry_signals(self):
        app = get_vistrails_application()
        app.register_notification("reg_new_module", self.newModule)
        app.register_notification("reg_new_package", self.newPackage)
        app.register_notification("reg_deleted_module", self.deletedModule)
        app.register_notification("reg_deleted_package", self.deletedPackage)
        app.register_notification("reg_show_module", self.showModule)
        app.register_notification("reg_hide_module", self.hideModule)
        app.register_notification("reg_module_updated", self.switchDescriptors)

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
        try:
            item = self.packages[package.identifier]
        except KeyError:
            pass
        else:
            index = self.treeWidget.indexOfTopLevelItem(item)
            self.treeWidget.takeTopLevelItem(index)
            del self.packages[package.identifier]

    def newPackage(self, package_identifier, prepend=False):
        # prepend places at the front of the list of packages,
        # by default adds to the end of the list of packages
        # Right now the list is sorted so prepend has no effect
        if package_identifier in self.packages:
            return self.packages[package_identifier]
        registry = get_module_registry()
        package_name = registry.packages[package_identifier].name
        package_item = QPackageTreeWidgetItem(None,
                                              package_name, package_identifier)
        self.packages[package_identifier] = package_item
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
                package_item = self.packages[package_identifier]

            if descriptor.ghost_namespace is not None:
                namespace = descriptor.ghost_namespace
            else:
                namespace = descriptor.namespace
            if descriptor.namespace_hidden or not namespace:
                parent_item = package_item
            else:
                parent_item = \
                    package_item.get_namespace(namespace.split('|'))

            item = QModuleTreeWidgetItem(descriptor, parent_item,
                                         [descriptor.name],
                                         descriptor.is_hidden)
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

        self.treeWidget.setSortingEnabled(False)
        registry = get_module_registry()
        for package in registry.package_list:
            self.newPackage(package.identifier)
        self.newModule(registry.root_descriptor, True)
        self.treeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treeWidget.setSortingEnabled(True)

    def sizeHint(self):
        return QtCore.QSize(256, 760)

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
        if item and item.parent() is None:
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
            assert isinstance(p, QPackageTreeWidgetItem)
            identifier = p.identifier
            registry = get_module_registry()
            package = registry.packages[identifier]
            try:
                if package.has_context_menu():
                    if isinstance(item, QPackageTreeWidgetItem):
                        text = None
                    elif isinstance(item, QNamespaceTreeWidgetItem):
                        return  # no context menu for namespaces
                    elif isinstance(item, QModuleTreeWidgetItem):
                        text = item.descriptor.name
                        if item.descriptor.namespace:
                            text = '%s|%s' % (item.descriptor.namespace, text)
                    else:
                        assert False, "fell through"
                    menu_items = package.context_menu(text)
                    if menu_items:
                        menu = QtGui.QMenu(self)
                        for text, callback in menu_items:
                            act = QtGui.QAction(text, self)
                            act.setStatusTip(text)
                            QtCore.QObject.connect(act,
                                                   QtCore.SIGNAL("triggered()"),
                                                   callback)
                            menu.addAction(act)
                        menu.exec_(event.globalPos())
                    return
            except Exception, e:
                debug.unexpected_exception(e)
                debug.warning("Got exception trying to display %s's "
                              "context menu in the palette: %s\n%s" % (
                                  package.name,
                                  debug.format_exception(e),
                                  traceback.format_exc()))

            item.contextMenuEvent(event, self)

    def startDrag(self, actions):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            mime_data = self.model().mimeData(indexes)
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            item = mime_data.items[0]

            app = get_vistrails_application()
            pipeline_view = app.builderWindow.get_current_controller().current_pipeline_view
            if hasattr(pipeline_view.scene(), 'add_tmp_module'):
                module_item = \
                    pipeline_view.scene().add_tmp_module(item.descriptor)
                pixmap = pipeline_view.paintModuleToPixmap(module_item)

                drag.setPixmap(pixmap)
                drag.setHotSpot(QtCore.QPoint(pixmap.width()/2,
                                              pixmap.height()/2))
                drag.exec_(actions)
                pipeline_view.scene().delete_tmp_module()


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
        self.isMac = systemType == 'Darwin'

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
                           QtCore.Qt.DisplayRole),
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

    def __init__(self, descriptor, parent, labelList, is_hidden):
        """ QModuleTreeWidgetItem(descriptor: ModuleDescriptor
                                    (or None for top-level),
                                  parent: QTreeWidgetItem
                                  labelList: string)
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

        self.is_hidden = is_hidden

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
        menu = QtGui.QMenu(widget)
        act = QtGui.QAction("View Documentation", widget)
        act.setStatusTip("View module documentation")
        QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.view_documentation)
        menu.addAction(act)
        if self.descriptor.package == 'local.abstractions':
            act = QtGui.QAction("Edit Subworkflow", widget)
            act.setStatusTip("Edit this Subworkflow")
            QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.edit_subworkflow)
            menu.addAction(act)
            act = QtGui.QAction("Remove Subworkflow", widget)
            act.setStatusTip("Delete this Subworkflow")
            QtCore.QObject.connect(act,
                               QtCore.SIGNAL("triggered()"),
                               self.remove_subworkflow)
            menu.addAction(act)
        menu.exec_(event.globalPos())

    def view_documentation(self):
        from vistrails_window import _app
        _app.show_documentation()
        widget = QModuleDocumentation.instance()
        widget.update_descriptor(self.descriptor)

    def edit_subworkflow(self):
        from vistrails_window import _app
        filename = self.descriptor.module.vt_fname
        _app.openAbstraction(filename)

    def remove_subworkflow(self):
        registry = get_module_registry()
        res = QtGui.QMessageBox.question(None,
                  'Delete subworkflow?',
                  'Remove local subworkflow "%s" and delete from disk?' % self.descriptor.name,
                  buttons=QtGui.QMessageBox.Yes,
                  defaultButton=QtGui.QMessageBox.No)
        if res == QtGui.QMessageBox.Yes:
            os.unlink(self.descriptor.module.vt_fname)
            registry.delete_module(*self.descriptor.spec_tuple)

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor
        if descriptor:
            descriptor.set_widget(self)

class QNamespaceTreeWidgetItem(QModuleTreeWidgetItem):
    def __init__(self, parent, name):
        QModuleTreeWidgetItem.__init__(self, None, parent, [name], False)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDragEnabled)
        self.namespaces = {}

    def get_namespace(self, namespace_items):
        if len(namespace_items) <= 0:
            return self
        namespace_item = namespace_items.pop(0)
        if namespace_item in self.namespaces and self.namespaces[namespace_item]:
            item = self.namespaces[namespace_item]
        else:
            item = QNamespaceTreeWidgetItem(self, namespace_item)
            self.namespaces[namespace_item] = item
        return item.get_namespace(namespace_items)

    def takeChild(self, index):
        child = self.child(index)
        if child.text(0) in self.namespaces:
            del self.namespaces[child.text(0)]
        QModuleTreeWidgetItem.takeChild(self, index)
        if self.childCount() < 1 and self.parent():
            self.parent().takeChild(self.parent().indexOfChild(self))

class QPackageTreeWidgetItem(QNamespaceTreeWidgetItem):
    def __init__(self, parent, name, identifier):
        QNamespaceTreeWidgetItem.__init__(self, parent, name)
        self.identifier = identifier
