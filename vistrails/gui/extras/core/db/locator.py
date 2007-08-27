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

from gui.open_db_window import QOpenDBWindow
from core.db.locator import DBLocator, XMLFileLocator
from PyQt4 import QtGui
import core.system
import os


##############################################################################
# DB dialogs

def get_load_db_locator_from_gui(parent):
    config, vistrail_id = QOpenDBWindow.getOpenVistrail()
    if config == {} or vistrail_id == -1:
        return None
    return DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     None,
                     vistrail_id,
                     config.get('id', None))

def get_save_db_locator_from_gui(parent, locator=None):
    config, name = QOpenDBWindow.getSaveVistrail()
    if config == {} or name == '':
        return None
    return DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     name,
                     None,
                     config.get('id', None))

##############################################################################
# XML File dialogs

def get_load_xml_file_locator_from_gui(parent):
    fileName = QtGui.QFileDialog.getOpenFileName(
        parent,
        "Open Vistrail...",
        core.system.vistrails_file_directory(),
        "Vistrail files (*.xml)\nOther files (*)")
    if fileName.isEmpty():
        return None
    return XMLFileLocator(str(fileName))

def get_save_xml_file_locator_from_gui(parent, locator=None):
    # Ignore current locator for now
    # In the future, use locator to guide GUI for better starting directory
    print parent
    fileName = QtGui.QFileDialog.getSaveFileName(
        parent,
        "Save Vistrail...",
        core.system.vistrails_file_directory(),
        "VisTrails files (*.xml)",
        None,
        QtGui.QFileDialog.DontConfirmOverwrite)
    if fileName.isEmpty():
        return None
    f = str(fileName)
    if not f.endswith('.xml'):
        f += '.xml'
    if os.path.isfile(f):
        msg = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                                "VisTrails",
                                "File exists. Overwrite?",
                                (QtGui.QMessageBox.Yes |
                                 QtGui.QMessageBox.No),
                                parent)
        if msg.exec_() == QtGui.QMessageBox.No:
            return None
    return XMLFileLocator(f)

