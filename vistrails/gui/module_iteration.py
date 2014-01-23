###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
    VisTrails module is looped.

QModuleIteration
"""
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.module_registry import ModuleRegistryException
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

LOOP_KEY = '__loop_type__'

class QModuleIteration(QtGui.QDialog, QVistrailsPaletteInterface):
    """
    QModuleIteration is a dialog for editing module looping options.

    """
    def __init__(self, parent=None):
        """ 
        QModuleIteration(parent)
        -> None

        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Module Looping")
        self.setLayout(QtGui.QVBoxLayout())
        # self.layout().addStrut()
        layout = QtGui.QHBoxLayout()
        type_group = QtGui.QButtonGroup(self) # Number group
        layout.addWidget(QtGui.QLabel("Looping method:"))
        self.pairwiseButton = QtGui.QRadioButton("Pairwise")
        self.pairwiseButton.setToolTip("Execute multiple looped input ports pairwise:"
                                       " [(A, B), (C, D)] -> [(A, C), (B, D)]")
        self.pairwiseButton.setChecked(True)
        self.pairwiseButton.toggled.connect(self.stateChanged)
        type_group.addButton(self.pairwiseButton)
        layout.addWidget(self.pairwiseButton)
        layout.setStretch(0, 0)
        self.controller = None
        self.state_changed = False
        self.module = None
        self.cartesianButton = QtGui.QRadioButton("Cartesian")
        self.cartesianButton.setToolTip("Execute multiple looped input ports using cartesian product:"
                                       " [(A, B), (C, D)] -> [(A, C), (A, D), (B, C), (B, D)]")
        self.cartesianButton.toggled.connect(self.stateChanged)
        type_group.addButton(self.cartesianButton)
        layout.addWidget(self.cartesianButton)
        layout.setStretch(1, 0)
        layout.addStretch(1)
        #layout.addStretch(1)
        self.layout().addLayout(layout)
        self.layout().setStretch(0, 0)
        self.layout().addStretch(1)
        self.createButtons()
        self.update_module()

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
        self.layout().setStretch(2, 0)
        self.update_module()

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
        self.update_module(self.module)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)

    def stateChanged(self, state=False):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        self.state_changed = True
    
    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()

    def set_controller(self, controller):
        self.controller = controller
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
            return
        self.pairwiseButton.setEnabled(True)
        self.pairwiseButton.setChecked(True)
        self.cartesianButton.setEnabled(True)
        if module.has_annotation_with_key(LOOP_KEY):
            type = module.get_annotation_by_key(LOOP_KEY).value
            self.pairwiseButton.setChecked(type=='pairwise')
            self.cartesianButton.setChecked(type=='cartesian')

    def updateVistrail(self):
        type = 'pairwise' if self.pairwiseButton.isChecked() else 'cartesian'
        if self.module.has_annotation_with_key(LOOP_KEY):
            self.controller.delete_annotation(LOOP_KEY, self.module.id)
        self.controller.add_annotation((LOOP_KEY, type), self.module.id)
        return True

    def activate(self):
        if self.isVisible() == False:
            self.show()
        self.activateWindow()
