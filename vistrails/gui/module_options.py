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
""" This file contains a dialog for editing options for how the given
    VisTrails module is executed.

QModuleOptions
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

import json
import unittest

###############################################################################

class QModuleOptions(QtGui.QDialog, QVistrailsPaletteInterface):
    """
    QModuleIteration is a dialog for editing module looping options.

    """
    def __init__(self, parent=None):
        """ 
        QModuleIteration(parent)
        -> None

        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Module Execution Options")
        self.createButtons()
        self.update_module()

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button
        
        """
        self.controller = None
        self.state_changed = False
        self.module = None
        self.setLayout(QtGui.QVBoxLayout())
        # self.layout().addStrut()
        layout = QtGui.QHBoxLayout()
        type_group = QtGui.QButtonGroup(self) # Number group
        layout.addWidget(QtGui.QLabel("Port list combination method:"))
        self.pairwiseButton = QtGui.QRadioButton("Pairwise")
        self.pairwiseButton.setToolTip("Execute multiple looped input ports pairwise:"
                                       " [(A, B), (C, D)] -> [(A, C), (B, D)]")
        type_group.addButton(self.pairwiseButton)
        layout.addWidget(self.pairwiseButton)
        layout.setStretch(0, 0)
        self.cartesianButton = QtGui.QRadioButton("Cartesian")
        self.cartesianButton.setToolTip("Execute multiple looped input ports using cartesian product:"
                                       " [(A, B), (C, D)] -> [(A, C), (A, D), (B, C), (B, D)]")
        self.cartesianButton.setChecked(True)
        type_group.addButton(self.cartesianButton)
        layout.addWidget(self.cartesianButton)
        layout.setStretch(1, 0)
        self.customButton = QtGui.QRadioButton("Custom")
        self.customButton.setToolTip("Build a custom combination using pairwise/cartesian functions")
        type_group.addButton(self.customButton)
        layout.addWidget(self.customButton)
        layout.setStretch(2, 0)
        layout.addStretch(1)
        self.layout().addLayout(layout)
        self.layout().setStretch(0, 0)

        self.portCombiner = QPortCombineTreeWidget()
        self.layout().addWidget(self.portCombiner)
        self.portCombiner.setVisible(False)
        
        whileLayout = QtGui.QVBoxLayout()

        self.whileButton = QtGui.QCheckBox("While Loop")
        self.whileButton.setToolTip('Repeatedly execute module until a specified output port has a false value')
        whileLayout.addWidget(self.whileButton)
        whileLayout.setStretch(0, 0)

        layout = QtGui.QHBoxLayout()
        self.condLabel = QtGui.QLabel("Condition output port:")
        layout.addWidget(self.condLabel)
        layout.setStretch(0, 0)
        self.condEdit = QtGui.QLineEdit()
        self.condEdit.setToolTip('Name of output port containing the condition of the loop')
        layout.addWidget(self.condEdit)
        layout.setStretch(1, 1)
        whileLayout.addLayout(layout)
        whileLayout.setStretch(1, 0)

        layout = QtGui.QHBoxLayout()
        self.maxLabel = QtGui.QLabel("Max iterations:")
        layout.addWidget(self.maxLabel)
        layout.setStretch(0, 0)
        self.maxEdit = QtGui.QLineEdit()
        self.maxEdit.setValidator(QtGui.QIntValidator())
        self.maxEdit.setToolTip('Fail after this number of iterations have been reached (default=20)')
        layout.addWidget(self.maxEdit)
        layout.setStretch(1, 1)
        whileLayout.addLayout(layout)
        whileLayout.setStretch(2, 0)

        layout = QtGui.QHBoxLayout()
        self.delayLabel = QtGui.QLabel("Delay:")
        layout.addWidget(self.delayLabel)
        layout.setStretch(0, 0)
        self.delayEdit = QtGui.QLineEdit()
        self.delayEdit.setValidator(QtGui.QDoubleValidator(self))
        self.delayEdit.setToolTip('Delay between iterations in fractions of seconds')
        layout.addWidget(self.delayEdit)
        layout.setStretch(1, 1)
        whileLayout.addLayout(layout)
        whileLayout.setStretch(2, 0)

        layout = QtGui.QHBoxLayout()
        self.feedInputLabel = QtGui.QLabel("Feedback Input port:")
        layout.addWidget(self.feedInputLabel)
        layout.setStretch(0, 0)
        self.feedInputEdit = QtGui.QLineEdit()
        self.feedInputEdit.setToolTip('Name of input port to feed the value from last iteration')
        layout.addWidget(self.feedInputEdit)
        layout.setStretch(1, 1)
        whileLayout.addLayout(layout)
        whileLayout.setStretch(3, 0)

        layout = QtGui.QHBoxLayout()
        self.feedOutputLabel = QtGui.QLabel("Feedback Output port:")
        layout.addWidget(self.feedOutputLabel)
        layout.setStretch(0, 0)
        self.feedOutputEdit = QtGui.QLineEdit()
        self.feedOutputEdit.setToolTip('Name of output port to feed to next iteration')
        layout.addWidget(self.feedOutputEdit)
        layout.setStretch(1, 1)
        whileLayout.addLayout(layout)
        whileLayout.setStretch(4, 0)

        whileLayout.addStretch(1)
        self.layout().addLayout(whileLayout)

        self.jobCacheButton = QtGui.QCheckBox("Cache Output Persistently")
        self.jobCacheButton.setToolTip('Cache the module results persistently to disk. (outputs must be constants)')
        self.layout().addWidget(self.jobCacheButton)
        self.layout().setStretch(2, 0)

        self.layout().addStretch(1)
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
        self.layout().setStretch(3, 0)
        self.update_module()
        self.pairwiseButton.toggled.connect(self.stateChanged)
        self.cartesianButton.toggled.connect(self.stateChanged)
        self.customButton.toggled.connect(self.stateChanged)
        self.customButton.toggled.connect(self.customToggled)
        self.portCombiner.itemChanged.connect(self.stateChanged)
        self.whileButton.toggled.connect(self.stateChanged)
        self.whileButton.toggled.connect(self.whileToggled)
        self.condEdit.textChanged.connect(self.stateChanged)
        self.maxEdit.textChanged.connect(self.stateChanged)
        self.delayEdit.textChanged.connect(self.stateChanged)
        self.feedInputEdit.textChanged.connect(self.stateChanged)
        self.feedOutputEdit.textChanged.connect(self.stateChanged)
        self.jobCacheButton.toggled.connect(self.stateChanged)

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
        self.update_module(self.module)

    def stateChanged(self, state=False, other=None):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        self.state_changed = True

    def customToggled(self, state=False):
        self.portCombiner.setVisible(state)

    def whileToggled(self, state=False):
        if state:
            self.condEdit.setVisible(True)
            self.maxEdit.setVisible(True)
            self.delayEdit.setVisible(True)
            self.feedInputEdit.setVisible(True)
            self.feedOutputEdit.setVisible(True)
            self.condLabel.setVisible(True)
            self.maxLabel.setVisible(True)
            self.delayLabel.setVisible(True)
            self.feedInputLabel.setVisible(True)
            self.feedOutputLabel.setVisible(True)
            self.condEdit.setText('')
            self.maxEdit.setText('')
            self.delayEdit.setText('')
            self.feedInputEdit.setText('')
            self.feedOutputEdit.setText('')
        else:
            self.condEdit.setVisible(False)
            self.maxEdit.setVisible(False)
            self.delayEdit.setVisible(False)
            self.feedInputEdit.setVisible(False)
            self.feedOutputEdit.setVisible(False)
            self.condLabel.setVisible(False)
            self.maxLabel.setVisible(False)
            self.delayLabel.setVisible(False)
            self.feedInputLabel.setVisible(False)
            self.feedOutputLabel.setVisible(False)
    
    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()

    def set_controller(self, controller):
        self.controller = controller
        if not controller:
            return
        scene = controller.current_pipeline_scene
        selected_ids = scene.get_selected_module_ids() 
        modules = [controller.current_pipeline.modules[i] 
                   for i in selected_ids]
        if len(modules) == 1:
            self.update_module(modules[0])
        else:
            self.update_module(None)

    def update_module(self, module=None):
        self.module = module
        if not module:
            self.pairwiseButton.setEnabled(False)
            self.cartesianButton.setEnabled(False)
            self.customButton.setEnabled(False)
            self.whileButton.setEnabled(False)
            self.condEdit.setVisible(False)
            self.maxEdit.setVisible(False)
            self.delayEdit.setVisible(False)
            self.feedInputEdit.setVisible(False)
            self.feedOutputEdit.setVisible(False)
            self.condLabel.setVisible(False)
            self.maxLabel.setVisible(False)
            self.delayLabel.setVisible(False)
            self.feedInputLabel.setVisible(False)
            self.feedOutputLabel.setVisible(False)
            self.portCombiner.setVisible(False)
            self.jobCacheButton.setEnabled(False)
            self.state_changed = False
            self.saveButton.setEnabled(False)
            self.resetButton.setEnabled(False)
            return
        # set defaults
        self.pairwiseButton.setEnabled(True)
        self.cartesianButton.setEnabled(True)
        self.cartesianButton.setChecked(True)
        self.customButton.setEnabled(True)

        self.whileButton.setEnabled(True)
        self.whileButton.setChecked(False)
        self.condEdit.setVisible(False)
        self.maxEdit.setVisible(False)
        self.delayEdit.setVisible(False)
        self.feedInputEdit.setVisible(False)
        self.feedOutputEdit.setVisible(False)
        self.condLabel.setVisible(False)
        self.maxLabel.setVisible(False)
        self.delayLabel.setVisible(False)
        self.feedInputLabel.setVisible(False)
        self.feedOutputLabel.setVisible(False)
        self.portCombiner.setVisible(False)
        self.portCombiner.setDefault(module)
        self.jobCacheButton.setEnabled(True)
        self.jobCacheButton.setChecked(False)
        if module.has_control_parameter_with_name(ModuleControlParam.LOOP_KEY):
            type = module.get_control_parameter_by_name(ModuleControlParam.LOOP_KEY).value
            self.pairwiseButton.setChecked(type=='pairwise')
            self.cartesianButton.setChecked(type=='cartesian')
            self.customButton.setChecked(type not in ['pairwise', 'cartesian'])
            self.portCombiner.setVisible(type not in ['pairwise', 'cartesian'])
            if type not in ['pairwise', 'cartesian']:
                self.portCombiner.setValue(type)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_COND_KEY) or \
           module.has_control_parameter_with_name(ModuleControlParam.WHILE_MAX_KEY):
            self.whileButton.setChecked(True)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_COND_KEY):
            cond = module.get_control_parameter_by_name(ModuleControlParam.WHILE_COND_KEY).value
            self.condEdit.setText(cond)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_MAX_KEY):
            max = module.get_control_parameter_by_name(ModuleControlParam.WHILE_MAX_KEY).value
            self.maxEdit.setText(max)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_DELAY_KEY):
            delay = module.get_control_parameter_by_name(ModuleControlParam.WHILE_DELAY_KEY).value
            self.delayEdit.setText(delay)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_INPUT_KEY):
            input = module.get_control_parameter_by_name(ModuleControlParam.WHILE_INPUT_KEY).value
            self.feedInputEdit.setText(input)
        if module.has_control_parameter_with_name(ModuleControlParam.WHILE_OUTPUT_KEY):
            output = module.get_control_parameter_by_name(ModuleControlParam.WHILE_OUTPUT_KEY).value
            self.feedOutputEdit.setText(output)
        if module.has_control_parameter_with_name(ModuleControlParam.JOB_CACHE_KEY):
            jobCache = module.get_control_parameter_by_name(ModuleControlParam.JOB_CACHE_KEY).value
            self.jobCacheButton.setChecked(jobCache.lower()=='true')
        self.state_changed = False
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)

    def updateVistrail(self):
        values = []
        if self.pairwiseButton.isChecked():
            value = 'pairwise'
        elif self.cartesianButton.isChecked():
            value = 'cartesian'
        else:
            value = self.portCombiner.getValue()
        values.append((ModuleControlParam.LOOP_KEY, value))
        _while = self.whileButton.isChecked()
        values.append((ModuleControlParam.WHILE_COND_KEY,
                       _while and self.condEdit.text()))
        values.append((ModuleControlParam.WHILE_MAX_KEY,
                       _while and self.maxEdit.text()))
        values.append((ModuleControlParam.WHILE_DELAY_KEY,
                       _while and self.delayEdit.text()))
        values.append((ModuleControlParam.WHILE_INPUT_KEY,
                       _while and self.feedInputEdit.text()))
        values.append((ModuleControlParam.WHILE_OUTPUT_KEY,
                       _while and self.feedOutputEdit.text()))
        jobCache = self.jobCacheButton.isChecked()
        values.append((ModuleControlParam.JOB_CACHE_KEY,
                       [False, 'true'][jobCache]))
        for name, value in values:
            if value:
                if (not self.module.has_control_parameter_with_name(name) or
                        value != self.module.get_control_parameter_by_name(name).value):
                    if self.module.has_control_parameter_with_name(name):
                        self.controller.delete_control_parameter(name,
                                                                 self.module.id)
                    self.controller.add_control_parameter((name, value),
                                                          self.module.id)
            elif self.module.has_control_parameter_with_name(name):
                self.controller.delete_control_parameter(name, self.module.id)
        return True

    def activate(self):
        if self.isVisible() == False:
            self.show()
        self.activateWindow()

PORTITEM = 1000
DOTITEM = 1001
CROSSITEM = 1002
class PortItem(QtGui.QTreeWidgetItem):
    def __init__(self, port_name, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, PORTITEM)
        self.setText(0, port_name)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDropEnabled)

class DotItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, DOTITEM)
        self.setExpanded(True)
        self.setIcon(0, CurrentTheme.DOT_PRODUCT_ICON)
        self.setText(0, 'Dot')

class CrossItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, CROSSITEM)
        self.setExpanded(True)
        self.setIcon(0, CurrentTheme.CROSS_PRODUCT_ICON)
        self.setText(0, 'Cross')

class QPortCombineTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.header().hide()
        self.setExpandsOnDoubleClick(False)
        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.expandAll()
        self.setToolTip("Right-click to add dot/cross product. Rearrange "
                        "items to get suitable order. 'Del' key deletes "
                        "selected product.")

    def dropEvent(self, event):
        QtGui.QTreeWidget.dropEvent(self, event)
        self.expandAll()

    def loadNode(self, parent, node):
        # populate widget from json struct
        if isinstance(node, basestring):
            PortItem(node, parent)
        else:
            item = DotItem(parent) if node[0] == 'pairwise' \
                                   else CrossItem(parent)
            for i in node[1:]:
                self.loadNode(item, i)
        
    def saveNode(self, item):
        # populate json struct from widget items
        if item.type()==PORTITEM:
            return item.text(0)
        L = ['pairwise'] if item.type()==DOTITEM else ['cartesian']
        L.extend([self.saveNode(item.child(i))
                  for i in xrange(item.childCount())])
        L = [i for i in L if i is not None]
        if len(L)<2:
            L = None
        return L
    
    def setValue(self, value):
        self.clear()
        value = json.loads(value)
        for v in value[1:]:
            self.loadNode(self.invisibleRootItem(), v)
    
    def getValue(self):
        nodes = [self.topLevelItem(i)
                 for i in xrange(self.topLevelItemCount())]
        L = ['cartesian'] # default
        L.extend([self.saveNode(node) for node in nodes])
        L = [i for i in L if i is not None]
        if len(L)<2:
            L = None
        return json.dumps(L)

    def setDefault(self, module):
        self.clear()
        if not module:
            return
        for port_name in module.iterated_ports:
            PortItem(port_name, self)
            
    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        dotAction = QtGui.QAction(CurrentTheme.DOT_PRODUCT_ICON,
                                  'Add Pairwise Product', self)
        dotAction.triggered.connect(self.addDot)
        menu.addAction(dotAction)
        crossAction = QtGui.QAction(CurrentTheme.CROSS_PRODUCT_ICON,
                                    'Add Cartesian Product', self)
        crossAction.triggered.connect(self.addCross)
        menu.addAction(crossAction)
        menu.exec_(event.globalPos())
        event.accept()

    def addDot(self):
        DotItem(self)

    def addCross(self):
        CrossItem(self)

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Capture 'Del', 'Backspace' for deleting items.
        Ctrl+C, Ctrl+V, Ctrl+A for copy, paste and select all
        
        """
        items = self.selectedItems()
        if (len(items)==1 and \
            event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]) and \
            type(items[0]) in [DotItem, CrossItem] and\
            not items[0].childCount():
            item = items[0]
            if item.parent():
                item.parent().takeChild(item.parent().indexOfChild(item))
            else:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)

class TestIterationGui(unittest.TestCase):
    def testGetSet(self):
        p = QPortCombineTreeWidget()
        v = '["cartesian", ["pairwise", "a", "b"], "c"]'
        p.setValue(v)
        self.assertEqual(v, p.getValue())
