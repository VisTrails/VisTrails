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
""" This file contains a dialog and widgets related to the module documentation
dialog, which displays the available documentation for a given VisTrails module.

QMethodDocumentation
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.vistrail.port import PortEndPoint
from vistrails.core.utils import VistrailsInternalError

class QPortDocumentation(QtGui.QDialog):
    """
    QPortDocumentation is a dialog for showing port documentation. duh.

    """
    def __init__(self, module, port_type, port_name, parent=None):
        QtGui.QDialog.__init__(self, parent)

        if not module.has_port_spec(port_name, port_type):
            doc = None
        else:
            port_spec = module.get_port_spec(port_name, port_type)
            doc = port_spec.docstring()
            if doc is None:
                descriptor = module.module_descriptor
                # try the old method of accessing documentation
                if port_type == 'output':
                    call_ = descriptor.module.provide_output_port_documentation
                elif port_type == 'input':
                    call_ = descriptor.module.provide_input_port_documentation
                else:
                    raise VistrailsInternalError("Invalid port type")
                doc = call_(port_name)
                
        self.setWindowTitle('Documentation for %s port %s in "%s"' %
                            (port_type, port_name, module.name))


        layout = QtGui.QVBoxLayout()
        layout.addStrut(600)
        layout.addWidget(QtGui.QLabel("Port name: %s" % port_name))
        layout.addWidget(QtGui.QLabel("Module name: %s" % module.name))
        layout.addWidget(QtGui.QLabel("Module package: %s" % \
                                                 module.package))
        self.textEdit = QtGui.QTextEdit(self)
        layout.addWidget(self.textEdit, 1)
        if doc:
            self.textEdit.insertPlainText(doc)
        else:
            self.textEdit.insertPlainText("(Documentation not available)")
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextCursor(QtGui.QTextCursor(self.textEdit.document()))
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
