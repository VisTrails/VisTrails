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
from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

import sys
import os

from db import VistrailsDBException
from db.domain import DBVistrail, DBWorkflow, DBLog
import db.services.vistrail
from db.versions import getVersionDAO, currentVersion, translateVistrail, \
    getVersionSchemaDir

def open_db_connection(config):
    import MySQLdb

    if config is None:
        msg = "You need to provide valid config dictionary"
        raise Exception(msg)
    try:
        db_connection = MySQLdb.connect(**config)
        return db_connection
    except MySQLdb.Error, e:
        # should have a DB exception type
        msg = "cannot open connection (%d: %s)" % (e.args[0], e.args[1])
        raise VistrailsDBException(msg)

def close_db_connection(db_connection):
    if db_connection is not None:
        db_connection.close()

def test_db_connection(config):
    """testDBConnection(config: dict) -> None
    Tests a connection raising an exception in case of error.
    
    """
    import MySQLdb

    try:
        dbConnection = MySQLdb.connect(**config)
        close_db_connection(dbConnection)
    except MySQLdb.Error, e:
        msg = "connection test failed (%d: %s)" % (e.args[0], e.args[1])
        raise VistrailsDBException(msg)

def get_db_vistrail_list(config):
    
    import MySQLdb

    result = []    
    db = open_db_connection(config)

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
        msg = "Couldn't get list of vistrails from db (%d : %s)" % (e.args[0], 
                                                                    e.args[1])
        raise VistrailsDBException(msg)
    return result

def setup_db_tables(db_connection, version=None):
    import MySQLdb

    schemaDir = getVersionSchemaDir(version)
    try:
        # delete tables
        c = db_connection.cursor()
        f = open(os.path.join(schemaDir, 'vistrails_drop.sql'))
        db_script = f.read()
        c.execute(db_script)
        c.close()
        f.close()

        # create tables        
        c = db_connection.cursor()
        f = open(os.path.join(schemaDir, 'vistrails.sql'))
        db_script = f.read()
        c.execute(db_script)
        f.close()
        c.close()
    except MySQLdb.Error, e:
        raise VistrailsDBException("unable to create tables: " + str(e))

