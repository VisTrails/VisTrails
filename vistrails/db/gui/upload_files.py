
import os
import stat
import core.system
import MySQLdb
from PyQt4 import QtCore, QtGui
from db.gui.upload_files_GUI import Ui_Upload
from core.utils import *
import md5
import socket
import getpass

class SendFileThread(QtCore.QThread):
    def __init__(self,config, pathList, baseDir, userName, notes):
        QtCore.QThread.__init__(self)
        self.config = config
        self.pathList = pathList
        self.baseDirectory = baseDir
        self.userName = userName
        self.notes = notes
    def run(self):
        # Creates a connection 
        db = self.config.createDBConnection()
        c = db.cursor()

        # Gets the current time from DB (to use as a holding directory for the selected files)
        c.execute("select UNIX_TIMESTAMP(NOW())")        
        dateRS = c.fetchall()
        dateStr = str(dateRS[0][0])

        paramsList = []
        if os.path.isdir(self.baseDirectory+os.sep+self.pathList[0]):
            # use a recursive copy
            paramsList.append("-r \""+self.baseDirectory+os.sep+self.pathList[0]+"\" "+self.config.sshAddressPath+dateStr)
        else:
            # copy each file
            for file in self.pathList:
                paramsList.append(" \""+self.baseDirectory+os.sep+file+"\"  "+self.config.sshAddressPath+dateStr+"/"+file)

        # create the holding directory for this upload
        mkdirParam = " "+self.config.sshAddress+" \"mkdir -p "+self.config.sshPath+dateStr+"\""
            
        os.system(system.remoteShellProgram()+str(self.config.sshPort)+mkdirParam)
        # copy the files (recursively or not)
        success = True
        for param in paramsList:
            if os.system(system.remoteCopyProgram()+str(self.config.sshPort)+param) != 0:
                success = False

        # add the DB info for every file
        count = 0
        if success==False:
            # delete the directory where a partial transfer has occured
            mkdirParam = " "+self.config.sshAddress+" \"rm -rf "+self.config.sshPath+dateStr+"\""
            
            os.system(system.remoteShellProgram()+str(self.config.sshPort)+mkdirParam)
        else:
            # for each file, add DB info
            host = socket.getfqdn()
            for path in self.pathList:
                if os.path.isdir(self.baseDirectory+os.sep+path):
                    children = os.listdir(self.baseDirectory+os.sep+path)
                    for child in children:
                        self.pathList.append(path+os.sep+child)
                else:
                    self.saveDatabaseInfo(host,path,dateStr,c, self.userName, self.notes)
                    count = count + 1

        c.close()
        db.close()
        self.emit(QtCore.SIGNAL("success(int)"), count)

    def saveDatabaseInfo(self,host,path,dateStr,c, userName, notes):

        """ Save the file information for a selected path, using the given date """

        # Opens the file so that we can calculate the MD5 digest
        fileHandler = open (self.baseDirectory + os.sep + path,"r")
        digester = md5.new()
        while True:
            # Reads the file taking chunks of 8 kbytes
            buf = fileHandler.read(8192)
            # If EOF has been reached, breaks loop
            if len(buf)==0:
                break
            # Updates the digester with the newly read bytes
            digester.update(buf)
        # Gets the digest itself, as an hex string
        md5dig = digester.hexdigest()

        # Define the source path using an scp-like form: containing the hostname and path inside that host.
	sourcePath = host + ":" + self.baseDirectory + os.sep + path
         
        size = str(os.stat(self.baseDirectory + os.sep + path)[6])

        # Use a linux file separator for every file
        dbFilename = "/".join(path.split(os.sep))

        # Constructs the SQL INSERT statement, containing all fields according to db schema (see above)
        sql = "insert into files (source_path,filename,size,hash,user,date,notes) values \
              ('"+sourcePath+"','"+dbFilename+"',"+size+",'"+md5dig+"','"+str(userName)+"',FROM_UNIXTIME("+dateStr+"),'"+str(notes)+"');"
            
        print("add to database: "+sql)
            
        # Executes the statement
        c.execute(str(sql))

