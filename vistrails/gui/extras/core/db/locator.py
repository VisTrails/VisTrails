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
# File dialogs

def get_load_file_locator_from_gui(parent):
    fileName = QtGui.QFileDialog.getOpenFileName(
        parent,
        "Open Vistrail...",
        core.system.vistrails_file_directory(),
        "Vistrail files (*.xml *.vt)\nOther files (*)")
    if fileName.isEmpty():
        return None
    filename = str(fileName)
    dirName = os.path.dirname(filename)
    setattr(VistrailsApplication.configuration, 'fileDirectory', dirName)
    core.system.set_vistrails_file_directory(dirName)
    return FileLocator(filename)

def get_save_file_locator_from_gui(parent, locator=None):
    # Ignore current locator for now
    # In the future, use locator to guide GUI for better starting directory
    filetypes = "*%s "%VistrailsApplication.configuration.defaultFileType
    supported_files = [".vt", ".xml"]
    for e in supported_files:
        if filetypes.find(str(e)+" ") == -1:
            filetypes += "*%s " % e
    fileName = QtGui.QFileDialog.getSaveFileName(
        parent,
        "Save Vistrail...",
        core.system.vistrails_file_directory(),
        "VisTrails files (%s)"%filetypes.strip(),
        None,
        QtGui.QFileDialog.DontConfirmOverwrite)
    if fileName.isEmpty():
        return None
    f = str(fileName)
    if not f.endswith('.xml') and not f.endswith('.vt'):
        f += VistrailsApplication.configuration.defaultFileType
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
    accepted = VistrailsApplication.configuration.publicDomain.accepted
    if (core.configuration._class_version == True and
        VistrailsApplication.configuration.publicDomain.ask):
        (accepted, not_ask) =  ask_public_domain_permission(parent)
        setattr(VistrailsApplication.configuration.publicDomain,
                'accepted', accepted)
        setattr(VistrailsApplication.configuration.publicDomain,
                'ask', not not_ask)
    print f
    return FileLocator(f, accepted)

def ask_public_domain_permission(parent):
    """ask_public_domain_permission(parent: QWidget) -> (bool, bool)
      The first element in the result tuple is whether the user accepted,
      the second is whether the user doesn't want to be asked again.
    """
    dialog = QtGui.QDialog(parent)
    dialog.setWindowTitle("VisTrails")
    label_txt = """We strongly encourage you to donate your VisTrails
files to public domain. Your files will contain a disclaimer very similar
to the one below: """
    label1 = QtGui.QLabel(label_txt, dialog) 
    text_edt = QtGui.QTextEdit(dialog)
    text_edt.setPlainText(core.system.public_domain_string() % "<NAMEOFUSER>")
    dont_askme_again = QtGui.QCheckBox(dialog)
    dont_askme_again.setText("Don't ask me again")
    b1 = QtGui.QPushButton("Yes", dialog)
    dialog.connect(b1, QtCore.SIGNAL("clicked()"),
                   dialog, QtCore.SLOT("accept()"))
    b2 = QtGui.QPushButton("No", dialog)
    dialog.connect(b2, QtCore.SIGNAL("clicked()"),
                   dialog, QtCore.SLOT("reject()"))
    layout = QtGui.QVBoxLayout()
    layout.setMargin(5)
    layout.setSpacing(5)
    layout.addWidget(label1)
    layout.addWidget(text_edt)
    layout.addWidget(dont_askme_again,0,QtCore.Qt.AlignRight)
    blayout = QtGui.QHBoxLayout()
    blayout.setMargin(5)
    blayout.setSpacing(5)
    blayout.addWidget(b1)
    blayout.addWidget(b2)
    layout.addLayout(blayout)
    dialog.setLayout(layout)
    if dialog.exec_() == QtGui.QDialog.Accepted:
        result = (True, dont_askme_again.isChecked())
        fullname = VistrailsApplication.configuration.publicDomain.fullname
        if  type(fullname) == tuple or fullname == "None":
            (res, ok) = QtGui.QInputDialog.getText(parent,
                                                   "VisTrails",
                                                   "Full Name: ",
                                                   QtGui.QLineEdit.Normal,
                                                   "")
            if not ok:
                return ask_public_domain_permission(parent)
            name = str(res)
            setattr(VistrailsApplication.configuration.publicDomain,
                'fullname', name)
    else:
        result = (False, dont_askme_again.isChecked())
    
    return result
   
       
