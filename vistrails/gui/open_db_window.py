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
""" File for the window used when opening a vistrail from the database

QOpenDBWindow
QDBConnectionList
QDBConnectionListItem
QVistrailList
QVistrailListItem

"""
from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.utils import show_warning, show_question, NO_BUTTON, YES_BUTTON
import db.services.io as io



class QOpenDBWindow(QtGui.QDialog):
    """
    QOpenDBWindow is a dialog containing two panels. the left panel shows all
    the stored database connections and the right paanel shows the vistrails
    available on the selected database connection.

    """
    def __init__(self, parent=None):
        """ __init__(parent: QWidget) -> QOpenDBWindow
        Construct the dialog with the two panels

        """
        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Choose a vistrail")
        mainLayout = QtGui.QVBoxLayout()
        panelsLayout = QtGui.QGridLayout()
        self.connectionList = QDBConnectionList(self)
        self.vistrailList = QVistrailList(self)
        panelsLayout.addWidget(self.connectionList,0,0,1,1)
        panelsLayout.setColumnMinimumWidth(1,10)
        panelsLayout.addWidget(self.vistrailList,0,2,1,2)
        self.createButton = QtGui.QPushButton('New/Change')
        panelsLayout.addWidget(self.createButton,1,0,1,1, QtCore.Qt.AlignRight)
        buttonsLayout = QtGui.QHBoxLayout()
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.openButton = QtGui.QPushButton('Open')
        self.openButton.setEnabled(False)
        
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.openButton)

        mainLayout.addLayout(panelsLayout)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)
        self.connectSignals()
        if self.connectionList.count() == 0:
            text = "You don't seem to have any connection available. \
Would you like to create one?"
            res = show_question('Vistrails',
                                text, 
                                [NO_BUTTON, YES_BUTTON],
                                NO_BUTTON)
            if res == YES_BUTTON:
                self.showConnConfig()
        
    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between GUI components        
        
        """
        self.connect(self.cancelButton,
                     QtCore.SIGNAL('clicked()'),
                     self.reject)
        self.connect(self.openButton,
                     QtCore.SIGNAL('clicked()'),
                     self.accept)
        self.connect(self.createButton,
                     QtCore.SIGNAL('clicked()'),
                     self.showConnConfig)
        self.connect(self.connectionList,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateVistrailsList)
        self.connect(self.connectionList,
                     QtCore.SIGNAL("reloadConnections"),
                     self.vistrailList.updateContents)
        self.connect(self.vistrailList,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateButtons)
        self.connect(self.vistrailList,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self.accept)

    def updateVistrailsList(self):
        """ updateVistrailsList() -> None
        Whenever a different connection is selected, it reloads the
        correspondent vistrails

        """
        currConn = str(self.connectionList.currentItem().id)
        self.vistrailList.updateContents(currConn)

    def updateButtons(self):
        if len(self.vistrailList.selectedItems()) > 0:
            self.openButton.setEnabled(True)
        else:
            self.openButton.setEnabled(False)

    def showConnConfig(self, *args, **keywords):
        keywords["parent"] = self
        
        dialog = QConnectionDBSetupWindow(**keywords)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            config = {'host': str(dialog.hostEdt.text()),
                      'port': int(dialog.portEdt.value()),
                      'user': str(dialog.userEdt.text()),
                      'passwd': str(dialog.passwdEdt.text()),
                      'db': str(dialog.databaseEdt.text())}
            io.set_db_connection_info(**config)
            self.connectionList.loadConnections()
            
    @staticmethod
    def getOpenVistrail():
        dlg = QOpenDBWindow()
        if dlg.exec_() == QtGui.QDialog.Accepted:
            return (dlg.connectionList.currentItem().id,
                    dlg.vistrailList.currentItem().id)
        else:
            return(-1,-1)
        
class QDBConnectionList(QtGui.QListWidget):
    """
    QDBConnection list is a widget to show the available databases

    """
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self,parent)
        self.loadConnections()
        self.adjustSize()

    def loadConnections(self):
        self.clear()
        conns = io.get_db_connection_list()
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setIconSize(QtCore.QSize(32,32))
        for c in conns:
            cItem = QDBConnectionListItem(CurrentTheme.DB_ICON,
                                          int(c[0]),
                                          str(c[1]))
            self.addItem(cItem)
        self.emit(QtCore.SIGNAL("reloadConnections"))


class QDBConnectionListItem(QtGui.QListWidgetItem):
    
    def __init__(self, icon, id, text, parent=None):
        """__init__(icon: QIcon, id: int, text: QString, parent: QListWidget)
                         -> QDBConnectionListItem
        Creates an item with id
        
        """
        QtGui.QListWidgetItem.__init__(self,icon, text, parent)
        self.id = id

        
class QVistrailList(QtGui.QListWidget):
    """
    QVistrailList is a widget to show the vistrails available in the selected
    database

    """
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)

    def updateContents(self, conn_id=-1):
        """updateContents(connection_id: int) -> None
        Reloads vistrails from the given connection
        
        """
        self.clear()
        if conn_id != -1:
            try:
                vistrails = io.get_db_vistrail_list(int(conn_id))
                
                for (id,vistrail,date,user) in vistrails:
                    item = QVistrailListItem(CurrentTheme.FILE_ICON,
                                             int(id),
                                             str(vistrail),
                                             str(date),
                                             str(user))
                    self.addItem(item)
            except Exception, e:
                #show connection setup
                parent = self.parent()
                config = io.get_db_connection_info(int(conn_id))
                if config != None:
                    config["create"] = False
                    parent.showConnConfig(**config)
                else:
                    raise e
            
            
class QVistrailListItem(QtGui.QListWidgetItem):
    
    def __init__(self, icon, id, name, date, user, parent=None):
        """__init__(icon: QIcon, id: int, name: QString,
                    date: QString, user: QString, parent: QListWidget)
                         -> QVistrailListItem
        Creates an item with id
        
        """
        QtGui.QListWidgetItem.__init__(self,icon, name, parent)
        self.id = id
        self.user = user
        self.date = date
        self.setToolTip("Last Modified on %s by %s" % (date, user))

class QConnectionDBSetupWindow(QtGui.QDialog):
    """
    QConnectionDBSetupWindow is a dialog for creating a DB connection.
    Temporarily, the connection will be saved to the user's startup.py file.
    
    """
    def __init__(self, parent=None, host="", port=3306, user="",
                 passwd="", db="", create=True):
        """ __init__(parent: QWidget) -> QConnectionDBSetupWindow
        Construct the dialog with the two panels

        """
        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Create a new Connection")
        mainLayout = QtGui.QVBoxLayout()
        infoLayout = QtGui.QGridLayout()
        hostLabel = QtGui.QLabel("Server Hostname:", self)
        self.hostEdt = QtGui.QLineEdit(host, self)
        portLabel = QtGui.QLabel("Port:", self)
        self.portEdt = QtGui.QSpinBox(self)
        self.portEdt.setMaximum(65535)
        self.portEdt.setValue(port)
        userLabel = QtGui.QLabel("Username:", self)
        self.userEdt = QtGui.QLineEdit(user, self)
        passwdLabel = QtGui.QLabel("Password:", self)
        self.passwdEdt = QtGui.QLineEdit(passwd,self)
        self.passwdEdt.setEchoMode(QtGui.QLineEdit.Password)
        self.passwdEdt.setToolTip("For your protection, your "
                                  "password will not be saved.")
        databaseLabel = QtGui.QLabel("Database:", self)
        self.databaseEdt = QtGui.QLineEdit(db,self)
        mainLayout.addLayout(infoLayout)
        
        infoLayout.addWidget(hostLabel,0,0,1,1)
        infoLayout.addWidget(self.hostEdt,0,1,1,1)
        infoLayout.addWidget(portLabel,0,2,1,1)
        infoLayout.addWidget(self.portEdt,0,3,1,1)
        infoLayout.addWidget(userLabel,1,0,1,1)
        infoLayout.addWidget(self.userEdt,1,1,1,3)
        infoLayout.addWidget(passwdLabel,2,0,1,1)
        infoLayout.addWidget(self.passwdEdt,2,1,1,3)
        infoLayout.addWidget(databaseLabel,3,0,1,1)
        infoLayout.addWidget(self.databaseEdt,3,1,1,3)
        
        buttonsLayout = QtGui.QHBoxLayout()
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.testButton = QtGui.QPushButton('Test')
        if create:
            caption = 'Create'
        else:
            caption = 'Update'
        self.createButton = QtGui.QPushButton(caption)
        
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.testButton)
        buttonsLayout.addWidget(self.createButton)

        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)
        self.connectSignals()
        self.updateButtons()
        
    def connectSignals(self):
        """ connectSignals() -> None
        Map signals between GUI components        
        
        """
        self.connect(self.cancelButton,
                     QtCore.SIGNAL('clicked()'),
                     self.reject)
        self.connect(self.createButton,
                     QtCore.SIGNAL('clicked()'),
                     self.accept)
        self.connect(self.testButton,
                     QtCore.SIGNAL('clicked()'),
                     self.testConnection)
        self.connect(self.hostEdt,
                     QtCore.SIGNAL('editingFinished()'),
                     self.updateButtons)
        self.connect(self.userEdt,
                     QtCore.SIGNAL('editingFinished()'),
                     self.updateButtons)
        self.connect(self.passwdEdt,
                     QtCore.SIGNAL('editingFinished()'),
                     self.updateButtons)
        self.connect(self.databaseEdt,
                     QtCore.SIGNAL('editingFinished()'),
                     self.updateButtons)
        self.connect(self.portEdt,
                     QtCore.SIGNAL('valueChanged(int)'),
                     self.updateButtons)

    def testConnection(self):
        """testConnection() -> None """
        config = {'host': str(self.hostEdt.text()),
                  'port': int(self.portEdt.value()),
                  'user': str(self.userEdt.text()),
                  'passwd': str(self.passwdEdt.text()),
                  'db': str(self.databaseEdt.text())}
        try:
            io.test_db_connection(config)
            show_warning('Vistrails',"Connection succeeded!")
            
        except Exception, e:
            QtGui.QMessageBox.critical(None,
                                       'Vistrails',
                                       str(e))
    def updateButtons(self):
        if (self.hostEdt.text() != "" and
            self.portEdt.value() != 0 and
            self.userEdt.text() != "" and
            self.databaseEdt.text() != ""):
            self.createButton.setEnabled(True)
        else:
            self.createButton.setEnabled(False)
