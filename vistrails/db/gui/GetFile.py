"""TODO: Document this module."""

#Author: Mayank Maheshwary

from PyQt4 import *
import db.gui.login
import db.DBconfig
import xmlrpclib
import db.gui.downloadFromExist_GUI
from db.xUpdateFunctions import UpdateFunctions


# Class for Import and download GUI. Called from the corresponding menu item
class Ui_ImportFile(QtGui.QDialog):

    pathString =""
    
    def __init__(self):
	self.writeFile = 1
        
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = downloadFromExist_GUI.Ui_Dialog()
        self.ui.setupUi(self)


        self.populateFiles(self.pathString)
        self.populateFolders(self.pathString)

        self.connect(self.ui.importButton, QtCore.SIGNAL("clicked()"), self.importfile)
        self.connect(self.ui.downloadButton, QtCore.SIGNAL("clicked()"), self.save)
        self.connect(self.ui.openFolderButton, QtCore.SIGNAL("clicked()"), self.openFolder)       
        self.connect(self.ui.upButton, QtCore.SIGNAL("clicked()"), self.goToParent)
        
    def importfile(self):
	self.writeFile = 0
	self.filename = ""
	selectedRanges = self.ui.fileTable.selectedRanges()
        for selection in selectedRanges:
	    lines = range(selection.topRow(),selection.bottomRow()+1)
	    for line in lines:
		self.filename = str(self.ui.fileTable.item(line,0).text())

	if(DBconfig.username == None):
	    QtGui.QMessageBox.information(None, "ERROR","You are not logged in", QtGui.QMessageBox.Ok)
	    self.close()
	else:
	    if(self.filename != ""):
	        update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
		self.name = self.filename
	        self.filename = self.pathString + "/" + self.filename
	        self.content = update.getDocData(self.filename)
	self.close()

    def populateFiles(self, path):

        self.ui.fileTable.setColumnCount(4)
	self.ui.fileTable.setHorizontalHeaderLabels(["File name", "Owner", "Group", "Permissions"])
 
        #global update
	if(DBconfig.username == None):
	    QtGui.QMessageBox.information(None, "ERROR","You are not logged in", QtGui.QMessageBox.Ok)
	    self.close()
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
	    self.close()
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
	self.writeFile = 1
	
	self.filename = ""
	selectedRanges = self.ui.fileTable.selectedRanges()
        for selection in selectedRanges:
	    lines = range(selection.topRow(),selection.bottomRow()+1)
	    for line in lines:
		self.filename = str(self.ui.fileTable.item(line,0).text())

	if(DBconfig.username == None):
	    QtGui.QMessageBox.information(None, "ERROR","You are not logged in", QtGui.QMessageBox.Ok)
	    self.close()
	else:
	    if(self.filename != ""):
		self.saveFilename = QtGui.QFileDialog.getSaveFileName(None, "Save File", "/home", "XML (*.xml)")
		if(self.saveFilename != ""):
		    update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
		    self.filename = self.pathString + "/" + self.filename
		    print self.filename
		    fileContent = update.getDocData(self.filename)
		    #print fileContent
		    f = file(self.saveFilename, "w")
		    f.write(fileContent)
		    f.close()	
