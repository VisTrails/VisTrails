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

QMethodDocumentation
"""

from PyQt4 import QtCore, QtGui
from core.vistrail.port import PortEndPoint
from core.utils import VistrailsInternalError

class QPortDocumentation(QtGui.QDialog):
    """
    QPortDocumentation is a dialog for showing port documentation. duh.

    """
    def __init__(self, descriptor, port_type, port_name, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.descriptor = descriptor
        self.setModal(True)
        if port_type == 'output':
            call_ = descriptor.module.provide_output_port_documentation
        elif port_type == 'input':
            call_ = descriptor.module.provide_input_port_documentation
        else:
            raise VistrailsInternalError("Invalid port type")
        self.setWindowTitle('Documentation for %s port %s in "%s"' %
                            (port_type, port_name, descriptor.name))
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addStrut(600)
        self.layout().addWidget(QtGui.QLabel("Port name: %s" % port_name))
        self.layout().addWidget(QtGui.QLabel("Module name: %s" % descriptor.name))
        package = descriptor.module_package()
        self.layout().addWidget(QtGui.QLabel("Module package: %s" % package))
        self.closeButton = QtGui.QPushButton('Ok', self)
        self.textEdit = QtGui.QTextEdit(self)
        self.layout().addWidget(self.textEdit, 1)
        doc = call_(port_name)
        if doc:
            self.textEdit.insertPlainText(doc)
        else:
            self.textEdit.insertPlainText("Documentation not available.")
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextCursor(QtGui.QTextCursor(self.textEdit.document()))
        self.layout().addWidget(self.closeButton)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked(bool)'), self.close)
        self.closeButton.setShortcut('Enter')
