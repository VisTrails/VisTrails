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

from vistrails.core.modules import basic_modules
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.packagemanager import get_package_manager
from PyQt4 import QtGui


class Dialog(Module):
    _input_ports = [('title', basic_modules.String,
                     {'optional': True}),
                    ('cacheable', basic_modules.Boolean,
                     {'optional': True, 'defaults': "['False']"})]

    cacheable_dialog = False

    def is_cacheable(self):
        return self.cacheable_dialog


class TextDialog(Dialog):
    _input_ports = [('label', basic_modules.String,
                     {'optional': True, 'defaults': "['']"}),
                    ('default', basic_modules.String,
                     {'optional': True, 'defaults': "['']"})]
    _output_ports = [('result', basic_modules.String)]

    mode = QtGui.QLineEdit.Normal

    def compute(self):
        if self.has_input('title'):
            title = self.get_input('title')
        else:
            title = 'VisTrails Dialog'
        label = self.get_input('label')

        default = self.get_input('default')

        self.cacheable_dialog = self.get_input('cacheable')

        (result, ok) = QtGui.QInputDialog.getText(None, title, label,
                                                  self.mode,
                                                  default)
        if not ok:
            raise ModuleError(self, "Canceled")
        self.set_output('result', str(result))


class PasswordDialog(TextDialog):
    _input_ports = [('label', basic_modules.String,
                     {'optional': True, 'defaults': "['Password']"})]

    mode = QtGui.QLineEdit.Password


class YesNoDialog(Dialog):
    _input_ports = [('label', basic_modules.String,
                     {'optional': True, 'defaults': "['Yes/No?']"})]
    _output_ports = [('result', basic_modules.Boolean)]

    def compute(self):
        if self.has_input('title'):
            title = self.get_input('title')
        else:
            title = 'VisTrails Dialog'
        label = self.get_input('label')

        self.cacheable_dialog = self.get_input('cacheable')

        result = QtGui.QMessageBox.question(
                None,
                title, label,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        result = result == QtGui.QMessageBox.Yes

        self.set_output('result', result)


_modules = [(Dialog, {'abstract': True}),
            TextDialog, PasswordDialog,
            YesNoDialog]


pm = get_package_manager()
if pm.has_package('org.vistrails.vistrails.spreadsheet'):
    from .continue_prompt import _modules as continue_modules
    _modules.extend(continue_modules)
