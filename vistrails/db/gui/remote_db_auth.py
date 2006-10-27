import os
import sys
import MySQLdb
from PyQt4 import *
from db.gui.remote_db_auth_GUI import Ui_Database

class Ui_RemoteDbAuth(QtGui.QDialog):

    def __init__(self):

        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_Database()
        self.ui.setupUi(self)

        # Connect up the GUI elements.
        self.connect(self.ui.btn_submit, QtCore.SIGNAL("clicked()"), self.validatePassword)
        self.connect(self.ui.btn_quit, QtCore.SIGNAL("clicked()"), self.reject)

    def setConfig(self,configParam):
        self.config = configParam

    def validatePassword(self):
        try:
            self.config.dbPasswd = str(self.ui.txt_dbpassword.text())
            self.config.createDBConnection()
            self.config.showMainWindow()
        except MySQLdb.OperationalError, message:
            errorMessage = "Please, check your DB availability and password.\nError: %d : %s" % (message[0], message[1])
            QtGui.QMessageBox.information(None, "ERROR", errorMessage, QtGui.QMessageBox.Ok)
            self.ui.txt_dbpassword.setText("")
