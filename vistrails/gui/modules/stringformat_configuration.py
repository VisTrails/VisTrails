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

from __future__ import division

from PyQt4 import QtCore, QtGui

from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget


class StringFormatConfigurationWidget(StandardModuleConfigurationWidget):
    """
    Configuration widget creating the ports corresponding to the format.

    """
    def __init__(self, module, controller, parent=None):
        """ StringFormatConfigurationWidget(
                module: Module,
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
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Give it a nice window title
        self.setWindowTitle("StringFormat Configuration")

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)

        # Add the configuration button
        self.button = QtGui.QPushButton("Sync ports")
        self.connect(self.button, QtCore.SIGNAL('clicked()'),
                     self.saveTriggered)
        centralLayout.addWidget(self.button)

    def activate(self):
        self.button.focusWidget(QtCore.Qt.ActiveWindowFocusReason)

    def saveTriggered(self, checked = False):
        """ saveTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok

        """
        if self.updateVistrail():
            self.emit(QtCore.SIGNAL('stateChanged'))
            self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)

    def get_format(self):
        for i in xrange(self.module.getNumFunctions()):
            func = self.module.functions[i]
            if func.name == 'format':
                return func.params[0].strValue
        else:
            return ''

    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table

        """
        from vistrails.core.modules.basic_modules import StringFormat
        args, kwargs = StringFormat.list_placeholders(self.get_format())
        wanted_ports = set('_%d' % n for n in xrange(args)) | kwargs

        current_ports = set(port_spec.name
                            for port_spec in self.module.input_port_specs)

        sigstring = '(org.vistrails.vistrails.basic:Variant)'
        add_ports = [('input', n, sigstring, -1)
                     for n in (wanted_ports - current_ports)]
        delete_ports = [('input', n)
                        for n in (current_ports - wanted_ports)]

        self.controller.update_ports(self.module.id, delete_ports, add_ports)

        return True
