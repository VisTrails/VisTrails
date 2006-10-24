"""TODO: Document this file."""

#Author: Mayank Maheshwary

from PyQt4 import *
import login
import DBconfig
import xmlrpclib
import uploadToExist_GUI
from xUpdateFunctions import UpdateFunctions
from xml_parser import XMLParser
from vistrail import Vistrail

# Class for upload GUI. Called from the corresponding menu item

class Ui_UploadFile(QtGui.QDialog):

    pathString =""
    
    def __init__(self):
        
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = uploadToExist_GUI.Ui_Dialog()
        self.ui.setupUi(self)


        self.populateFiles(self.pathString)
        self.populateFolders(self.pathString)

        self.connect(self.ui.saveButton, QtCore.SIGNAL("clicked()"), self.save)
        self.connect(self.ui.openFolderButton, QtCore.SIGNAL("clicked()"), self.openFolder)       
        self.connect(self.ui.upButton, QtCore.SIGNAL("clicked()"), self.goToParent)
	self.connect(self.ui.exportButton, QtCore.SIGNAL("clicked()"), self.export)

    def populateFiles(self, path):

        self.ui.fileTable.setColumnCount(4)
	self.ui.fileTable.setHorizontalHeaderLabels(["File name", "Owner", "Group", "Permissions"])
 
        #global update
	if(DBconfig.username == None):
	    QtGui.QMessageBox.information(None, "ERROR","You are not logged in", QtGui.QMessageBox.Ok)
	else:
	    update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
	    listOfFiles = update.getListOfFiles(path)
	    self.ui.fileTable.setRowCount(len(listOfFiles))
	    #print listOfFiles
	    i = 0
        
	    for j in listOfFiles:
		self.ui.fileTable.setItem(i, 0, QtGui.QTableWidgetItem(str(j['name'])))
		self.ui.fileTable.setItem(i, 1, QtGui.QTableWidgetItem(str(j['owner'])))
		self.ui.fileTable.setItem(i, 2, QtGui.QTableWidgetItem(str(j['group'])))
		self.ui.fileTable.setItem(i, 3, QtGui.QTableWidgetItem(str(j['permissions'])))
		i = i + 1


    def populateFolders(self, path):

        self.ui.folderTable.setColumnCount(1)
	self.ui.folderTable.setHorizontalHeaderLabels(["Folder name"])

        #global update
	if(DBconfig.username == None):
	    QtGui.QMessageBox.information(None, "ERROR","You are not logged in", QtGui.QMessageBox.Ok)
	else:
	    update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
	    listOfFolders = update.getListOfFolders(path)
	    #print listOfFolders
	    self.ui.folderTable.setRowCount(len(listOfFolders))
	    i = 0

	    for j in listOfFolders:
		self.ui.folderTable.setItem(i, 0, QtGui.QTableWidgetItem(str(j)))
		i = i+1

    def openFolder(self):
        
        selectedRanges = self.ui.folderTable.selectedRanges()
        for selection in selectedRanges:
                lines = range(selection.topRow(),selection.bottomRow()+1)
		for line in lines:
		    foldername = str(self.ui.folderTable.item(line,0).text())

	if(self.pathString == ""):
	    self.pathString += '%s' % foldername
	else:
	    self.pathString += '/%s' % foldername

	self.populateFolders(self.pathString)
	self.populateFiles(self.pathString)
	
    def goToParent(self):

	i = self.pathString.rfind("/")
	#print i
	if(i == -1):
	    self.pathString = ""
	else:
	    stringList = self.pathString.split('/')
	    listLen = len(stringList)
	    #print listLen
	    j = 0
	    self.pathString = ""
	    while j < listLen-1:
		self.pathString += str(stringList[j])
		if(j < listLen-2):
		    self.pathString += "/"
		j = j+1

	self.populateFolders(self.pathString)
	self.populateFiles(self.pathString)

    def save(self):
	self.export = 0
	fname = QtGui.QFileDialog.getOpenFileName(self, 
			                             "Upload Vistrail to eXist...",
						     "",
						     "XML files (*.xml)")
	self.filename = str(fname)
	update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
	
	items = self.ui.fileTable.selectedItems()
	f = items[0].text()

	if(self.pathString == ""):
	    self.pathString += '%s' % str(f)
	else:
	    self.pathString += '/%s' % str(f)

	#  The best way to assure we are writing the file properly is to read in the vistrail,
	#  form the object, update the dbinfo tag, and re-serialize.
	parser = XMLParser()
	parser.openVistrail(self.filename)
	vistrail = parser.getVistrail()

	vistrail.lastDBTime = vistrail.latestTime
	vistrail.remoteFilename = self.pathString

	vistrail.serialize(self.filename)
	f = open(self.filename, "r")
	con = f.read()
	f.close()
	update.putDoc(self.pathString, con, True)
	self.close()

    def export(self):
	self.export = 1
	items = self.ui.fileTable.selectedItems()
	f = items[0].text()
	if(self.pathString == ""):
	    self.pathString += '%s' % str(f)
	else:
	    self.pathString += '/%s' % str(f)
	self.close()
