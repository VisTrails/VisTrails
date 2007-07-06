############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
################################################################################
# Spreadsheet Package for VisTrails
################################################################################
from PyQt4 import QtCore, QtGui
from core.modules import basic_modules, module_registry
from core.modules.vistrails_module import Module
from core.system import vistrails_root_directory
from spreadsheet_controller import spreadsheetController
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_window import SpreadsheetWindow
import os
import string
import sys

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
        widget = importReturnLast(packagePath)
        if hasattr(widget, 'widgetName'):
            widgetName = widget.widgetName()
        else:
            widgetName = packagePath
        widget.registerWidget(module_registry, basic_modules, basicWidgets)
        spreadsheetRegistry.registerPackage(widget, packagePath)
        print '  ==> Successfully import <%s>' % widgetName
    except:
        print '  ==> Ignored package <%s>' % packagePath
        widget = None
    return widget

def importWidgetModules(basicWidgets):
    """ importWidgetModules(basicWidgets: widget) -> None
    Find all widget package under ./widgets/* to add to the spreadsheet registry
    
    """
    widgetDir = (vistrails_root_directory()+
                 '/'+string.replace(__name__, '.', '/')+'/widgets/')
    candidates = os.listdir(widgetDir)
    for folder in candidates:
        if os.path.isdir(widgetDir+folder) and folder!='.svn':
            addWidget(__name__+'.widgets.'+folder)

def initialize(*args, **keywords):
    """ initialize() -> None
    Package-entry to initialize the package
    
    """
    # Create application if there is no one available
    module_registry.registry.setCurrentPackageName('Spreadsheet')
    print 'Loading Spreadsheet widgets...'
    global basicWidgets
    if basicWidgets==None:
        basicWidgets = addWidget('packages.spreadsheet.basic_widgets')
    importWidgetModules(basicWidgets)
    global app
    app = QtCore.QCoreApplication.instance()
    if app==None:
        app = QtGui.QApplication(sys.argv)
    if hasattr(app, 'builderWindow'):
        global spreadsheetWindow        
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()

def finalize():
    spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
    spreadsheetWindow.destroy()
    spreadsheetWindow.deleteLater()
