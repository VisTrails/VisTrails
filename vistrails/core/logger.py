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
""" File responsible for logging workflows
   It defines the class Logger
 """
import getpass
import socket
from core import system
import platform
from datetime import datetime

_nologger = True
MySQLdb = None

##############################################################################
# DummyLogger

class DummyLogger(object):
    """DummyLogger is a class that has the entire interface for a logger
    but simply ignores the calls."""
    def start_workflow_execution(*args, **kwargs):
        pass
    def start_module_execution(*args, **kwargs):
        pass
    def finish_module_execution(*args, **kwargs):
        pass
    def insert_annotation_DB(*args, **kwargs):
        pass
    def finish_workflow_execution(*args, **kwargs):
        pass
    def finish_session(*args, **kwargs):
        pass
    
##############################################################################
# Logger

class Logger(object):
    """ Class that provides an interface for logging workflows. """
    def __init__(self):
        """ gather all the runtime information (such as username, machine name,
        machine IP, vistrails version) and init a session on the database.

        """
        self.username = getpass.getuser()
        self.machine_name = socket.getfqdn()
        self.machine_id = -1 #it will be retrieved from DB
        self.os = system.systemType
        self.architecture = self.extract_bit_number(platform.architecture()[0]) 
        #the following ugly expression avoids getting '127.0.0.1' 
        self.processor = platform.processor()
        if not self.processor:
            self.processor = 'n/a'
        self.ip = self.get_ip_address()
        self.vist_ver = system.vistrails_version()
        self.ram = system.guess_total_memory()/(1024*1024)
        self.get_settings_from_app()
        self.ssid = -1
        self.vistrails_map = {} #maps locators to vistrails_id in db
	self.wf_dict = {} #vistrails_id : {version_number:wf_exec_id}
        self.mod_dict = {}#wf_exec_id : {module_id: exec_id}
        self.init_session()

    def get_ip_address(self):
        """ get_ip_address() -> str
        Gets current IP address trying to avoid the IPv6 interface """
	info = socket.getaddrinfo(socket.gethostname(), None)
	for i in info:
	    if len(i[4][0]) <= 15:
		return i[4][0]
	else:
	    return '0.0.0.0'

    def extract_bit_number(self, bitString):
        """ self.extract_bit_number(bitString) -> int 
        Given a string with a number followed by the word bit, it extracts only
        the number.
        """
        
        if bitString.endswith('bit'):
            return int(bitString[:-3])
        else:
            return 32 #default value 
    
    def create_DB_connection(self):
        """ create_DB_connection() -> MySQLdb.connection 
        Creates a database connection 
        
        """
        try:
            db = MySQLdb.connect(host=self.dbHost, 
                                 port=self.dbPort,
                                 user=self.dbUser,
                                 passwd=self.dbPasswd,
                                 db=self.dbName)
        except MySQLdb.Error, e:
            msg = "MySQL returned de following error %d: %s" % (e.args[0], e.args[1])
            raise Exception(msg)
        return db

    def get_settings_from_app(self):
        """ self.get_settings_from_app()->None 
        Get information from configuration.logger in vis_application.py 
        
        """
        import gui.application
        app = gui.application.VistrailsApplication 
        self.dbHost = app.configuration.logger.dbHost
        self.dbPort = app.configuration.logger.dbPort
        self.dbUser = app.configuration.logger.dbUser
        self.dbPasswd = app.configuration.logger.dbPasswd
        self.dbName = app.configuration.logger.dbName

    def init_session(self):
        """ init_session() -> None - 
        Init a log session keeping the session on self.ssid 

        """
        self.ssid = -1
        self.vistrails_map = {} 
	self.wf_dict = {} 
        self.mod_dict = {}
        self.db = self.create_DB_connection()
        #check if machine_id is there
        self.machine_id = self.get_machine_id_DB()
        if self.machine_id == -1:
            self.machine_id = self.insert_machine_DB()
        self.ssid = self.insert_session_id_DB()
        
    def finish_session(self):
        """ self.finish_session()->None 
        Finish Log session """ 
        if self.ssid != -1:
            try:
                timestamp = self.get_current_time_DB()
                c = self.db.cursor()
                c.execute("""UPDATE session
                SET ts_end = %s 
                WHERE ss_id = %s""", (timestamp,self.ssid))
                self.db.commit()
            except MySQLdb.Error, e:
                print " Logger Error %d: %s" % (e.args[0], e.args[1])
            c.close()
            self.db.close()

    def get_machine_id_DB(self):
        """ get_machine_id_DB() -> int 
        Get machine id from db given machine name, os, architecture,
        processor and memory. Return -1 if not found """
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
            AND ram = %s """, (self.machine_name, self.os, 
                               self.architecture, self.processor, self.ram))
            row = c.fetchone()
            if row:
                result = row[0]

        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

        return result

    def insert_machine_DB(self):
        """ self.insert_machine_DB() -> int 
        Insert machine information into the database and return the 
        machine_id 

        """
        result = -1
        try:
            c = self.db.cursor()
            c.execute("""
            INSERT INTO machine(name,os,architecture,processor,ram)
            VALUES(%s,%s,%s,%s,%s) """, (self.machine_name, self.os, 
                                         self.architecture,
                                         self.processor, self.ram))
            self.db.commit()
            result = self.get_machine_id_DB()
            
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        c.close()
        return result

    def get_vistrails_id_DB(self, vistrailsName):
        """ self.get_vistrails_id_DB(vistrailsName)->int 
        Get vistrails_id from database given full path of a vistrails. 
        
        """
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
    
    def insert_vistrails_DB(self, vistrailsName):
        """ self.insert_vistrails_DB() -> int 
        Insert vistrailsName information into the database and return the 
        vistrails_id 
        
        """
        result = -1
        try:
            c = self.db.cursor()
            c.execute("""
            INSERT INTO vistrails(vistrails_name)
            VALUES(%s) """, (vistrailsName))
            self.db.commit()
            result = self.get_vistrails_id_DB(vistrailsName)
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        c.close()
        return result
    
    def insert_session_id_DB(self):
        """ self.insert_session_id_DB()->int It creates an entry in the 
        database and return the ss_id of the new entry."""
        result = -1
        try:
            timestamp = self.get_current_time_DB()
            c = self.db.cursor()
            c.execute("""
            INSERT INTO session(user,machine_id,ip,vis_ver, ts_start)
            VALUES(%s,%s,%s,%s,%s) """, (self.username, self.machine_id,
                                      self.ip, self.vist_ver, timestamp.strftime("%Y-%m-%d %H:%M:%S")))
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
        
    def get_current_time_DB(self):
        """ get_current_time_DB() -> datetime.datetime 
        Get current time on database to keep consistency across applications

        """
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
        
    def start_workflow_execution(self, locator, version_number):
        """ start_workflow_execution(locator: VistrailLocator,
                                     version_number)->None 
        Log the start of a workflow execution 
        
        """
        try:
            #vistrails information
	    if self.vistrails_map.has_key(locator.name):
		vistrails_id = self.vistrails_map[locator.name]
	    else:
		vistrails_id = self.get_vistrails_id_DB(locator.name) 
		if vistrails_id == -1:
		    vistrails_id = self.insert_vistrails_DB(locator.name)
		self.vistrails_map[locator.name] = vistrails_id

            ts = self.get_current_time_DB()
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
		
		if not self.wf_dict.has_key(vistrails_id):
		    dict = {}
		    dict[version_number] = wf_exec_id
		    self.wf_dict[vistrails_id] = dict
		else:
		    d = self.wf_dict[vistrails_id]
		    d[version_number] = wf_exec_id
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
      
    def finish_workflow_execution(self, locator, version_number):
        """ finish_workflow_execution(locator: VistrailLocator,
                                       version_number) -> None 
        Log the end of a workflow execution
        
        """
	try:
	    vistrails_id = self.vistrails_map[locator.name]
	    wf_exec_id = self.wf_dict[vistrails_id][version_number]
	    
	    timestamp = self.get_current_time_DB()
	    c = self.db.cursor()
	    c.execute("""UPDATE wf_exec
	    SET ts_end = %s 
	    WHERE wf_exec_id = %s""", (timestamp,wf_exec_id))
            self.db.commit()
	    del self.wf_dict[vistrails_id][version_number]
	except MySQLdb.Error, e:
	    print "Logger Error %d: %s" % (e.args[0], e.args[1])
		
	c.close()

    def start_module_execution(self, locator, version_number, module_id, 
                             module_name):
        """ start_module_execution(locator: VistrailLocator,
                                   version_number, module_id, 
                                 module_name) -> None
        Log the start of the execution of a module

        """
	try:
	    vistrails_id = self.vistrails_map[locator.name]
	    wf_exec_id = self.wf_dict[vistrails_id][version_number]

            ts = self.get_current_time_DB()
            c = self.db.cursor()
            c.execute(""" INSERT INTO 
            exec(ts_start,wf_exec_id,module_id,module_name)
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
		
		if not self.mod_dict.has_key(wf_exec_id):
		    dict = {}
		    dict[module_id] = exec_id
		    self.mod_dict[wf_exec_id] = dict
		else:
		    d = self.mod_dict[wf_exec_id]
		    d[module_id] = exec_id
        
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()
   
    def finish_module_execution(self, locator, version_number, module_id):
        """ finish_module_execution(locator, version_number, 
                                  module_id) -> None
        Log the end of the execution of a module

        """
        try:
	    vistrails_id = self.vistrails_map[locator.name]
	    wf_exec_id = self.wf_dict[vistrails_id][version_number]
            exec_id = self.mod_dict[wf_exec_id][module_id]

	    timestamp = self.get_current_time_DB()
	    c = self.db.cursor()
	    c.execute("""UPDATE exec
	    SET ts_end = %s 
	    WHERE exec_id = %s""", (timestamp,exec_id))
            self.db.commit()
	    del self.mod_dict[wf_exec_id][module_id]

	except MySQLdb.Error, e:
	    print "Logger Error %d: %s" % (e.args[0], e.args[1])
		
	c.close()


    def insert_annotation_DB(self, locator, version_number, module_id, annot_dict):
        """ insert_annotation_DB(locator, version_number, 
                               module_id, annot_dict:dict[str:str]) -> None
        Log a module annotation (key, value) on the database"""
        try:
	    vistrails_id = self.vistrails_map[locator.name]
	    wf_exec_id = self.wf_dict[vistrails_id][version_number]
            exec_id = self.mod_dict[wf_exec_id][module_id]

            insert_values = []
            c = self.db.cursor()
            for (key,value) in annot_dict.iteritems():
                insert_values.append((exec_id,key,str(value)))
            
            c.executemany(""" INSERT INTO 
            annotation(exec_id,annotation.key,value)
	    VALUES (%s,%s,%s)""",insert_values)
            self.db.commit()
	           
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])
        
        c.close()

    def get_exec_id_info(self, exec_id):
        """ get_exec_id_info(exec_id) -> dict 
        Returns a dictionary containing execution time_start, duration 
        and username of a execution """ 
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

    def get_exec_id_details(self, exec_id):
        """ get_exec_id_details(exec_id) -> dict 
        Get more dataied information of a workflow execution.
        
        """
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

    __instance = None
    
    @staticmethod
    def get():
        if Logger.__instance:
            return Logger.__instance
        if _nologger:
            Logger.__instance = DummyLogger()
        else:
            import MySQLdb as _MySQLdb
            global MySQLdb
            MySQLdb = _MySQLdb
            Logger.__instance = Logger()
        return Logger.__instance
   
################################################################################
