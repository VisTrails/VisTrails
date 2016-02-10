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


from vistrails.core.configuration import get_vistrails_persistent_configuration, \
    get_vistrails_configuration
from vistrails.gui.open_db_window import QOpenDBWindow, QConnectionDBSetupWindow
from vistrails.core.db.locator import DBLocator, FileLocator
from vistrails.db import VistrailsDBException
from vistrails.core import debug
import vistrails.db.services.io
from vistrails.gui.qt import QtCore, QtWidgets

import vistrails.core.system
import os

##############################################################################
# DB dialogs

def get_load_db_locator_from_gui(parent, obj_type):
    config, obj_id, obj_name = QOpenDBWindow.getOpenDBObject(obj_type)
    if config == {} or obj_id == -1:
        return None
    return DBLocator(config['host'],
                     config['port'],
                     config['db'],
                     config['user'],
                     config['passwd'],
                     obj_name,
                     obj_id=obj_id,
                     obj_type=obj_type,
                     connection_id=config.get('id', None))

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
                     obj_id=None,
                     obj_type=obj_type,
                     connection_id=config.get('id', None))

##############################################################################

def get_db_connection_from_gui(parent, id, name, host, port, user, passwd,
                               database):
    def show_dialog(parent, id, name, host, port, user,
                    passwd, databaseb, create):
        dialog = QConnectionDBSetupWindow(parent, id, name, host, port, user,
                                          passwd, database, create)
        config = None
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            config = {'host': str(dialog.hostEdt.text()),
                      'port': int(dialog.portEdt.value()),
                      'user': str(dialog.userEdt.text()),
                      'passwd': str(dialog.passwdEdt.text()),
                      'db': str(dialog.databaseEdt.text())
                      }
            try:
                vistrails.db.services.io.test_db_connection(config)
                config['succeeded'] = True
                config['name'] = str(dialog.nameEdt.text())
                config['id'] = dialog.id
            except VistrailsDBException as e:
                debug.critical('VisTrails DB Exception',  e)
                config['succeeded'] = False
        return config
    #check if the information is already there
    dbwindow = QOpenDBWindow.getInstance()
        
    config = dbwindow.connectionList.findConnectionInfo(host,port,database)

    if config:
        testconfig = dict(config)
        del testconfig['id']
        del testconfig['name']
        try:
            vistrails.db.services.io.test_db_connection(testconfig)
            config['succeeded'] = True
        except VistrailsDBException as e:
            config = show_dialog(parent, config['id'],
                                 config['name'], host, port, config['user'],
                                 passwd, database, create = False)
            
    elif config is None:
        config = show_dialog(parent, -1,"",
                             host, port, user, passwd,
                             database, create = True)
        if config['succeeded'] == True:
            #add to connection list
            dbwindow.connectionList.setConnectionInfo(**config)
    return config

##############################################################################
# File dialogs

suffix_map = {'vistrail': ['.vt', '.xml', '.vtl'],
              'workflow': ['.xml'],
              'log': ['.xml'],
              'registry': ['.xml'],
              'opm_graph': ['.xml'],
              'prov_document': ['.xml']
              }

def get_load_file_locator_from_gui(parent, obj_type):
    suffixes = "*" + " *".join(suffix_map[obj_type])
    fileName = QtWidgets.QFileDialog.getOpenFileName(
        parent,
        "Open %s..." % obj_type.capitalize(),
        vistrails.core.system.vistrails_file_directory(),
        "VisTrails files (%s)\nOther files (*)" % suffixes)[0]
    if not fileName:
        return None
    dirName = os.path.dirname(fileName)
    setattr(get_vistrails_persistent_configuration(), 'fileDir', dirName)
    setattr(get_vistrails_configuration(), 'fileDir', dirName)
    vistrails.core.system.set_vistrails_file_directory(dirName)
    return FileLocator(fileName)

def get_save_file_locator_from_gui(parent, obj_type, locator=None):
    # Ignore current locator for now
    # In the future, use locator to guide GUI for better starting directory

    suffixes = "*" + " *".join(suffix_map[obj_type])
    fileName = QtWidgets.QFileDialog.getSaveFileName(
        parent,
        "Save Vistrail...",
        vistrails.core.system.vistrails_file_directory(),
        filter="VisTrails files (%s)" % suffixes, # filetypes.strip()
        options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
    if not fileName:
        return None
    # check for proper suffix
    found_suffix = False
    for suffix in suffix_map[obj_type]:
        if fileName.endswith(suffix):
            found_suffix = True
            break
    if not found_suffix:
        if obj_type == 'vistrail':
            fileName += get_vistrails_configuration().defaultFileType
        else:
            fileName += suffix_map[obj_type][0]

    if os.path.isfile(fileName):
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                "VisTrails",
                                "File exists. Overwrite?",
                                (QtWidgets.QMessageBox.Yes |
                                 QtWidgets.QMessageBox.No),
                                parent)
        if msg.exec_() == QtWidgets.QMessageBox.No:
            return None
    dirName = os.path.dirname(fileName)
    setattr(get_vistrails_persistent_configuration(), 'fileDir', dirName)
    setattr(get_vistrails_configuration(), 'fileDir', dirName)
    vistrails.core.system.set_vistrails_file_directory(dirName)
    return FileLocator(fileName)
   
def get_autosave_prompt(parent):
    """ get_autosave_prompt(parent: QWidget) -> bool
    
    """
    result = QtWidgets.QMessageBox.question(parent, 
                                        "AutoSave",
                                        "Autosave data has been found.\nDo you want to open autosave data?",
                                        QtWidgets.QMessageBox.Open,
                                        QtWidgets.QMessageBox.Ignore)
    return result == QtWidgets.QMessageBox.Open

def ask_to_overwrite_file(parent=None, obj_type='vistrail'):
    overwrite = True
    fname = None
    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                            "VisTrails",
                            "File exists and contains changes. Overwrite?",
                            (QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No),
                            parent)
    if msg.exec_() == QtWidgets.QMessageBox.No:
        overwrite = False
        locator = get_save_file_locator_from_gui(parent, obj_type)
        if locator:
            fname = locator._name
    return (overwrite, fname)
