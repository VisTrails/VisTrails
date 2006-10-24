import os
import sys
#import ConfigParser
import MySQLdb

from PyQt4 import QtGui
from remote_db_auth import Ui_RemoteDbAuth
from upload_files import Ui_UploadFiles
from fetch_files import Ui_FetchFiles

class RemoteRep(object):
    def __init__(self, settings, type):
        self.loadSettings(settings)
        self.type = type
        self.auth = None
        if self.dbPasswd=="":
            self.showAuthDialog()
        else:
            self.showMainWindow()

    def createDBConnection(self):

        db = MySQLdb.connect(host=self.dbHost, 
                             port=self.dbPort,
                             user=self.dbUser,
                             passwd=self.dbPasswd,
                             db=self.dbName)
        return db

    def showAuthDialog(self):

        self.auth = Ui_RemoteDbAuth()
        self.auth.setConfig(self)
        self.auth.show()

    def showUploadFilesDialog(self):

        self.upload = Ui_UploadFiles()
        self.upload.setConfig(self)
        self.upload.show()

    def showFetchFilesDialog(self):

        self.fetch = Ui_FetchFiles()
        self.fetch.setConfig(self)
        self.fetch.show()

    def showMainWindow(self):

        if self.auth!=None:
            self.auth.hide()

        if self.type == "Upload":
            self.showUploadFilesDialog();
        else:
            self.showFetchFilesDialog();

    def loadSettings(self, settings):
        """ loadSettings(settings)->None """
        self.sshAddress = settings.sshUser+"@"+settings.sshHost
        self.sshPath = settings.sshDir+"/"
        self.sshAddressPath = self.sshAddress+":"+self.sshPath
        self.sshPort = settings.sshPort
        self.localDir = settings.localDir
        self.dbPasswd = settings.dbPasswd
        self.dbHost = settings.dbHost
        self.dbPort = settings.dbPort
        self.dbUser = settings.dbUser
        self.dbName = settings.dbName

class RemoteConfig:

    def __init__(self, settings=None):

        #self.config = ConfigParser.RawConfigParser()
        #self.config.read("vistrails.cfg")
        self.config = settings
        self.commandLineParam = sys.argv[1]
        self.auth = None
        self.loadParametersFromFile()

    def get(self,prop):

        return self.config.get("FileRepository",prop)

    def loadParametersFromFile(self):

        self.sshAddress = self.get("SSH_USER")+"@"+self.get("SSH_HOST")
        self.sshPath = self.get("SSH_DIR")+"/"
        self.sshAddressPath = self.sshAddress+":"+self.sshPath
        self.sshPort = self.get("SSH_PORT")
        self.localDir = self.get("LOCALDIR")
        self.dbPasswd = self.get("DB_PASSWD")

    def createDBConnection(self):

        db = MySQLdb.connect(host=self.get("DB_HOST"), 
                             port=int(self.get("DB_PORT")),
                             user=self.get("DB_USER"),
                             passwd=self.dbPasswd,
                             db=self.get("DB_NAME"))
        return db

    def showAuthDialog(self):

        self.auth = Ui_RemoteDbAuth()
        self.auth.setConfig(self)
        self.auth.show()

    def showUploadFilesDialog(self):

        self.upload = Ui_UploadFiles()
        self.upload.setConfig(self)
        self.upload.show()

    def showFetchFilesDialog(self):

        self.fetch = Ui_FetchFiles()
        self.fetch.setConfig(self)
        self.fetch.show()

    def showMainWindow(self):
 
        if self.auth!=None:
            self.auth.hide()

        if self.commandLineParam=="Upload":
            self.showUploadFilesDialog();
        else:
            self.showFetchFilesDialog();

if __name__ == "__main__":

    remoteConfigObj = RemoteConfig()

    app = QtGui.QApplication(sys.argv)
    
    if remoteConfigObj.dbPasswd=="":
        remoteConfigObj.showAuthDialog()
    else:
        remoteConfigObj.showMainWindow()

    sys.exit(app.exec_())

