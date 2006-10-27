#Author: Mayank Maheshwary

from PyQt4 import *
import db.gui.logout_GUI
import db.DBconfig
import xmlrpclib
from db.xUpdateFunctions import UpdateFunctions

class Ui_Logout(QtGui.QDialog):

     def __init__(self):
       
         QtGui.QDialog.__init__(self)

         # Set up the user interface from Designer.
         self.ui = logout_GUI.Ui_Dialog()
         self.ui.setupUi(self)

         self.connect(self.ui.logoutButton, QtCore.SIGNAL("clicked()"), self.disconnect)
        
     def disconnect(self):
	 
	 DBconfig.username = None
	 DBconfig.password = None
	 DBconfig.server = None
         QtGui.QMessageBox.information(None,"SUCCESS","You have been disconnected from the database",QtGui.QMessageBox.Ok)
	 self.close()
