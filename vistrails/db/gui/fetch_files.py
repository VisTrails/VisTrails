
import os
import core.system
import MySQLdb
from PyQt4 import QtCore, QtGui
from db.gui.fetch_files_GUI import Ui_Fetch

class FetchFileThread(QtCore.QThread):
    """ Thread to get files from the repository """
    def __init__(self,sql, config):
        QtCore.QThread.__init__(self)
        self.sql = sql
        self.config = config

    def run(self):
        db = self.config.createDBConnection()
        c = db.cursor()
        c.execute(str(self.sql))
        rs = c.fetchall()
        n = 0
        # Retrieve all files searching for the file path within a directory containing 
        # the date that the file was uploaded
        for file in rs:
            if self.getFile(str(file[1])+"/"+str(file[0]),str(file[0])) == 0:
                n += 1
        self.emit(QtCore.SIGNAL("success(int)"),n)
    
    def getFile(self,source,target):

        """ Fetch an specific file from the Repository """

        # create the directory to store the file
        parentDir = self.config.localDir+os.sep+os.path.split(target)[0]
        if not self._mkdir(parentDir):
            # handling the file separator 
            # (we are considering that the repository runs on a linux box)
            targetArray = target.split("/")
            params = " "+self.config.sshAddressPath+source+" "+self.config.localDir+os.sep+((os.sep).join(targetArray))  
        
            status = os.system(system.remoteCopyProgram()+str(self.config.sshPort)+params)
        else:
            status = 1
        return status

    def _mkdir(self, newdir):

        """ Create a new directory (building up all necessary parent directories) """

        if os.path.isdir(newdir):
            return 0
        elif os.path.isfile(newdir):
            return 1
            #raise OSError("There is a file on the way! " + newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                return self._mkdir(head)
            if tail:
                os.mkdir(newdir)
                return 0

class QueryDBThread(QtCore.QThread):
    """ Thread to query the database of the remote repository """

    def __init__(self, sql, config,results):
        QtCore.QThread.__init__(self)
        self.sql = sql
        self.config = config
        self.results = results

    def run(self):
        """ Connect to the Repository DB, execute the user specified query, and emit a
        signal containing the results."""

        db = self.config.createDBConnection()
        c = db.cursor()
        c.execute(str(self.sql))
        rs = c.fetchall()
        result = []
        
        # Check if the query produced any results
        if len(rs) > 0:
            desc = c.description
            self.results.append(desc)
            for line in rs:
                self.results.append(line)
        c.close()
        db.close()   

class Ui_FetchFiles(QtGui.QDialog):

    # This field is used to check whether the SQL query produced fully identifiable elements (files)
    firstColumnId = ""

    def __init__(self):

        QtGui.QDialog.__init__(self)

        self.config = None

        # Set up the user interface from Designer.
        self.ui = Ui_Fetch()
        self.ui.setupUi(self)
        self.results = []
        self.populateSampleQueries()

        # Connect up the GUI elements.
        self.connect(self.ui.btn_search, QtCore.SIGNAL("clicked()"), self.queryDB)
        self.connect(self.ui.cmb_queries, QtCore.SIGNAL("activated(int)"), self.updateQuery)
        self.connect(self.ui.btn_getSelectedFiles, QtCore.SIGNAL("clicked()"), self.getFiles)
        self.connect(self.ui.btn_done,QtCore.SIGNAL("clicked()"),self.reject)

    def setConfig(self, configParam):
        self.config=configParam
    
    def queryDB(self):

        """ Connect to the Repository DB, execute the user specified query"""
        self.ui.btn_search.setEnabled(False)
        self.qthread = QueryDBThread(str(self.ui.txt_query.text()),self.config, self.results)
        self.connect(self.qthread, QtCore.SIGNAL("finished()"), self.queryDBResult)
        self.qthread.start()

    def queryDBResult(self):
        """ Method called when QueryDBThread emits a succes signal. It populates 
            the GUI table (setting the column headers according to the user's query)."""
        result = self.results
        # Check if the query produced any results
        if len(result) > 0:
            i = 0
            j = 0
            # Set the dimensions for the Table Widget (used to show the query results)
            self.ui.tbl_results.setRowCount(len(result)-1)
            self.ui.tbl_results.setColumnCount(len(result[0]))
            desc = result[0]
            self.firstColumnId = desc[0][0]
            index = 0
            # Update table header
            for info in desc:
                self.ui.tbl_results.setHorizontalHeaderItem(index, QtGui.QTableWidgetItem(str(info[0])))
                index += 1
            # Update table contents
            rs = result[1:]
            for line in rs:
                #print line
                for elem in line:
                    self.ui.tbl_results.setItem(i,j,QtGui.QTableWidgetItem(str(elem)))
                    j += 1
                j = 0
                i = i + 1
        else:
            QtGui.QMessageBox.information(None,"VisTrails","There are no elements satisfying your query",QtGui.QMessageBox.Ok)
        self.qthread.deleteLater()
        self.qthread = None
        self.ui.btn_search.setEnabled(True)
   
    def updateQuery(self):

        """ Update the user's query field (according to the element selected within the combo box) """

        self.ui.txt_query.setText(self.ui.cmb_queries.currentText())

    def getFiles(self):

        """ Download the user selected files (multiple selection is allowed) """

        if self.firstColumnId == "id":
            ids = []
            # get the selected ranges in the table. If any cell is selected, the whole line is considered.
            selectedRanges = self.ui.tbl_results.selectedRanges()
            # collect the file id for every selected line
            for selection in selectedRanges:
                lines = range(selection.topRow(),selection.bottomRow()+1)
                for line in lines:
                    ids.append(str(self.ui.tbl_results.item(line,0).text()))
            # build an sql query to get all the required file info for all selected files
            sql = "select filename,UNIX_TIMESTAMP(date) from files where id in ("+(",".join(ids))+")"
#            print sql
 
            self.fthread = FetchFileThread(sql,self.config)
            self.connect(self.fthread, QtCore.SIGNAL("success(int)"), self.fetchFileResult)
            self.connect(self.fthread, QtCore.SIGNAL("finished()"), self.fthread, QtCore.SLOT("deleteLater()"))
            self.fthread.start()
        else:
            QtGui.QMessageBox.information(None,
                                          "ERROR","Sorry, I rely upon the \"id\" column to fetch files."
                                          "\nPlease, search again adding \"id\" as the very first column"
                                          " in your result set.",
                                          QtGui.QMessageBox.Ok)

    def fetchFileResult(self, count):
            QtGui.QMessageBox.information(None,
                                          "VisTrails",
                                          str(count)+" file(s) transferred successfully",
                                          QtGui.QMessageBox.Ok)

    def populateSampleQueries(self):

        """ Populate the sample queries according to a hardcoded list of options """

        queries = [" ", \
                   "select * from files", \
                   "select * from files where user='<user>'", \
                   "select id,notes from files where size>102400"]
        index = 0
        for query in queries:
            self.ui.cmb_queries.insertItem(index,QtCore.QString(query))
            index = index + 1
