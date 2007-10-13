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

from gui.application import VistrailsApplication
from gui.open_db_window import QOpenDBWindow
from core.db.locator import DBLocator, FileLocator
from PyQt4 import QtGui, QtCore
import core.system
import os
import core.configuration

##############################################################################
# DB dialogs

def get_load_db_locator_from_gui(parent, obj_type):
    config, obj_id = QOpenDBWindow.getOpenDBObject(obj_type)
    if config == {} or obj_id == -1:
        return None
    return DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     None,
                     obj_id,
                     obj_type,
                     config.get('id', None))

def get_save_db_locator_from_gui(parent, obj_type, locator=None):
    config, name = QOpenDBWindow.getSaveDBObject(obj_type)
    if config == {} or name == '':
        return None
    return DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     name,
                     None,
                     obj_type,
                     config.get('id', None))

##############################################################################
# File dialogs

suffix_map = {'vistrail': ['vt', 'xml'],
              'workflow': ['xml'],
              'log': ['xml'],
              }

def get_load_file_locator_from_gui(parent, obj_type):
    suffixes = "*." + " *.".join(suffix_map[obj_type])
    fileName = QtGui.QFileDialog.getOpenFileName(
        parent,
        "Open %s..." % obj_type.capitalize(),
        core.system.vistrails_file_directory(),
        "VisTrails files (%s)\nOther files (*)" % suffixes)
    if fileName.isEmpty():
        return None
    filename = os.path.abspath(str(fileName))
    dirName = os.path.dirname(filename)
    setattr(VistrailsApplication.configuration, 'fileDirectory', dirName)
    core.system.set_vistrails_file_directory(dirName)
    return FileLocator(filename)

def get_save_file_locator_from_gui(parent, obj_type, locator=None):
    # Ignore current locator for now
    # In the future, use locator to guide GUI for better starting directory

# DAK -- don't understand this so replacing with suffix map
#     filetypes = "*%s "%VistrailsApplication.configuration.defaultFileType
#     supported_files = [".vt", ".xml"]
#     for e in supported_files:
#         if filetypes.find(str(e)+" ") == -1:
#             filetypes += "*%s " % e
    suffixes = "*." + " *.".join(suffix_map[obj_type])
    fileName = QtGui.QFileDialog.getSaveFileName(
        parent,
        "Save Vistrail...",
        core.system.vistrails_file_directory(),
        "VisTrails files (%s)" % suffixes, # filetypes.strip()
        None,
        QtGui.QFileDialog.DontConfirmOverwrite)
    if fileName.isEmpty():
        return None
    f = str(fileName)

    # check for proper suffix
    found_suffix = False
    for suffix in suffix_map[obj_type]:
        if f.endswith(suffix):
            found_suffix = True
            break
    if not found_suffix:
        if obj_type == 'vistrail':
            f += VistrailsApplication.configuration.defaultFileType
        else:
            f += '.' + suffix_map[obj_type][0]

    if os.path.isfile(f):
        msg = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                                "VisTrails",
                                "File exists. Overwrite?",
                                (QtGui.QMessageBox.Yes |
                                 QtGui.QMessageBox.No),
                                parent)
        if msg.exec_() == QtGui.QMessageBox.No:
            return None
    dirName = os.path.dirname(str(f))
    setattr(VistrailsApplication.configuration, 'fileDirectory', dirName)
    core.system.set_vistrails_file_directory(dirName)
    return FileLocator(f)
   
       
