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
""" This file specifies the configuration widget for Tuple
module. This should be used as a template for creating a configuration
for other modules. The widget here should inherit from
vistrails.gui.modules.module_configure.StandardModuleConfigurationWidget,
which is also a QWidget.

"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core import debug
from vistrails.core.utils import VistrailsInternalError
from vistrails.core.modules.module_registry import get_module_registry, \
    ModuleRegistryException
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.core.utils import PortAlreadyExists
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget
from vistrails.gui.utils import show_question, SAVE_BUTTON, DISCARD_BUTTON

############################################################################

class PortTable(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self,1,3,parent)
        horiz = self.horizontalHeader()
        horiz.setMovable(False)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.delegate = PortTableItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.connect(self.model(),
                     QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'),
                     self.handleDataChanged)
        self.connect(self.delegate, QtCore.SIGNAL("modelDataChanged"),
                     self, QtCore.SIGNAL("contentsChanged"))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.setMouseTracking(True)
        #self.mouseOver = False
        
    def sizeHint(self):
        return QtCore.QSize()

    def fixGeometry(self):
        rect = self.visualRect(self.model().index(self.rowCount()-1,
                                                  self.columnCount()-1))
        self.setFixedHeight(self.horizontalHeader().height()+
                            rect.y()+rect.height()+1)

    def handleDataChanged(self, topLeft, bottomRight):
        if topLeft.column()==0:
            text = str(self.model().data(topLeft, QtCore.Qt.DisplayRole))
            changedGeometry = False
            if text!='' and topLeft.row()==self.rowCount()-1:
                self.setRowCount(self.rowCount()+1)
                changedGeometry = True
            if text=='' and topLeft.row()<self.rowCount()-1:
                self.removeRow(topLeft.row())
                changedGeometry = True
            if changedGeometry:
                self.fixGeometry()
            self.emit(QtCore.SIGNAL("contentsChanged"))

    def initializePorts(self, port_specs, reverse_order=False):
        self.disconnect(self.model(),
                        QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'),
                        self.handleDataChanged)
        if reverse_order:
            port_specs_iter = reversed(port_specs)
        else:
            port_specs_iter = port_specs
        for p in port_specs_iter:
            model = self.model()
            sigstring = p.sigstring[1:-1]
            siglist = sigstring.split(':')
            short_name = "%s (%s)" % (siglist[1], siglist[0])
            model.setData(model.index(self.rowCount()-1, 2),
                          p.depth,
                          QtCore.Qt.DisplayRole)
            model.setData(model.index(self.rowCount()-1, 1),
                          sigstring,
                          QtCore.Qt.UserRole)
            model.setData(model.index(self.rowCount()-1, 1),
                          short_name,
                          QtCore.Qt.DisplayRole)
            model.setData(model.index(self.rowCount()-1, 0),
                          p.name,
                          QtCore.Qt.DisplayRole)
            self.setRowCount(self.rowCount()+1)
        self.connect(self.model(),
                     QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'),
                     self.handleDataChanged)
            
    def getPorts(self):
        ports = []
        model = self.model()
        for i in xrange(self.rowCount()):
            name = model.data(model.index(i, 0), QtCore.Qt.DisplayRole)
            sigstring = model.data(model.index(i, 1), QtCore.Qt.UserRole)
            depth = model.data(model.index(i, 2), QtCore.Qt.DisplayRole) or 0
            if name is not None and sigstring is not None:
                ports.append((name, '(%s)' % sigstring, i, depth))
        return ports

#    def focusOutEvent(self, event):
#        if self.parent():
#            QtCore.QCoreApplication.sendEvent(self.parent(), event)
#        QtGui.QTableWidget.focusOutEvent(self, event)


class CompletingComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self._last_good_index = -1

    def select_default_item(self, initial_idx):
        self.setCurrentIndex(initial_idx)
        self._last_good_index = initial_idx

    def validate_input(self):
        invalid = (self.currentIndex() == -1 or
                   self.itemData(self.currentIndex()) == '')
        completion = self.completer().currentCompletion()
        if completion:
            idx = self.findText(completion)
            if idx:
                invalid = False
                self.setCurrentIndex(idx)
        if invalid and self._last_good_index != -1:
            self.setCurrentIndex(self._last_good_index)
        elif invalid:
            self.setEditText('')
        else:
            self._last_good_index = self.currentIndex()
            self.setEditText(self.itemText(self.currentIndex()))


class PortTableItemDelegate(QtGui.QItemDelegate):

    def createEditor(self, parent, option, index):
        registry = get_module_registry()
        if index.column()==2: #Depth type
            spinbox = QtGui.QSpinBox(parent)
            spinbox.setValue(0)
            return spinbox
        elif index.column()==1: #Port type
            combo = CompletingComboBox(parent)
            # FIXME just use descriptors here!!
            variant_desc = registry.get_descriptor_by_name(
                get_vistrails_basic_pkg_id(), 'Variant')
            for _, pkg in sorted(registry.packages.iteritems()):
                pkg_item = QtGui.QStandardItem("----- %s -----" % pkg.name)
                pkg_item.setData('', QtCore.Qt.UserRole)
                pkg_item.setFlags(pkg_item.flags() & ~(
                        QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable))
                font = pkg_item.font()
                font.setBold(True)
                pkg_item.setFont(font)
                combo.model().appendRow(pkg_item)
                for _, descriptor in sorted(pkg.descriptors.iteritems()):
                    if descriptor is variant_desc:
                        variant_index = combo.count()
                    combo.addItem("%s (%s)" % (descriptor.name,
                                               descriptor.identifier),
                                  descriptor.sigstring)

            combo.select_default_item(variant_index)
            return combo
        else:
            return QtGui.QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        if index.column()==2:
            data = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setValue(data or 0)
        elif index.column()==1:
            data = index.model().data(index, QtCore.Qt.UserRole)
            editor.setCurrentIndex(editor.findData(data))
        else:
            QtGui.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column()==2:
            model.setData(index, editor.value() or 0, QtCore.Qt.DisplayRole)
        elif index.column()==1:
            editor.validate_input()
            model.setData(index, editor.itemData(editor.currentIndex()), 
                          QtCore.Qt.UserRole)
            model.setData(index, editor.currentText(), 
                          QtCore.Qt.DisplayRole)
        else:
            QtGui.QItemDelegate.setModelData(self, editor, model, index)
        self.emit(QtCore.SIGNAL("modelDataChanged"))

############################################################################

class PortTableConfigurationWidget(StandardModuleConfigurationWidget):
    """
    PortTableConfigurationWidget is the configuration widget for a
    tuple-like module, we want to build an interface for specifying a
    number of input (output) ports and the type of each port. Then
    compose (decompose) a tuple of those input as a result.

    When subclassing StandardModuleConfigurationWidget, there are
    only two things we need to care about:
    
    1) The builder will provide the VistrailController (through the
       constructor) associated with the pipeline the module is in. The
       configuration widget can use the controller to change the
       current vistrail such as delete connections, add/delete module
       port...

    2) The builder also provide the current Module object (through the
       constructor) of the module. This is the instance of the module
       in the pipeline. Changes to this Module object usually will not
       result a new version in the current Vistrail. Such changes are
       change the visibility of input/output ports on the builder,
       change module color.

       Each module has a local set of input and output ports that may
       change, unlike those stored by the global registry. The same
       module can have different types of input ports at two different
       time in the same vistrail.

    That's it, the rest of the widget will be just like a regular Qt
    widget.
    
    """
    def __init__(self, module, controller, parent=None):
        """ PortTableConfigurationWidget(module: Module,
                                         controller: VistrailController,
                                         parent: QWidget)
                                         -> PortTableConfigurationWidget                                       
        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.        
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        self.module : the Module object int the pipeline        
        self.controller: the current vistrail controller
                                       
        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

    def updateVistrail(self):
        msg = "Must implement updateVistrail in subclass"
        raise VistrailsInternalError(msg)

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button
        
        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.saveButton = QtGui.QPushButton('&Save', self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        self.buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton('&Reset', self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        self.buttonLayout.addWidget(self.resetButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'),
                     self.saveTriggered)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked(bool)'),
                     self.resetTriggered)        

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window
        
        """
        return QtCore.QSize(512, 256)

    def saveTriggered(self, checked = False):
        """ saveTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok
        
        """
        if self.updateVistrail():
            self.saveButton.setEnabled(False)
            self.resetButton.setEnabled(False)
            self.state_changed = False
            self.emit(QtCore.SIGNAL("stateChanged"))
            self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)
            
    def resetTriggered(self, checked = False):
        self.state_changed = False
    
    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()
        
    def getRegistryPorts(self, registry, type):
        if not registry:
            return []
        if type == 'input':
            getter = registry.destination_ports_from_descriptor
        elif type == 'output':
            getter = registry.source_ports_from_descriptor
        else:
            raise VistrailsInternalError("Unrecognized port type '%s'", type)

        ports = []
        try:
            ports = [(p.name, p.sigstring) 
                     for p in getter(self.module.module_descriptor)] 
        except ModuleRegistryException:
            pass
        return ports
        
    def registryChanges(self, old_ports, new_ports):
        deleted_ports = [p for p in old_ports if p not in new_ports]
        added_ports = [p for p in new_ports if p not in old_ports]
        return (deleted_ports, added_ports)
    
    def getPortDiff(self, p_type, port_table):
        if p_type == 'input':
            old_ports = [(p.name, p.sigstring, p.sort_key, p.depth)
                         for p in self.module.input_port_specs]
        elif p_type == 'output':
            old_ports = [(p.name, p.sigstring, p.sort_key, p.depth) 
                         for p in self.module.output_port_specs]
        else:
            old_ports = []
        # old_ports = self.getRegistryPorts(self.module.registry, p_type)
        new_ports = port_table.getPorts()
        (deleted_ports, added_ports) = \
            self.registryChanges(old_ports, new_ports)
        deleted_ports = [(p_type,) + p for p in deleted_ports]
        added_ports = [(p_type,) + p for p in added_ports]
        return (deleted_ports, added_ports)
    
class TupleConfigurationWidget(PortTableConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        """ TupleConfigurationWidget(module: Module,
                                     controller: VistrailController,
                                     parent: QWidget)
                                     -> TupleConfigurationWidget

        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.        
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        self.module : the Module object int the pipeline        
        self.controller: the current vistrail controller
                                       
        """
        PortTableConfigurationWidget.__init__(self, module,
                                              controller, parent)

        # Give it a nice window title
        self.setWindowTitle('Tuple Configuration')

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)
        
        # Then add a PortTable to our configuration widget
        self.portTable = PortTable(self)
        self.portTable.setHorizontalHeaderLabels(
            ['Input Port Name', 'Type', 'List Depth'])

        # We know that the Tuple module initially doesn't have any
        # input port, we just use the local registry to see what ports
        # it has at the time of configuration.
        self.portTable.initializePorts(self.module.input_port_specs)
        self.portTable.fixGeometry()
        centralLayout.addWidget(self.portTable)

        horiz = self.portTable.horizontalHeader()
        horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.portTable.resizeColumnToContents(0)
        self.portTable.resizeColumnToContents(2)

        # We need a padded widget to take all vertical white space away
        paddedWidget = QtGui.QWidget(self)
        paddedWidget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                   QtGui.QSizePolicy.Expanding)
        centralLayout.addWidget(paddedWidget, 1)

        # Then we definitely need a Save & Reset button
        self.createButtons()
        
        #Connect signals
        self.connect(self.portTable, QtCore.SIGNAL("contentsChanged"),
                     self.updateState)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.setMouseTracking(True)
        #self.mouseOver = False
#        
#    def enterEvent(self, event):
#        self.mouseOver = True
#        
#    def leaveEvent(self, event):
#        self.mouseOver = False
        

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table
        
        """
        (deleted_ports, added_ports) = self.getPortDiff('input', self.portTable)
        if len(deleted_ports) + len(added_ports) == 0:
            # nothing changed
            return
        current_ports = self.portTable.getPorts()
        # note that the sigstring and sort_key for deletion doesn't matter
        deleted_ports.append(('output', 'value'))
        if len(current_ports) > 0:
            spec = "(" + ','.join(p[1][1:-1] for p in current_ports) + ")"
            added_ports.append(('output', 'value', spec, -1))
        try:
            self.controller.update_ports(self.module.id, deleted_ports, 
                                         added_ports)
        except PortAlreadyExists, e:
            debug.critical('Port Already Exists %s' % str(e))
            return False
        return True            
    
    def resetTriggered(self, checked = False):
        self.portTable.clearContents()
        self.portTable.setRowCount(1)
        self.portTable.initializePorts(self.module.input_port_specs)
        self.portTable.fixGeometry()
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL("stateChanged"))

    def updateState(self):
        if not self.hasFocus():
            self.setFocus(QtCore.Qt.TabFocusReason)
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL("stateChanged"))
            
