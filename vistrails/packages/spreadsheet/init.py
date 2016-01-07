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

"""Spreadsheet Package for VisTrails
"""

from __future__ import division

import copy
import os
from PyQt4 import QtCore, QtGui
import sys

from vistrails.core import debug
from vistrails.core.modules import basic_modules
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.utils import create_descriptor_string
from vistrails.core.system import vistrails_root_directory
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler, \
    UpgradePackageRemap, UpgradeModuleRemap

from .spreadsheet_controller import spreadsheetController
from .spreadsheet_registry import spreadsheetRegistry


# This must be here because of VisTrails protocol

basicWidgets = None


def importReturnLast(name):
    """ importReturnLast(name: str) -> package
    Import a package whose name is specified in name and return right-most
    package on the package name

    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def addWidget(packagePath):
    """ addWidget(packagePath: str) -> package
    Add a new widget type to the spreadsheet registry supplying a
    basic set of spreadsheet widgets

    """
    try:
        registry = get_module_registry()
        widget = importReturnLast(packagePath)
        if hasattr(widget, 'widgetName'):
            widgetName = widget.widgetName()
        else:
            widgetName = packagePath
        widget.registerWidget(registry, basic_modules, basicWidgets)
        spreadsheetRegistry.registerPackage(widget, packagePath)
        debug.log('  ==> Successfully import <%s>' % widgetName)
    except Exception, e:
        debug.log('  ==> Ignored package <%s>' % packagePath, e)
        widget = None
    return widget


def importWidgetModules(basicWidgets):
    """ importWidgetModules(basicWidgets: widget) -> None
    Find all widget package under ./widgets/* to add to the spreadsheet registry

    """
    packageName = __name__.lower().endswith('.init') and \
        __name__[:-5] or __name__
    widgetDir = os.path.join(
        os.path.join(os.path.dirname(vistrails_root_directory()),
                     *packageName.split('.')),
        'widgets')
    candidates = os.listdir(widgetDir)
    for folder in candidates:
        if os.path.isdir(os.path.join(widgetDir, folder)) and folder != '.svn':
            addWidget('.'.join([packageName, 'widgets', folder]))


def initialize(*args, **keywords):
    """ initialize() -> None
    Package-entry to initialize the package

    """
    import vistrails.core.application
    if not vistrails.core.application.is_running_gui():
        raise RuntimeError, "GUI is not running. The Spreadsheet package requires the GUI"

    # initialize widgets
    debug.log('Loading Spreadsheet widgets...')
    global basicWidgets
    if basicWidgets==None:
        basicWidgets = addWidget('vistrails.packages.spreadsheet.basic_widgets')
    importWidgetModules(basicWidgets)

    # Create application if there is no one available
    global app
    app = QtCore.QCoreApplication.instance()
    if app==None:
        app = QtGui.QApplication(sys.argv)
    if hasattr(app, 'builderWindow'):
        global spreadsheetWindow
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow(show=False)


def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.

    """
    def show_spreadsheet():
        spreadsheetWindow.show()
        spreadsheetWindow.activateWindow()
        spreadsheetWindow.raise_()
    lst = []
    lst.append(("Show Spreadsheet", show_spreadsheet))
    return tuple(lst)


def finalize():
    spreadsheetWindow = spreadsheetController.findSpreadsheetWindow(
        show=False, create=False)
    if spreadsheetWindow is not None:
        ### DO NOT ADD BACK spreadsheetWindow.destroy()
        ### That will crash VisTrails on Mac.
        ### It is not supposed to be called directly
        spreadsheetWindow.cleanup()
        spreadsheetWindow.deleteLater()


def upgrade_cell_to_output(module_remap, module_id, pipeline,
                           old_name, new_module,
                           end_version, input_port_name,
                           start_version=None, output_version=None):
    """This function upgrades a *Cell module to a *Output module.

    The upgrade only happens if the original module doesn't have any connection
    on the cell input ports that can't be translated.

    This is to ease the transition to *Output modules, but we don't want (or
    need) to break anything; the *Cell modules still exist, so they can stay.
    """
    if not isinstance(module_remap, UpgradePackageRemap):
        module_remap = UpgradePackageRemap.from_dict(module_remap)

    old_module = pipeline.modules[module_id]
    old_module_name = create_descriptor_string(old_module.package,
                                               old_module.name,
                                               old_module.namespace,
                                               False)
    if old_module_name != old_name:
        return module_remap

    used_input_ports = set(old_module.connected_input_ports.keys())
    for func in old_module.functions:
        used_input_ports.add(func.name)

    if used_input_ports != set([input_port_name]):
        return module_remap

    _old_remap = module_remap
    module_remap = copy.copy(module_remap)
    assert _old_remap.remaps is not module_remap.remaps
    remap = UpgradeModuleRemap(start_version, end_version, output_version,
                               module_name=old_name,
                               new_module=new_module)
    remap.add_remap('dst_port_remap', input_port_name, 'value')
    remap.add_remap('function_remap', input_port_name, 'value')
    module_remap.add_module_remap(remap)
    return module_remap


def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {
            'CellLocation': [
                (None, '0.9.3', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
            ],
            'SheetReference': [
                (None, '0.9.3', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
            ],
            'SingleCellSheetReference': [
                (None, '0.9.3', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
            ],
        }

    module_remap = upgrade_cell_to_output(
            module_remap, module_id, pipeline,
            'RichTextCell', 'org.vistrails.vistrails.basic:RichTextOutput',
            '0.9.4', 'File')
    module_remap = upgrade_cell_to_output(
            module_remap, module_id, pipeline,
            'ImageViewerCell', 'org.vistrails.vistrails.basic:ImageOutput',
            '0.9.4', 'File')

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)
