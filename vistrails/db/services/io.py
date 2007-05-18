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

import sys
import os
from xml.parsers.expat import ExpatError
from xml.dom.minidom import parse, getDOMImplementation

from db.domain import DBVistrail, DBWorkflow, DBLog
from db.versions import getVersionDAO, currentVersion, translateVistrail, \
    getVersionSchemaDir

def openDBConnection(config=None):
    import MySQLdb
    if config is None:
        # get settings from config
        import gui.application
        startup = gui.application.VistrailsApplication.vistrailsStartup
        config = {'host': startup.configuration.db.host,
                  'port': startup.configuation.db.port,
                  'user': startup.configuration.db.user,
                  'passwd': startup.configuration.db.passwd,
                  'db': startup.configuration.db.database}

    try:
        dbConnection = MySQLdb.connect(**config)
        return dbConnection
    except MySQLdb.Error, e:
        # should have a DB exception type
        msg = "MySQL returned the following error %d: %s" % (e.args[0], e.args[1])
        raise Exception(msg)

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
        return importVistrailFromXML(filename, version)
    else:
        return readXMLObjects(DBVistrail.vtType, dom.documentElement)[0]

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

def saveWorkflowToXML(workflow, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    dom.appendChild(root)
    writeXMLFile(filename, dom)

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

