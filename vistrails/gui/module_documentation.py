###############################################################################
##
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
""" This file contains a dialog and widgets related to the module documentation
dialog, which displays the available documentation for a given VisTrails module.

QModuleDocumentation
"""

from PyQt4 import QtCore, QtGui
from gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

class QModuleDocumentation(QtGui.QDialog, QVistrailsPaletteInterface):
    """
    QModuleDocumentation is a dialog for showing module documentation. duh.

    """
    def __init__(self, parent=None):
        """ 
        QModuleAnnotation(parent)
        -> None

        """
        QtGui.QDialog.__init__(self, parent)
        # self.setModal(True)
        self.setWindowTitle("Module Documentation")
        self.setLayout(QtGui.QVBoxLayout())
        # self.layout().addStrut()
        self.name_label = QtGui.QLabel("")
        self.layout().addWidget(self.name_label)
        self.package_label = QtGui.QLabel("")
        self.layout().addWidget(self.package_label)
        # self.closeButton = QtGui.QPushButton('Ok', self)
        self.textEdit = QtGui.QTextEdit(self)
        self.layout().addWidget(self.textEdit, 1)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextCursor(QtGui.QTextCursor(self.textEdit.document()))
        # self.layout().addWidget(self.closeButton)
        # self.connect(self.closeButton, QtCore.SIGNAL('clicked(bool)'), 
        #              self.close)
        # self.closeButton.setShortcut('Enter')

        self.update_descriptor()

    def set_controller(self, controller):
        scene = controller.current_pipeline_view
        selected_ids = scene.get_selected_module_ids() 
        modules = [controller.current_pipeline.modules[i] 
                   for i in selected_ids]
        if len(modules) == 1:
            self.update_module(modules[0])
        else:
            self.update_module(None)

    def update_module(self, module=None):
        if module and module.module_descriptor:
            self.update_descriptor(module.module_descriptor)
        else:
            self.update_descriptor(None)

    def update_descriptor(self, descriptor=None):
        self.descriptor = descriptor
        if descriptor is None:
            # self.setWindowTitle("Module Documentation")
            self.name_label.setText("Module name:")
            self.package_label.setText("Module package:")
            self.textEdit.setText("")
        else:
            # self.setWindowTitle('%s Documentation' % descriptor.name)
            self.name_label.setText("Module name: %s" % descriptor.name)
            self.package_label.setText("Module package: %s" % \
                                           descriptor.module_package())
            if descriptor.module.__doc__:
                self.textEdit.setText(descriptor.module.__doc__)
            else:
                self.textEdit.setText("Documentation not available.")

    def activate(self):
        if self.isVisible() == False:
            self.show()
        self.activateWindow()
