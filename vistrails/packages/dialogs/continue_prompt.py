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

from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.modules import basic_modules
from vistrails.core.modules.vistrails_module import Module, ModuleError

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellContainer


class PromptWindow(QtGui.QDialog):
    def __init__(self, widget, label=None):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("Check intermediate results")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(widget)
        if label is not None:
            self.layout().addWidget(QtGui.QLabel(label))
        buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Yes | QtGui.QDialogButtonBox.No)
        self.connect(buttons, QtCore.SIGNAL('accepted()'),
                     self, QtCore.SLOT('accept()'))
        self.connect(buttons, QtCore.SIGNAL('rejected()'),
                     self, QtCore.SLOT('reject()'))
        self.layout().addWidget(buttons)


class PromptIsOkay(Module):
    _input_ports = [('label', basic_modules.String,
                     {'optional': True}),
                    ('carry_on', basic_modules.Boolean,
                     {'optional': True, 'defaults': "['False']"}),
                    ('cell', SpreadsheetCell)]
    _output_ports = [('result', basic_modules.Boolean)]

    def compute(self):
        vt_configuration = get_vistrails_configuration()
        if not getattr(vt_configuration, 'interactiveMode', False):
            self.set_output('result', True)
            return

        cell = self.get_input('cell')
        label = self.force_get_input('label', None)

        # FIXME : This should be done via the spreadsheet, removing it properly
        # and then sending a new DisplayCellEvent
        # However, there is currently no facility to remove the widget from
        # wherever it is
        oldparent = cell.parent()
        assert isinstance(oldparent, QCellContainer)
        ncell = oldparent.takeWidget()
        assert ncell == cell
        dialog = PromptWindow(cell, label)
        result = dialog.exec_() == QtGui.QDialog.Accepted
        oldparent.setWidget(cell)

        self.set_output('result', result)

        if not result and not self.get_input('carry_on'):
            raise ModuleError(self, "Execution aborted")


_modules = [PromptIsOkay]
