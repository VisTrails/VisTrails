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

from datetime import datetime
import sys
import os
from xml.parsers.expat import ExpatError
from xml.dom.minidom import parse, parseString, getDOMImplementation

from db.domain import DBVistrail, DBWorkflow, DBLog
import db.services.vistrail
from db.versions import getVersionDAO, currentVersion, translateVistrail, \
    getVersionSchemaDir

myconnections = {}

def openDBConnection(config):
    import MySQLdb
    global myconnections
    
    if config is None:
        msg = "You need to provide valid config dictionary"
        raise Exception(msg)
    try:
        if config.has_key('id'):
            id = config['id']
            del config['id']
        dbConnection = MySQLdb.connect(**config)
        myconnections[id] = dbConnection
        return dbConnection
    except MySQLdb.Error, e:
        # should have a DB exception type
        msg = "MySQL returned the following error %d: %s" % (e.args[0],
                                                             e.args[1])
        raise Exception(msg)
    
def test_db_connection(config):
    """testDBConnection(config: dict) -> None
    Tests a connection raising an exception in case of error.
    
    """
    import MySQLdb
    try:
        dbConnection = MySQLdb.connect(**config)
        closeDBConnection(dbConnection)
    
    except MySQLdb.Error, e:
        # should have a DB exception type
        msg = "MySQL returned the following error %d: %s" % (e.args[0],
                                                             e.args[1])
        raise Exception(msg)

def get_db_vistrail_list(config):
    result = []
    
    import MySQLdb
    
    db = openDBConnection(config)

    #FIXME Create a DBGetVistrailListSQLDAOBase for this
    # and maybe there's another way to build this query
    command = """SELECT v.id, v.name, a.date, a.user
    FROM vistrail v, action a,
    (SELECT a.vt_id, MAX(a.date) as recent, a.user
    FROM action a
    GROUP BY vt_id) latest
    WHERE v.id = latest.vt_id 
    AND a.vt_id = v.id
    AND a.date = latest.recent 
    """

    try:
        c = db.cursor()
        c.execute(command)
        rows = c.fetchall()
        result = rows
        c.close()
        
    except MySQLdb.Error, e:
        print "ERROR: Couldn't get list of vistrails from db (%d : %s)" % (
                e.args[0], e.args[1])
            
    return result

def openXMLFile(filename):
    try:
        return parse(filename)
    except ExpatError, e:
        msg = 'XML parse error at line %s, col %s: %s' % \
            (e.lineno, e.offset, e.code)
        raise Exception(msg)

def writeXMLFile(filename, dom):
    output = file(filename, 'w')
    dom.writexml(output, '','  ','\n')
    output.close()

def setupDBTables(dbConnection, version=None):
    import MySQLdb

    schemaDir = getVersionSchemaDir(version)
    try:
        # delete tables
        print "dropping tables"
        
        c = dbConnection.cursor()
        f = open(os.path.join(schemaDir, 'vistrails_drop.sql'))
        dbScript = f.read()
        c.execute(dbScript)
        c.close()
        f.close()

        # create tables
        print "creating tables"
        
        c = dbConnection.cursor()
        f = open(os.path.join(schemaDir, 'vistrails.sql'))
        dbScript = f.read()
        c.execute(dbScript)
        f.close()
        c.close()
    except MySQLdb.Error, e:
        raise Exception("unable to create tables: " + str(e))

def closeDBConnection(dbConnection):
    if dbConnection is not None:
        dbConnection.close()

def openVistrailFromXML(filename):
    """openVistrailFromXML(filename) -> Vistrail"""
    dom = openXMLFile(filename)
    version = getVersionForXML(dom.documentElement)
    if version != currentVersion:
        vistrail = importVistrailFromXML(filename, version)
    else:
        vistrail = readXMLObjects(DBVistrail.vtType, dom.documentElement)[0]
    db.services.vistrail.updateIdScope(vistrail)
    return vistrail

def open_from_db(config, vt_id):
    """open_from_db(config: dict, vt_id:int) -> DBVistrail
    Opens a vistrail using config to open a connection and the vistrail id

    """
    global myconnections
    id = -1
    if config.has_key('id'):
        id = config['id']
        del config['id']
    if myconnections.has_key(id):
        db = myconnections[id]
    else:
        db = openDBConnection(config)
        if id != -1:
            myconnections[id] = db

    vt = openVistrailFromDB(db, vt_id)
    setDBParameters(vt, config)
    return vt

def openVistrailFromDB(dbConnection, id):
    """openVistrailFromDB(dbConnection, id) -> Vistrail """

    if dbConnection is None:
        msg = "Need to call openDBConnection() before reading"
        raise Exception(msg)
    vt = readSQLObjects(dbConnection, DBVistrail.vtType, id)[0]
    # not sure where this really should be done...
    # problem is that db reads the add ops, then change ops, then delete ops
    # need them ordered by their id
    for db_action in vt.db_get_actions():
        db_action.db_operations.sort(lambda x,y: cmp(x.db_id, y.db_id))
    db.services.vistrail.updateIdScope(vt)
    return vt

