###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

from vistrails.core.modules.utils import make_modules_dict
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler

from .common import _modules as common_modules, TableOutput
from .convert import _modules as convert_modules
from .operations import _modules as operation_modules
from .read import _modules as read_modules
from .write import _modules as write_modules


_modules = [common_modules,
            convert_modules,
            operation_modules,
            read_modules,
            write_modules]

if get_package_manager().has_package( # pragma: no branch
        'org.vistrails.vistrails.spreadsheet'):
    from .viewer import _modules as viewer_modules, TableToSpreadsheetMode
    _modules.append(viewer_modules)
    TableOutput.register_output_mode(TableToSpreadsheetMode)

_modules = make_modules_dict(*_modules)


def handle_module_upgrade_request(controller, module_id, pipeline):
    def add_keyname(fname, module):
        new_function = controller.create_function(module,
                                                  "key_name",
                                                  ["_key"])
        return [('add', new_function, 'module', module.id)]

    module_remap = {
            'read|csv|CSVFile': [
                (None, '0.1.1', 'read|CSVFile', {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|numpy|NumPyArray': [
                (None, '0.1.1', 'read|NumPyArray', {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|CSVFile': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
                ('0.1.3', '0.1.5', None, {})
            ],
            'read|NumPyArray': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|ExcelSpreadsheet': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
                ('0.1.3', '0.1.4', None, {})
            ],
            'read|JSONFile': [
                (None, '0.1.5', 'read|JSONObject', {
                    'function_remap': {
                        None: add_keyname},
                })
            ],
        }

    try:
        from vistrails.packages.spreadsheet.init import upgrade_cell_to_output
    except ImportError:
        pass
    else:
        module_remap = upgrade_cell_to_output(
                module_remap, module_id, pipeline,
                'TableCell', 'TableOutput',
                '0.1.6', 'table')

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)