def open_vistrail_from_xml(filename):
    """open_vistrail_from_xml(filename) -> Vistrail"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    vistrail = daoList.open_from_xml(filename, DBVistrail.vtType)
    vistrail = translateVistrail(vistrail, version)
    db.services.vistrail.updateIdScope(vistrail)
    return vistrail

def open_vistrail_from_db(dbConnection, id):
    """open_vistrail_from_db(dbConnection, id) -> Vistrail """

    if dbConnection is None:
        msg = "Need to call open_db_connection() before reading"
        raise Exception(msg)
    vt = readSQLObjects(dbConnection, DBVistrail.vtType, id)[0]
    # not sure where this really should be done...
    # problem is that db reads the add ops, then change ops, then delete ops
    # need them ordered by their id
    for db_action in vt.db_get_actions():
        db_action.db_operations.sort(lambda x,y: cmp(x.db_id, y.db_id))
    db.services.vistrail.updateIdScope(vt)
    return vt

def save_vistrail_to_xml(vistrail, filename):
    daoList = getVersionDAO(currentVersion)
    daoList.save_to_xml(vistrail, filename)
    
def save_vistrail_to_db(vistrail, dbConnection):
    vistrail.db_version = currentVersion
    writeSQLObjects(dbConnection, [vistrail])

def open_workflow_from_xml(filename):
    dom = parse_xml_file(filename)
    return readXMLObjects(DBWorkflow.vtType, dom.documentElement)[0]

def openWorkflowFromSQL(dbConnection, id):
    if dbConnection is None:
        msg = "Need to call open_db_connection() before reading"
        raise Exception(msg)
    readSQLObjects(dbConnection, DBWorkflow.vtType, id)[0]

def serialize(object):
    daoList = getVersionDAO(currentVersion)
    return daoList.serialize(object)

def unserialize(str, obj_type):
    daoList = getVersionDAO(currentVersion)
    return daoList.unserialize(str, obj_type)

def getWorkflowFromXML(str):
    dom = parseString(str)
    return readXMLObjects(DBWorkflow.vtType, dom.documentElement)[0]

def save_workflow_to_xml(workflow, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    write_xml_file(filename, dom)

def getWorkflowAsXML(workflow):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    return dom.toxml()
    
def openLogFromXML(filename):
    dom = parse_xml_file(filename)
    return readXMLObjects(DBLog.vtType, dom.documentElement)[0]

def openLogFromSQL(dbConnection, id):
    if dbConnection is None:
        msg = "Need to call open_db_connection() before reading"
        raise Exception(msg)
    return readSQLObjects(dbConnection, DBLog.vtType, id)[0]

def saveLogToXML(log, filename):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([log], dom)
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    write_xml_file(filename, dom)

def readXMLObjects(vtType, node):
    daoList = getVersionDAO(currentVersion)
    result = []
    result.append(daoList['xml'][vtType].fromXML(node))
    return result

def writeXMLObjects(objectList, dom, node=None):
    daoList = getVersionDAO(currentVersion)
    # FIXME only works for list of length 1
    object = objectList[0]
    res_node = daoList['xml'][object.vtType].toXML(object, dom, node)
    return res_node

def readSQLObjects(dbConnection, vtType, id):
    dao_list = getVersionDAO(currentVersion)

    all_objects = {}
    res = []
    global_props = {'id': id}
    all_objects.update(dao_list['sql'][vtType].get_sql_columns(dbConnection, 
                                                               global_props))
    res = all_objects.values()
    del global_props['id']

    for dao in dao_list['sql'].itervalues():
        if dao == dao_list['sql'][vtType]:
            continue
        all_objects.update(dao.get_sql_columns(dbConnection, global_props))
    for obj in all_objects.values():
        dao_list['sql'][obj.vtType].from_sql_fast(obj, all_objects)
    return res

def writeSQLObjects(dbConnection, objectList):
    dao_list = getVersionDAO(currentVersion)

    for object in objectList:
        children = object.db_children()
        children.reverse()
        global_props = {}
        for (child, _, _) in children:
            dao_list['sql'][child.vtType].set_sql_columns(dbConnection, child, 
                                                          global_props)
            dao_list['sql'][child.vtType].to_sql_fast(child)
            child.is_dirty = False
            child.is_new = False

def importXMLObjects(vtType, node, version):
    daoList = getVersionDAO(version)
    result = []
    result.append(daoList['xml'][vtType].fromXML(node))
    return result

def importSQLObjects(dbConnection, vtType, id, version):
    daoList = getVersionDAO(version)
    return daoList['xml'][vtType].fromSQL(dbConnection, id)

def importVistrailFromXML(filename, version):
    dom = parse_xml_file(filename)
    vistrail = importXMLObjects(DBVistrail.vtType, 
                                dom.documentElement, version)[0]
    return translateVistrail(vistrail, version)

def importVistrailFromSQL(dbConnection, id, version):
    if dbConnection is None:
        msg = "Need to call open_db_connection() before reading"
        raise Exception(msg)
    vistrail = importSQLObjects(dbConnection, Vistrail.vtType, id, version)[0]
    #        return self.translateVistrail(vistrail)
    return vistrail

def get_version_for_xml(root):
    version = root.get('version', None)
    if version is not None:
        return version
    msg = "Cannot find version information"
    raise VistrailsDBException(msg)

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

class TestDBIO(unittest.TestCase):
    def test1(self):
        """test importing an xml file"""
        import core.system
        import os
        vistrail = open_vistrail_from_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy.xml'))
        assert vistrail is not None
        
    def test2(self):
        """test importing an xml file"""
        import core.system
        import os
        vistrail = open_vistrail_from_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.xml'))
        assert vistrail is not None