def setDBParameters(vistrail, config):
    vistrail.db_dbHost = config['host']
    vistrail.db_dbPort = config['port']
    vistrail.db_dbName = config['db']

def saveVistrailToXML(vistrail, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([vistrail], dom)
    root.setAttribute('version', currentVersion)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/vistrail.xsd')
    dom.appendChild(root)
    writeXMLFile(filename, dom)

def save_to_db(conn_id, vistrail, config=None):
    """save_to_db(conn_id: int, vistrail: Vistrail) -> None
    save the vistrail using the connection identified by conn_id

    """
    global myconnections
    if myconnections.has_key(conn_id):
        db = myconnections[conn_id]
        saveVistrailToDB(vistrail,db)
    else:
        msg = "Need to open a connection before" 
        raise Exception(msg)
    
def saveVistrailToDB(vistrail, dbConnection):
    vistrail.db_version = currentVersion
    writeSQLObjects(dbConnection, [vistrail])

def openWorkflowFromXML(filename):
    dom = openXMLFile(filename)
    return readXMLObjects(DBWorkflow.vtType, dom.documentElement)[0]

def openWorkflowFromSQL(dbConnection, id):
    if dbConnection is None:
        msg = "Need to call openDBConnection() before reading"
        raise Exception(msg)
    readSQLObjects(dbConnection, DBWorkflow.vtType, id)[0]

def getWorkflowFromXML(str):
    dom = parseString(str)
    return readXMLObjects(DBWorkflow.vtType, dom.documentElement)[0]

def saveWorkflowToXML(workflow, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    dom.appendChild(root)
    writeXMLFile(filename, dom)

def getWorkflowAsXML(workflow):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    dom.appendChild(root)
    return dom.toxml()
    
def openLogFromXML(filename):
    dom = openXMLFile(filename)
    return readXMLObjects(DBLog.vtType, dom.documentElement)[0]

def openLogFromSQL(dbConnection, id):
    if dbConnection is None:
        msg = "Need to call openDBConnection() before reading"
        raise Exception(msg)
    return readSQLObjects(dbConnection, DBLog.vtType, id)[0]

def saveLogToXML(log, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([log], dom.documentElement)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    dom.appendChild(root)
    writeXMLFile(filename, dom)

def readXMLObjects(vtType, node):
    daoList = getVersionDAO(currentVersion)
    result = []
    result.append(daoList['xml'][vtType].fromXML(node))
    return result

def writeXMLObjects(objectList, dom):
    daoList = getVersionDAO(currentVersion)
    for object in objectList:
        root = daoList['xml'][object.vtType].toXML(object, dom)
    return root

def readSQLObjects(dbConnection, vtType, id):
    daoList = getVersionDAO(currentVersion)
    return daoList['sql'][vtType].fromSQL(dbConnection, id)

def writeSQLObjects(dbConnection, objectList):
    daoList = getVersionDAO(currentVersion)
    for object in objectList:
        daoList['sql'][object.vtType].toSQL(dbConnection, object)

def importXMLObjects(vtType, node, version):
    daoList = getVersionDAO(version)
    result = []
    result.append(daoList['xml'][vtType].fromXML(node))
    return result

def importSQLObjects(dbConnection, vtType, id, version):
    daoList = getVersionDAO(version)
    return daoList['xml'][vtType].fromSQL(dbConnection, id)

def importVistrailFromXML(filename, version):
    dom = openXMLFile(filename)
    vistrail = importXMLObjects(DBVistrail.vtType, 
                                dom.documentElement, version)[0]
    return translateVistrail(vistrail, version)

def importVistrailFromSQL(dbConnection, id, version):
    if dbConnection is None:
        msg = "Need to call openDBConnection() before reading"
        raise Exception(msg)
    vistrail = importSQLObjects(dbConnection, Vistrail.vtType, id, version)[0]
    #        return self.translateVistrail(vistrail)
    return vistrail

def getVersionForXML(node):
    try:
        version = node.attributes.get('version')
        if version is not None:
            return version.value
    except KeyError:
        pass
    msg = "Cannot find version information"
    raise Exception(msg)

def getCurrentTime(dbConnection=None):
    timestamp = datetime.now()
    if dbConnection is not None:
        try:
            c = dbConnection.cursor()
            c.execute("SELECT NOW()")
            row = c.fetchone()
            if row:
                timestamp = row[0]
            c.close()
        except MySQLdb.Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])

    return timestamp


##############################################################################
# Testing

import unittest
import random

class TestDBIO(unittest.TestCase):
    def test1(self):
        """test importing an xml file"""
        import core.system
        import os
        vistrail = openVistrailFromXML( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy.xml'))
        assert vistrail is not None
        
    def test2(self):
        """test importing an xml file"""
        import core.system
        import os
        vistrail = openVistrailFromXML( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.xml'))
        assert vistrail is not None

