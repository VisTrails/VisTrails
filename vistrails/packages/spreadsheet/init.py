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
################################################################################
# Spreadsheet Package for VisTrails
################################################################################
from PyQt4 import QtCore, QtGui
from core import debug
from core.modules import basic_modules
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module
from core.system import vistrails_root_directory
from spreadsheet_controller import spreadsheetController
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_window import SpreadsheetWindow
import os
import string
import sys

# This must be here because of VisTrails protocol
from spreadsheet_config import configuration

################################################################################

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
    except:
        debug.log('  ==> Ignored package <%s>' % packagePath)
        widget = None
    return widget

def importWidgetModules(basicWidgets):
    """ importWidgetModules(basicWidgets: widget) -> None
    Find all widget package under ./widgets/* to add to the spreadsheet registry
    
    """
    packageName = __name__.lower().endswith('.init') and __name__[:-5] or __name__
    widgetDir = (vistrails_root_directory()+
                 '/'+string.replace(packageName, '.', '/')+'/widgets/')
    candidates = os.listdir(widgetDir)
    for folder in candidates:
        if os.path.isdir(widgetDir+folder) and folder!='.svn':
            addWidget(packageName+'.widgets.'+folder)

def initialize(*args, **keywords):
    """ initialize() -> None
    Package-entry to initialize the package
    
    """
    debug.log('Loading Spreadsheet widgets...')
    global basicWidgets
    if basicWidgets==None:
        basicWidgets = addWidget('packages.spreadsheet.basic_widgets')
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
    spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
    ### DO NOT ADD BACK spreadsheetWindow.destroy()
    ### That will crash VisTrails on Mac. 
    ### It is not supposed to be called directly
    spreadsheetWindow.cleanup()
    spreadsheetWindow.deleteLater()