#    def focusOutEvent(self, event):
        #if not self.mouseOver:
        #    self.askToSaveChanges()
#        QtGui.QWidget.focusOutEvent(self, event)
                
class UntupleConfigurationWidget(PortTableConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        """ UntupleConfigurationWidget(module: Module,
                                     controller: VistrailController,
                                     parent: QWidget)
                                     -> UntupleConfigurationWidget                                       
        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.        
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        self.module : the Module object int the pipeline        
        self.controller: the current vistrail controller
                                       
        """
        PortTableConfigurationWidget.__init__(self, module,
                                              controller, parent)

        # Give it a nice window title
        self.setWindowTitle('Untuple Configuration')

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)
        
        # Then add a PortTable to our configuration widget
        self.portTable = PortTable(self)
        self.portTable.setHorizontalHeaderLabels(
            ['Output Port Name', 'Type', 'List Depth'])
        
        # We know that the Tuple module initially doesn't have any
        # input port, we just use the local registry to see what ports
        # it has at the time of configuration.
        self.portTable.initializePorts(self.module.output_port_specs, True)
        self.portTable.fixGeometry()
        centralLayout.addWidget(self.portTable)

        # We need a padded widget to take all vertical white space away
        paddedWidget = QtGui.QWidget(self)
        paddedWidget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                   QtGui.QSizePolicy.Expanding)
        centralLayout.addWidget(paddedWidget, 1)

        horiz = self.portTable.horizontalHeader()
        horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.portTable.resizeColumnToContents(0)
        self.portTable.resizeColumnToContents(2)

        # Then we definitely need a Save & Reset button
        self.createButtons()
        
        #Connect signals
        self.connect(self.portTable, QtCore.SIGNAL("contentsChanged"),
                     self.updateState)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.setMouseTracking(True)
        #self.mouseOver = False
        
    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table
        
        """
        (deleted_ports, added_ports) = self.getPortDiff('output', 
                                                        self.portTable)
        if len(deleted_ports) + len(added_ports) == 0:
            # nothing changed
            return
        current_ports = self.portTable.getPorts()
        # note that the sigstring for deletion doesn't matter
        deleted_ports.append(('input', 'value'))
        if len(current_ports) > 0:
            spec = "(" + ','.join(p[1][1:-1] for p in current_ports) + ")"
            added_ports.append(('input', 'value', spec, -1))
        try:
            self.controller.update_ports(self.module.id, deleted_ports, 
                                         added_ports)
        except PortAlreadyExists, e:
            debug.critical('Port Already Exists %s' % e)
            return False
        return True

    def updateState(self):
        if not self.hasFocus():
            self.setFocus(QtCore.Qt.TabFocusReason)
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL("stateChanged"))
            
#    def focusOutEvent(self, event):
#        #if not self.mouseOver:
#        #    self.askToSaveChanges()
#        QtGui.QWidget.focusOutEvent(self, event)
#        
#    def enterEvent(self, event):
#        self.mouseOver = True
#        
#    def leaveEvent(self, event):
#        self.mouseOver = False
    
    def resetTriggered(self, checked = False):
        self.portTable.clearContents()
        self.portTable.setRowCount(1)
        self.portTable.initializePorts(self.module.input_port_specs)
        self.portTable.fixGeometry()
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL("stateChanged"))
