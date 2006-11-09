""" File responsible to workflows related log """
import getpass
import socket
from core import system
import platform
import MySQLdb
from datetime import datetime

class Logger(object):

    def __init__(self):
        self.username = getpass.getuser()
        self.machineName = socket.getfqdn()
        self.machineId = -1 #it will be retrieved from DB
        self.os = system.systemType
        self.architecture = self.extractBitNumber(platform.architecture()[0]) 
        #the following ugly expression avoids getting '127.0.0.1' 
        self.processor = platform.processor()
        if not self.processor:
            self.processor = 'n/a'
        self.ip = self.getIpAddress()
        self.vistVer = system.vistrailsVersion()
        self.ram = system.guessTotalMemory()/(1024*1024)
        self.getSettingsFromApp()
        self.ssid = -1
        self.vistrailsMap = {} #maps vistrailsNames to vistrails_id in db
	self.wfDict = {} #vistrails_id : {version_number:wf_exec_id}
        self.modDict = {}#wf_exec_id : {module_id: exec_id}
        self.initSession()

    def getIpAddress(self):
	info = socket.getaddrinfo(socket.gethostname(), None)
	for i in info:
	    if len(i[4][0]) <= 15:
		return i[4][0]
	else:
	    return '0.0.0.0'

    def extractBitNumber(self, bitString):
        """ self.extractBitNumber(bitString) -> int """
        if bitString.endswith('bit'):
            return int(bitString[:-3])
        else:
            return 32 #default value 
    
    def createDBConnection(self):
        """ Creates a database connection """
        try:
            db = MySQLdb.connect(host=self.dbHost, 
                                 port=self.dbPort,
                                 user=self.dbUser,
                                 passwd=self.dbPasswd,
                                 db=self.dbName)
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        return db

    def getSettingsFromApp(self):
        """ self.getSettingsFromApp()->None 
        Get information from configuration.logger in vis_application.py"""
        import gui.vis_application
        app = gui.vis_application.VistrailsApplication
        if app:
            self.dbHost = app.configuration.logger.dbHost
            self.dbPort = app.configuration.logger.dbPort
            self.dbUser = app.configuration.logger.dbUser
            self.dbPasswd = app.configuration.logger.dbPasswd
            self.dbName = app.configuration.logger.dbName
        else:
            #testing purposes
            self.dbHost = 'frodo.sci.utah.edu'
            self.dbPort = 3306
            self.dbUser = 'vistrails'
            self.dbPasswd = 'vistrailspwd'
            self.dbName = 'vislog'

    def initSession(self):
        self.ssid = -1
        self.vistrailsMap = {} 
	self.wfDict = {} 
        self.modDict = {}

        self.db = self.createDBConnection()
        #check if machine_id is there
        self.machineId = self.getMachineIdDB()
        if self.machineId == -1:
            self.machineId = self.insertMachineDB()
        self.ssid = self.insertSessionIdDB()
        
    def finishSession(self):
        """ self.finishSession()->None """ 
        if self.ssid != -1:
            try:
                timestamp = self.getCurrentTimeDB()
                c = self.db.cursor()
                c.execute("""UPDATE session
                SET ts_end = %s 
                WHERE ss_id = %s""", (timestamp,self.ssid))
                self.db.commit()
            except MySQLdb.Error, e:
                print " Logger Error %d: %s" % (e.args[0], e.args[1])
            c.close()
            self.db.close()

    def getMachineIdDB(self):
        result = -1
        try:
            c = self.db.cursor()
            c.execute(""" 
            SELECT machine_id 
            FROM machine 
            WHERE name = %s 
            AND os = %s 
            AND architecture = %s 
            AND processor = %s 
            AND ram = %s """, (self.machineName, self.os, 
                               self.architecture, self.processor, self.ram))
            row = c.fetchone()
            if row:
                result = row[0]

        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

        return result

    def insertMachineDB(self):
        """ self.insertMachineInfo() -> int 
        Insert machine information into the database and return the machine_id """
        result = -1
        try:
            c = self.db.cursor()
            c.execute("""
            INSERT INTO machine(name,os,architecture,processor,ram)
            VALUES(%s,%s,%s,%s,%s) """, (self.machineName, self.os, self.architecture,
                                         self.processor, self.ram))
            self.db.commit()
            result = self.getMachineIdDB()
            
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        c.close()
        return result

    def getVistrailsIdDB(self, vistrailsName):
        """ self.getVistrailsIdDB(vistrailsName)->int"""
        result = -1
        try:
            c = self.db.cursor()
            c.execute(""" 
            SELECT vistrails_id 
            FROM vistrails 
            WHERE vistrails_name = %s """, (vistrailsName))
            row = c.fetchone()
            if row:
                result = row[0]

        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

        return result
    
    def insertVistrailsDB(self, vistrailsName):
        """ self.insertVistrailsDB() -> int 
        Insert vistrailsName information into the database and return the vistrails_id """
        result = -1
        try:
            c = self.db.cursor()
            c.execute("""
            INSERT INTO vistrails(vistrails_name)
            VALUES(%s) """, (vistrailsName))
            self.db.commit()
            result = self.getVistrailsIdDB(vistrailsName)
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        c.close()
        return result
    
    def insertSessionIdDB(self):
        """ self.insertSessionIdDB()->int It creates an entry in the database and return 
        the ss_id of the new entry."""
        result = -1
        try:
            timestamp = self.getCurrentTimeDB()
            c = self.db.cursor()
            c.execute("""
            INSERT INTO session(user,machine_id,ip,vis_ver, ts_start)
            VALUES(%s,%s,%s,%s,%s) """, (self.username, self.machineId,
                                      self.ip, self.vistVer, timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            self.db.commit()
            c.execute("""
            SELECT ss_id
            FROM session
            WHERE ts_start = %s AND user = %s""", (timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                                   self.username) )
            row = c.fetchone()
            if row:
                result = row[0]
            
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        c.close()
        return result

    def getVistrailsIdDB(self, vistrailsName):
        """ self.getVistrailsIdDB(vistrailsName)->int"""
        result = -1
        try:
            c = self.db.cursor()
            c.execute(""" 
            SELECT vistrails_id 
            FROM vistrails 
            WHERE vistrails_name = %s """, (vistrailsName))
            row = c.fetchone()
            if row:
                result = row[0]

        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

        return result
        
    def getCurrentTimeDB(self):
        """ getCurrentTimeDB() -> datetime.datetime object """
        timestamp = datetime.today()
        try:
            c = self.db.cursor()
            c.execute("SELECT NOW()")
            row = c.fetchone()
            if row:
                timestamp = row[0]
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
        return timestamp

    def startWorkflowExecution(self, vistrailsName, version_number):
        """ startWorkflowExecution(vistrailsName, version_number)->None """
        try:
            #vistrails information
	    if self.vistrailsMap.has_key(vistrailsName):
		vistrails_id = self.vistrailsMap[vistrailsName]
	    else:
		vistrails_id = self.getVistrailsIdDB(vistrailsName) 
		if vistrails_id == -1:
		    vistrails_id = self.insertVistrailsDB(vistrailsName)
		self.vistrailsMap[vistrailsName] = vistrails_id

            ts = self.getCurrentTimeDB()
            c = self.db.cursor()
            c.execute(""" INSERT INTO wf_exec(ss_id,vistrails_id,wf_version,ts_start)
	    VALUES (%s,%s,%s,%s)""",(self.ssid, vistrails_id, version_number, ts))
            self.db.commit()
	    c.execute(""" SELECT wf_exec_id 
	    FROM wf_exec
	    WHERE ss_id = %s
	    AND vistrails_id = %s
	    AND wf_version = %s
	    AND ts_start = %s""",(self.ssid, vistrails_id,version_number, ts))
	    
	    row = c.fetchone()
	    if row:
		wf_exec_id = row[0]
		
		if not self.wfDict.has_key(vistrails_id):
		    dict = {}
		    dict[version_number] = wf_exec_id
		    self.wfDict[vistrails_id] = dict
		else:
		    d = self.wfDict[vistrails_id]
		    d[version_number] = wf_exec_id
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
      
    def finishWorkflowExecution(self, vistrailsName, version_number):
	try:
	    vistrails_id = self.vistrailsMap[vistrailsName]
	    wf_exec_id = self.wfDict[vistrails_id][version_number]
	    
	    timestamp = self.getCurrentTimeDB()
	    c = self.db.cursor()
	    c.execute("""UPDATE wf_exec
	    SET ts_end = %s 
	    WHERE wf_exec_id = %s""", (timestamp,wf_exec_id))
            self.db.commit()
	    del self.wfDict[vistrails_id][version_number]
	except MySQLdb.Error, e:
	    print "Logger Error %d: %s" % (e.args[0], e.args[1])
		
	c.close()

    def startModuleExecution(self, vistrailsName, version_number, module_id, module_name):
	try:
	    vistrails_id = self.vistrailsMap[vistrailsName]
	    wf_exec_id = self.wfDict[vistrails_id][version_number]

            ts = self.getCurrentTimeDB()
            c = self.db.cursor()
            c.execute(""" INSERT INTO exec(ts_start,wf_exec_id,module_id,module_name)
	    VALUES (%s,%s,%s,%s)""",(ts, wf_exec_id, module_id, module_name))
            self.db.commit()
	    c.execute(""" SELECT exec_id 
	    FROM exec
	    WHERE ts_start = %s
	    AND wf_exec_id = %s
	    AND module_id = %s
	    AND module_name = %s""",(ts, wf_exec_id, module_id, module_name))
	    
	    row = c.fetchone()
	    if row:
		exec_id = row[0]
		
		if not self.modDict.has_key(wf_exec_id):
		    dict = {}
		    dict[module_id] = exec_id
		    self.modDict[wf_exec_id] = dict
		else:
		    d = self.modDict[wf_exec_id]
		    d[module_id] = exec_id
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
   
    def finishModuleExecution(self, vistrailsName, version_number, module_id):
	try:
	    vistrails_id = self.vistrailsMap[vistrailsName]
	    wf_exec_id = self.wfDict[vistrails_id][version_number]
            exec_id = self.modDict[wf_exec_id][module_id]

	    timestamp = self.getCurrentTimeDB()
	    c = self.db.cursor()
	    c.execute("""UPDATE exec
	    SET ts_end = %s 
	    WHERE exec_id = %s""", (timestamp,exec_id))
            self.db.commit()
	    del self.modDict[wf_exec_id][module_id]

	except MySQLdb.Error, e:
	    print "Logger Error %d: %s" % (e.args[0], e.args[1])
		
	c.close()


    def insertAnnotationDB(self, vistrailsName, version_number, module_id, annot_dict):
        """ """
        try:
	    vistrails_id = self.vistrailsMap[vistrailsName]
	    wf_exec_id = self.wfDict[vistrails_id][version_number]
            exec_id = self.modDict[wf_exec_id][module_id]

            insert_values = []
            c = self.db.cursor()
            for (key,value) in annot_dict.iteritems():
                insert_values.append((exec_id,key,str(value)))
            
            c.executemany(""" INSERT INTO annotation(exec_id,annotation.key,value)
	    VALUES (%s,%s,%s)""",insert_values)
            self.db.commit()
	           
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

    def getExecIdInfo(self, exec_id):
        try:
            c = self.db.cursor()
            c.execute("""SELECT exec.ts_start, exec.ts_end, user
            FROM exec, wf_exec, session
            WHERE exec.wf_exec_id = wf_exec.wf_exec_id 
            AND wf_exec.ss_id = session.ss_id
            AND exec_id = %s""", (exec_id))
            
            row = c.fetchone()
            result = {}
            result['ts_start'] = row[0]
            result['duration'] = row[1] - row[0]
            result['user'] = row[2]
            return result
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

    def getExecIdDetails(self, exec_id):
        try:
            c = self.db.cursor()
            c.execute("""SELECT machine.name, machine.os, machine.architecture, machine.processor,
            machine.ram, session.ip, session.vis_ver
            FROM exec, wf_exec, session, machine
            WHERE exec.wf_exec_id = wf_exec.wf_exec_id 
            AND wf_exec.ss_id = session.ss_id AND session.machine_id = machine.machine_id
            AND exec_id = %s""", (exec_id))
            
            row = c.fetchone()
            result = {}
            result['machine'] = row[0]
            result['os'] = row[1]
            result['architecture'] = row[2]
            result['processor'] = row[3]
            result['ram'] = row[4]
            result['ip'] = row[5]
            result['vis_version'] = row[6]

            return result
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
########################################################################################

import unittest

class TestLogger(unittest.TestCase):
    def test1(self):
        logger = Logger()
        logger.finishSession()

if __name__ == '__main__':
    unittest.main()