class Ui_UploadFiles(QtGui.QDialog):

    # store a list of selected files (or a directory name)
    pathList = []
    # store the base directory (the directory that holds the selected files)
    baseDirectory = ""

    def __init__(self):
        QtGui.QDialog.__init__(self)

	self.config = None

        # Set up the user interface from Designer.
        self.ui = Ui_Upload()
        self.ui.setupUi(self)

        # set the current user it the user's field
        self.ui.txt_user.setText(getpass.getuser())

        # Connect up the buttons.
        self.connect(self.ui.btn_find_files, QtCore.SIGNAL("clicked()"), self.findFiles)
        self.connect(self.ui.btn_find_dir, QtCore.SIGNAL("clicked()"), self.findDirectory)
        self.connect(self.ui.btn_send, QtCore.SIGNAL("clicked()"), self.sendFileAction)
        self.connect(self.ui.btn_done, QtCore.SIGNAL("clicked()"), self.reject)

    def setConfig(self, configParam):
        self.config = configParam

    def findFiles(self):

        """ Open up a FileDialog so that the user can select multiple files """
        self.pathList = []
        self.baseDirectory = ""
        s = QtGui.QFileDialog.getOpenFileNames(self, "Select Files...", ".")
        for elem in s:
            elem = self.convertFileSeparator(str(elem))
            pathProbe, file = os.path.split(elem)
            if self.baseDirectory != "" and pathProbe != self.baseDirectory:
                print "Were you able to select multiple files within different directories? I am sorry, I will fail!!!"
		raise VistrailsInternalError("Multiple files within different directories")
            else:
                self.baseDirectory = pathProbe
            self.pathList.append(file)
        self.updateFileListGUI()

    def findDirectory(self):

        """ Open up a FileDialog so that the user can select a directory (recursive upload of files) """
        self.pathList = []
        self.baseDirectory = ""
        s = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory...", ".")
        dir = self.convertFileSeparator(str(s))
        dir = dir.rstrip(os.sep)
        path, file = os.path.split(dir)
        self.baseDirectory = path
        self.pathList.append(file)
        self.updateFileListGUI()

    def convertFileSeparator(self, path):

        """ Tries to use the correct file separator for the current operating system """

        if path.find("/")!=-1 and path.find("\\")!=-1:
            print ("The path contains Windows and Linux path separator chars... Be aware!")
        pathArray = path.split("/")
        if len(pathArray)==1:
            pathArray = path.split("\\")
        return ((os.sep).join(pathArray))

    def updateFileListGUI(self):

        """ Update the GUI, buildind up a list of file paths using the ';' as a list 
            separator (leaves a trailing ';' at the end of string """
        pathListStr = ""
        for elem in self.pathList:
            pathListStr = pathListStr + self.baseDirectory + os.sep + elem + " ; "
        self.ui.txt_file.setText(pathListStr)

    def sendFileAction(self):

        """ Send the file list to the repository (updating the DB) """

	# In a highly concurrent access to the upload function, there may be directory 
        # clashes (if two users click the "send button" at the same time). If the contents
        # of these directories has equal filenames, some files may be wrongly overwritten.
        # It is safer to check whether a directory with "dateStr" name already exists. For now,
        # it is not a requirement for the File Repository.
        #
        # Samples:
        # Windows: plink visrep@frodo "test -d /scratch/visrep/storage/<dateStr> ; echo $?"
        # Linux: ssh visrep@frodo 'test -d /scratch/visrep/storage/<dateStr> ; echo $?'
        #
        # A simple solution, considering that the frequency of clicks at the "send button" is lower
        # than the MySQL time resolution, is to tweak the dateStr placeholder in order to try 
        # another directory, e.g., dateStr+1 (in a loop until there is no existing directory)

        if len(self.pathList) == 0:
            QtGui.QMessageBox.information(self,"File Message","You should have used a \"Find...\" button",QtGui.QMessageBox.Ok)
        else:
            self.thread = SendFileThread(self.config, self.pathList, 
                                         self.baseDirectory, self.ui.txt_user.text(),
                                         self.ui.txt_notes.toPlainText())
            self.connect(self.thread, QtCore.SIGNAL("success(int)"), self.fileSent)
            self.connect(self.thread, QtCore.SIGNAL("finished()"), self.thread, QtCore.SLOT("deleteLater()"))
            self.thread.start()
            
    def fileSent(self, count):
        QtGui.QMessageBox.information(None,"VisTrails",str(count)+" file(s) sent to the Repository",QtGui.QMessageBox.Ok)
