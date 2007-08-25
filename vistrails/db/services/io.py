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

def openDBConnection(config):
    import MySQLdb

    if config is None:
        msg = "You need to provide valid config dictionary"
        raise Exception(msg)
    try:
        dbConnection = MySQLdb.connect(**config)
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
    
    import MySQLdb

    result = []    
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

def writeXMLFile(filename, dom, prettyprint=True):
    output = file(filename, 'w')
    if prettyprint:
        dom.writexml(output, '','  ','\n')
    else:
        dom.writexml(output)
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
        vistrail.db_version = currentVersion
    else:
        vistrail = readXMLObjects(DBVistrail.vtType, dom.documentElement)[0]
    db.services.vistrail.updateIdScope(vistrail)
    dom.unlink()
    return vistrail

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

def saveVistrailToXML(vistrail, filename):

    # FIXME dakoop (enhancement) -- if save dom, can save quicker
    #     dom = vistrail.vt_origin
    #     writeXMLObjects([vistrail], dom, dom.documentElement)
    #     writeXMLFile(filename, dom)

    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([vistrail], dom)
    dom.appendChild(root)
    root.setAttribute('version', currentVersion)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                  'http://www.vistrails.org/vistrail.xsd')
    writeXMLFile(filename, dom)
    dom.unlink()
    
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
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    writeXMLFile(filename, dom)

def getWorkflowAsXML(workflow):
    dom = getDOMImplementation().createDocument(None, None, None)
    root = writeXMLObjects([workflow], dom)
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
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
    root = writeXMLObjects([log], dom)
    dom.appendChild(root)
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xsi:schemaLocation', 
                      'http://www.vistrails.org/workflow.xsd')
    writeXMLFile(filename, dom)

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
# Locators

class BaseLocator(object):

    def load(self):
        pass # returns a vistrail

    def save(self, vistrail):
        pass # saves a vistrail in the given place

    def is_valid(self):
        pass # Returns true if locator refers to a valid vistrail

    def save_temporary(self, vistrail):
        pass # Saves a temporary file (useful for making crashes less horrible)

    def clean_temporaries(self):
        pass # Cleans up temporary files

    def has_temporaries(self):
        pass # True if temporaries are present

    @staticmethod
    def load_from_gui(parent_widget):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for loading a file

    @staticmethod
    def save_from_gui(parent_widget, locator):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for saving a file

    def __eq__(self, other):
        pass # Implement equality

    def __eq__(self, other):
        pass # Implement nonequality


class XMLFileLocator(BaseLocator):

    def __init__(self, filename):
        self._name = filename

    def load(self):
        from core.vistrail.vistrail import Vistrail
        fname = self._find_latest_temporary()
        if fname:
            vistrail = openVistrailFromXML(fname)
        else:
            vistrail = openVistrailFromXML(self._name)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save(self, vistrail):
        saveVistrailToXML(vistrail, self._name)
        vistrail.locator = self
        # Only remove the temporaries if save succeeded!
        self.clean_temporaries()

    def save_temporary(self, vistrail):
        fname = self._find_latest_temporary()
        new_temp_fname = self._next_temporary(fname)
        saveVistrailToXML(vistrail, new_temp_fname)

    def is_valid(self):
        return os.path.isfile(self._name)

    def _get_name(self):
        return self._name
    name = property(_get_name)

    ##########################################################################

    def _iter_temporaries(self, f):
        """_iter_temporaries(f): calls f with each temporary file name, in
        sequence.

        """
        latest = None
        current = 0
        while True:
            fname = self._name + '_tmp_' + str(current)
            if os.path.isfile(fname):
                f(fname)
                current += 1
            else:
                break

    def clean_temporaries(self):
        """_remove_temporaries() -> None

        Erases all temporary files.

        """
        def remove_it(fname):
            os.unlink(fname)
        self._iter_temporaries(remove_it)

    def has_temporaries(self):
        return self._find_latest_temporary() is not None

    def _find_latest_temporary(self):
        """_find_latest_temporary(): String or None.

        Returns the latest temporary file saved, if it exists. Returns
        None otherwise.
        
        """
        latest = [None]
        def set_it(fname):
            latest[0] = fname
        self._iter_temporaries(set_it)
        return latest[0]
        
    def _next_temporary(self, temporary):
        """_find_latest_temporary(string or None): String

        Returns the next suitable temporary file given the current
        latest one.

        """
        if temporary == None:
            return self._name + '_tmp_0'
        else:
            split = temporary.rfind('_')+1
            base = temporary[:split]
            number = int(temporary[split:])
            return base + str(number+1)

    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.db.services.io as io
        return io.get_load_xml_file_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.db.services.io as io
        return io.get_save_xml_file_locator_from_gui(parent_widget, locator)

    def __eq__(self, other):
        if type(other) != XMLFileLocator:
            return False
        return self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)


class DBLocator(BaseLocator):

    connections = {}

    def __init__(self, host, port, database, user, passwd, name=None,
                 vistrail_id=None, connection_id=None):
        self._host = host
        self._port = port
        self._db = database
        self._user = user
        self._passwd = passwd
        self._vt_name = name
        self._vt_id = vistrail_id
        self._conn_id = connection_id

    def _get_host(self):
        return self._host
    host = property(_get_host)

    def _get_port(self):
        return self._port
    port = property(_get_port)

    def _get_vistrail_id(self):
        return self._vt_id
    vistrail_id = property(_get_vistrail_id)

    def _get_connection_id(self):
        return self._conn_id
    connection_id = property(_get_connection_id)
    
    def _get_name(self):
        return self._host + ':' + str(self._port) + ':' + self._db + ':' + \
            self._vt_name
    name = property(_get_name)

    def get_connection(self):
        if self._conn_id is not None \
                and DBLocator.connections.has_key(self._conn_id):
            connection = DBLocator.connections[self._conn_id]
        else:
            config = {'host': self._host,
                      'port': self._port,
                      'db': self._db,
                      'user': self._user,
                      'passwd': self._passwd}
            connection = openDBConnection(config)
            if self._conn_id is None:
                if len(DBLocator.connections.keys()) == 0:
                    self._conn_id = 1
                else:
                    self._conn_id = max(DBLocator.connections.keys()) + 1
            DBLocator.connections[self._conn_id] = connection
        return connection

    def load(self):
        from core.vistrail.vistrail import Vistrail
        connection = self.get_connection()
        vistrail = openVistrailFromDB(connection, self.vistrail_id)
        Vistrail.convert(vistrail)
        self._vt_name = vistrail.db_name
        vistrail.locator = self
        return vistrail

    def save(self, vistrail):
        connection = self.get_connection()
        vistrail.db_name = self._vt_name
        saveVistrailToDB(vistrail, connection)
        self._vt_id = vistrail.db_id
        vistrail.locator = self

    ##########################################################################
        
    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.db.services.io as io
        return io.get_load_db_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.db.services.io as io
        return io.get_save_db_locator_from_gui(parent_widget, locator)

    def __eq__(self, other):
        if type(other) != DBLocator:
            return False
        return (self._host == other._host and
                self._port == other._port and
                self._db == other._db and
                self._user == other._user and
                self._vt_name == other._vt_name and
                self._vt_id == other._vt_id)

    def __ne__(self, other):
        return not self.__eq__(other)


##############################################################################
# Testing

import unittest

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

