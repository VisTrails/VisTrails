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
QVistrailList

"""
from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from db.services.io import get_db_connection_list, get_db_vistrail_list

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
        self.connect(self.connectionList,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateVistrailsList)
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
        conns = get_db_connection_list()
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setIconSize(QtCore.QSize(32,32))
        for c in conns:
            cItem = QDBConnectionListItem(CurrentTheme.DB_ICON,
                                          int(c[0]),
                                          str(c[1]))
            self.addItem(cItem)
        self.adjustSize()


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
    QVistrailList is a widget to show the vistrails abailable in the selected
    database

    """
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)

    def updateContents(self, connection_id):
        """updateContents(connection_id: int) -> None
        Reloads vistrails from the given connection
        
        """
        self.clear()
        vistrails = get_db_vistrail_list(int(connection_id))
        for (id,vistrail,date,user) in vistrails:
            item = QVistrailListItem(CurrentTheme.FILE_ICON,
                                     int(id),
                                     str(vistrail),
                                     str(date),
                                     str(user))
            self.addItem(item)
            
            
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
