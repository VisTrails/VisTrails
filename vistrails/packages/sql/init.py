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

from core.bundles import py_import

MySQLdb = py_import('MySQLdb', {'linux-ubuntu':'python-mysqldb',
                                'linux-fedora':'MySQL-python'})

psycopg2 = py_import('psycopg2', {'linux-ubuntu':'python-psycopg2',
                                  'linux-fedora':'python-psycopg2'})
from PyQt4 import QtCore, QtGui
import urllib

from core import debug
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from gui.modules.source_configure import SourceConfigurationWidget
from core.upgradeworkflow import UpgradeWorkflowHandler
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
    def __init__(self):
         Module.__init__(self)
         self.conn = None
         self.protocol = 'mysql'
    
    def get_db_lib(self):
        if self.protocol == 'mysql':
            return MySQLdb
        elif self.protocol == 'postgresql':
            return psycopg2
        else:
            raise ModuleError(self, "Currently no support for '%s'" % protocol)
        
    def ping(self):
        """ping() -> boolean 
        It will ping the database to check if the connection is alive.
        It returns True if it is, False otherwise. 
        This can be used for preventing the "MySQL Server has gone away" error. 
        """
        result = False
        if self.conn:
            try:
                self.conn.ping()
                result = True
            except self.get_db_lib().OperationalError, e:
                result = False
            except AttributeError, e:
                #psycopg2 connections don't have a ping method
                try:
                    if self.conn.status == 1:
                        result = True
                except Exception, e:
                    result = False
        return result
    
    def open(self):        
        retry = True
        while retry:
            config = {'host': self.host,
                      'port': self.port,
                      'user': self.user}
            
            # unfortunately keywords are not standard across libraries
            if self.protocol == 'mysql':    
                config['db'] = self.db_name
                if self.password is not None:
                    config['passwd'] = self.password
            elif self.protocol == 'postgresql':
                config['database'] = self.db_name
                if self.password is not None:
                    config['password'] = self.password
            try:
                self.conn = self.get_db_lib().connect(**config)
                break
            except self.get_db_lib().Error, e:
                debug.warning(str(e))
                if (e[0] == 1045 or self.get_db_lib().OperationalError 
                    and self.password is None):
                    passwd_dlg = QPasswordEntry()
                    if passwd_dlg.exec_():
                        self.password = passwd_dlg.get_password()
                    else:
                        retry = False
                else:
                    raise ModuleError(self, str(e))
             
    def compute(self):
        self.checkInputPort('db_name')
        self.host = self.forceGetInputFromPort('host', 'localhost')
        self.port = self.forceGetInputFromPort('port', 3306)
        self.user = self.forceGetInputFromPort('user', None)
        self.db_name = self.getInputFromPort('db_name')
        self.protocol = self.forceGetInputFromPort('protocol', 'mysql')
        if self.hasInputFromPort('password'):
            self.password = self.getInputFromPort('password')
        else:
            self.password = None

        self.open()

    # nice to have enumeration constant type
    _input_ports = [('host', '(edu.utah.sci.vistrails.basic:String)'),
                    ('port', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('user', '(edu.utah.sci.vistrails.basic:String)'),
                    ('db_name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('protocol', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('self', '(edu.utah.sci.vistrails.sql:DBConnection)')]

class SQLSource(Module):
    def __init__(self):
        Module.__init__(self)
        self.is_cacheable = self.cachedOff
        
    def compute(self):
        cached = False
        if self.hasInputFromPort('cacheResults'):
            cached = self.getInputFromPort('cacheResults')
        self.checkInputPort('connection')
        connection = self.getInputFromPort('connection')
        inputs = [self.getInputFromPort(k) for k in self.inputPorts
                  if k != 'source' and k != 'connection' and k!= 'cacheResults']
        #print 'inputs:', inputs
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        if not connection.ping():
            connection.open()
        cur = connection.conn.cursor()
        cur.execute(s, inputs)
    
        if cached:
            self.is_cacheable = self.cachedOn
        else:
            self.is_cacheable = self.cachedOff
            
        self.setResult('resultSet', cur.fetchall())

    def cachedOn(self):
        return True
    
    def cachedOff(self):
        return False
    
    _input_ports = [('connection', \
                         '(edu.utah.sci.vistrails.sql:DBConnection)'),
                    ('cacheResults', \
                      '(edu.utah.sci.vistrails.basic:Boolean)'),    
                    ('source', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = \
        [('resultSet', '(edu.utah.sci.vistrails.basic:List)')]

class SQLSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, None,
                                           True, False, parent)
        
_modules = [DBConnection,
            (SQLSource, {'configureWidgetType': SQLSourceConfigurationWidget})]

def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {'SQLSource': [(None, '0.0.3', None, {})]}

    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               module_remap)
