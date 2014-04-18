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

    password = True


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


def handle_module_upgrade_request(controller, module_id, pipeline):
    from vistrails.core.modules.module_registry import get_module_registry
    from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler

    reg = get_module_registry()

    def fix_cell_input(old_conn, new_module):
        """Uses the 'Widget' output port instead of 'self'

        Only works if we are directly connected to a SpreadsheetCell module. If
        using a Group or something funny, the automatic upgrade will fail and
        you'll need to fix the connection yourself.
        """
        # Check that upstream port is 'self'
        if old_conn.source.name != 'self':
            return []

        # Check that upstream module is a SpreadsheetCell subclass
        old_src_module = pipeline.modules[old_conn.source.moduleId]
        # Can't use .module_descriptor here because it references the old
        # package version
        # Here we get the NEW package version, since it might be upgrading as
        # well... let's hope that upgrade doesn't do too much
        cell_desc = reg.get_descriptor_by_name(
                'org.vistrails.vistrails.spreadsheet',
                'SpreadsheetCell')
        desc = reg.get_descriptor_by_name(old_src_module.package,
                                          old_src_module.name,
                                          old_src_module.namespace)
        if not reg.is_descriptor_subclass(desc, cell_desc):
            # Not cool
            return []

        # Create connection to 'Widget' instead of 'self'
        # Here we create a Port object instead of just passing the string
        # 'Widget' because we are setting it on the OLD module -- the upgrade
        # affecting the upstream module is independent!
        # This way we avoid the UpgradeWorkflowHandler looking up the port and
        # raising MissingPackageVersion when it tries to access
        # old_src_module.module_descriptor.
        from vistrails.core.modules.utils import create_port_spec_string
        from vistrails.core.vistrail.port import Port
        source_port = Port(name="Widget", type='source',
                           signature=create_port_spec_string([
                                   ('org.vistrails.vistrails.spreadsheet',
                                    'SpreadsheetCell', '')]))
        new_conn = UpgradeWorkflowHandler.create_new_connection(
                controller,
                old_src_module, source_port,
                new_module, 'cell')
        return [('add', new_conn)]

    module_remap = {
            # SpreadsheetCell now outputs the widget on the 'Widget' output
            # port
            # We used to get it from m.cellWidget, with 'm' from the 'self'
            # output port
            'PromptIsOkay': [
                ('0.9.2', '0.9.3', None, {
                    'dst_port_remap': {
                        'cell': fix_cell_input},
                }),
            ],
        }

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)
