############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
#############################################################################

""" This package provides a better way to interact with collections of
workflows.
"""
import sys

#for testing purposes
#this can be removed when added to vistrails trunk
#sys.path.append('../vistrails')

from PyQt4 import QtCore, QtGui
from ..core.configuration import ConfigurationObject
from medley_manager import MedleyManager

version = '0.1'
identifier = 'edu.utah.sci.vistrails.medleys'
name = 'Workflow Medleys'

configuration = ConfigurationObject(path=(None,str),
                                    debug=False)

################################################################################

def initialize():
    #medleys package doesn't have any modules
    
    # Create application if there is no one available
    app = QtCore.QCoreApplication.instance()
    if app==None:
        print "could not find VisTrails application..."
        print "An application will be created."
        app = QtGui.QApplication(sys.argv)
    #if hasattr(app, 'builderWindow'):
        # MedleyManager.find_medley_window()
        
def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.

    """
    def show_medleys():
        MedleyManager.show_medley_window()
    def create_workflow_view():
        MedleyManager.create_workflow_view_from_current_pipeline()
    lst = []
    lst.append(("Show Medley Window", show_medleys))
    lst.append(("Add Current Pipeline to Medleys", create_workflow_view))
    return tuple(lst)

def finalize():
    MedleyManager.finalize()
