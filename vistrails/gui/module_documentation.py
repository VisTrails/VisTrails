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
    def __init__(self, descriptor, parent=None):
        """ 
        QModuleAnnotation(descriptor: ModuleDescriptor, parent)
        -> None

        """
        QtGui.QDialog.__init__(self, parent)
        # self.setModal(True)
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
            self.setWindowTitle("Module Documentation")
            self.name_label.setText("Module name:")
            self.package_label.setText("Module package:")
            self.textEdit.setText("")
        else:
            self.setWindowTitle('%s Documentation' % descriptor.name)

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
