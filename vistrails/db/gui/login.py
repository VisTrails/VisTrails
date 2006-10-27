#Author: Mayank Maheshwary

from PyQt4 import *
import db.gui.login_GUI
import xmlrpclib
import db.DBconfig
from db.xUpdateFunctions import UpdateFunctions

# Class for login GUI. Called from the corresponding menu item

class Ui_Login(QtGui.QDialog):

    def __init__(self):
        
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = login_GUI.Ui_Dialog()
        self.ui.setupUi(self)

        self.connect(self.ui.loginButton, QtCore.SIGNAL("clicked()"), self.login)

    def login(self):

        server = str(self.ui.serverLine.text())
        username = str(self.ui.usernameLine.text())
        password = str(self.ui.passwdLine.text())
	#print server
	#print username
	#print password
        try:
	    update = UpdateFunctions(server, username, password)
            folders = update.getListOfFolders("")
	    DBconfig.server = server
	    DBconfig.username = username
	    DBconfig.password = password
            #loggedIn = 1
#            print "logged in successfully"
        except xmlrpclib.Fault:
            QtGui.QMessageBox.information(None,"ERROR","Incorrect username or password",QtGui.QMessageBox.Ok)
	except IOError:
            QtGui.QMessageBox.information(None,"ERROR","Incorrect username or password",QtGui.QMessageBox.Ok)
        self.close()
