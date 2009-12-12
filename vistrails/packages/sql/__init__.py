############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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

identifier = 'edu.utah.sci.vistrails.sql'
version = '0.0.1'
name = 'SQL'

import MySQLdb
from PyQt4 import QtCore, QtGui
import urllib

from core.modules.basic_modules import PythonSource
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.modules.tuple_configuration import PortTableConfigurationWidget, \
    PortTable
from core.utils import PortAlreadyExists
from gui.theme import CurrentTheme

class QPasswordEntry(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle("Enter Password:")
        self.setLayout(QtGui.QVBoxLayout())
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel("Password:"))
        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setEchoMode(QtGui.QLineEdit.Password)
        hbox.addWidget(self.line_edit)
        self.layout().addLayout(hbox)

        bbox = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        ok = QtGui.QPushButton("OK")
        ok.setDefault(True)
        bbox.addWidget(cancel, 1, QtCore.Qt.AlignRight)
        bbox.addWidget(ok, 0, QtCore.Qt.AlignRight)
        self.layout().addLayout(bbox)
        self.connect(ok, QtCore.SIGNAL("clicked(bool)"), self.accept)
        self.connect(cancel, QtCore.SIGNAL("clicked(bool)"), self.reject)

    def get_password(self):
        return str(self.line_edit.text())

class DBConnection(Module):
#     def __init__(self):
#         Module.__init__(self)
        
    def compute(self):
        self.checkInputPort('db_name')
        host = self.forceGetInputFromPort('host', 'localhost')
        port = self.forceGetInputFromPort('port', 3306)
        user = self.forceGetInputFromPort('user', None)
        db_name = self.getInputFromPort('db_name')
        protocol = self.forceGetInputFromPort('protocol', 'mysql')
        if self.hasInputFromPort('password'):
            password = self.getInputFromPort('password')
        else:
            password = None

        config = {'host': host,
                  'port': port,
                  'user': user,
                  'db': db_name}
        if password is not None:
            config['passwd': password]

        if protocol == 'mysql':
            retry = True
            while retry:
                try:
                    self.conn = MySQLdb.connect(**config)
                    break
                except MySQLdb.Error, e:
                    if e[0] == 1045 and password is None:
                        passwd_dlg = QPasswordEntry()
                        if passwd_dlg.exec_():
                            config['passwd'] = passwd_dlg.get_password()
                        else:
                            retry = False
                    else:
                        raise ModuleError(self, str(e))
        else:
            raise ModuleError(self, "Currently no support for '%s'" % protocol)

    # nice to have enumeration constant type
    _input_ports = [('host', '(edu.utah.sci.vistrails.basic:String)'),
                    ('port', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('user', '(edu.utah.sci.vistrails.basic:String)'),
                    ('db_name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('protocol', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('self', '(edu.utah.sci.vistrails.sql:DBConnection)')]

class SQLSource(Module):

    def compute(self):
        self.checkInputPort('connection')
        connection = self.getInputFromPort('connection')
        inputs = [self.getInputFromPort(k) for k in self.inputPorts
                  if k != 'source' and k != 'connection']
        print 'inputs:', inputs
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        cur = connection.conn.cursor()
        cur.execute(s, inputs)
        self.setResult('resultSet', cur.fetchall())

    _input_ports = [('connection', \
                         '(edu.utah.sci.vistrails.sql:DBConnection)'),
                    ('source', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = \
        [('resultSet', '(edu.utah.sci.vistrails.control_flow:ListOfElements)')]

class SQLEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
        # self.highlighter = PythonHighlighter(self.document())
        self.connect(self,
                     QtCore.SIGNAL('currentCharFormatChanged(QTextCharFormat)'),
                     self.formatChanged)

    def formatChanged(self, f):
        self.setFont(CurrentTheme.PYTHON_SOURCE_EDITOR_FONT)

class SQLSourceConfigurationWidget(PortTableConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        PortTableConfigurationWidget.__init__(self, module, controller, parent)
        
    def doLayout(self):
        self.setWindowTitle('SQLSource Configuration')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.createPortTable()
        self.createEditor()
        self.createButtons()

    def createPortTable(self):
        self.inputPortTable = PortTable(self)
        labels = QtCore.QStringList() << "Input Port Name" << "Type"
        self.inputPortTable.setHorizontalHeaderLabels(labels)
        self.inputPortTable.initializePorts(self.module.input_port_specs)
        self.layout().addWidget(self.inputPortTable)
        self.inputPortTable.fixGeometry()

    def findSourceFunction(self):
        fid = -1
        for i in xrange(self.module.getNumFunctions()):
            if self.module.functions[i].name=='source':
                fid = i
                break
        return fid

    def sizeHint(self):
        return QtCore.QSize(512, 512)

    def createEditor(self):
        self.codeEditor = SQLEditor(self)
        fid = self.findSourceFunction()
        if fid!=-1:
            f = self.module.functions[fid]
            self.codeEditor.setPlainText(urllib.unquote(f.params[0].strValue))
        self.codeEditor.document().setModified(False)
        self.layout().addWidget(self.codeEditor, 1)

    def updateVistrail(self):
        """updateVistrail() -> None
        Update vistrail to contain changes to the python source

        """
        (deleted_ports, added_ports) = \
            self.getPortDiff('input', self.inputPortTable)

        functions = []
        if self.codeEditor.document().isModified():
            code = urllib.quote(str(self.codeEditor.toPlainText()))
            functions.append(('source', [code]))
        if len(deleted_ports) + len(added_ports) + len(functions) == 0:
            # nothing changed
            return
        try:
            self.controller.update_ports_and_functions(self.module.id, 
                                                       deleted_ports, 
                                                       added_ports,
                                                       functions)
        except PortAlreadyExists, e:
            QtGui.QMessageBox.critical(self, 'Port Already Exists', str(e))
            return False
        return True        

def package_dependencies():
    return ['edu.utah.sci.vistrails.control_flow']

_modules = [DBConnection,
            (SQLSource, {'configureWidgetType': SQLSourceConfigurationWidget})]
