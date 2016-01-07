###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" This file contains classes related to loading and saving a set of
connection objects to an XML file.
It defines the following
classes:
 - ExtConnection
 - DBConnection
 - ExtConnectionList
"""
from __future__ import division

import os
import tempfile
import unittest

from vistrails.core.utils import VistrailsInternalError, abstract
from vistrails.core.utils.enum import enum
from vistrails.core.utils.uxml import named_elements, XMLWrapper
################################################################################

ConnectionType = enum('ConnectionType',
                      ['DB', 'HTTP', 'Unknown'],
                      "Enumeration of Connection Types")

class ExtConnection(object):
    """Stores Information for an External Connection"""
    parseDispatch = {}
    
    def __init__(self, id=-1, name='', host='', type=ConnectionType.Unknown):
        """__init__(id: int,  name: str, host: str, type: ConnectionType)
                    -> ExtConnection
        It creates an external connection. Ignoring the connection type, every
        connection should have at least a name, a hostname and an id """
        self.id = id
        self.name = name
        self.host = host
        self.type = type
        
    def serialize(self, dom, element):
        abstract()

    @staticmethod
    def parse(element):
        type = str(element.getAttribute('type'))
        return ExtConnection.parseDispatch[type](element)

class DBConnection(ExtConnection):
    """Stores Information for Database Connection """
    def __init__(self, id=-1, name='', host='', port=0, user='', passwd='',
                 database='', dbtype=''):
        """__init__(id: int,  name: str, host: str, port: int, username: str,
                    passwd: str, database: str, type:ConnectionType)->DBConnection
           It creates a DBConnection Object
        """
        ExtConnection.__init__(self, id, name, host, ConnectionType.DB)
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database
        self.dbtype = dbtype

    def serialize(self, dom, element):
        """serialize(dom, element) -> None
        Convert this object to an XML representation.
        """
        conn = dom.createElement('connection')
        conn.setAttribute('id', str(self.id))
        conn.setAttribute('name', str(self.name))
        conn.setAttribute('host', str(self.host))
        conn.setAttribute('port',str(self.port))
        conn.setAttribute('user', str(self.user))
        conn.setAttribute('passwd', str(self.passwd))
        conn.setAttribute('database', str(self.database))
        conn.setAttribute('type', str(self.type))
        conn.setAttribute('dbtype', str(self.dbtype))
        element.appendChild(conn)

    def __str__(self):
        """ __str__() -> str - Writes itself as a string """ 
        return """<<id= '%s' name='%s' type='%s' host='%s' 
        user='%s' database='%s' dbtype='%s'>>""" %  (
            self.id,
            self.name,
            self.type,
            self.host,
            self.user,
            self.database,
            self.dbtype)

    @staticmethod
    def parse(element):
        """ parse(element) -> DBConnection
        Parse an XML object representing a DBConnection and returns a
        DBConnection object. 
        
        """
        conn = DBConnection()
        conn.type = ConnectionType.DB
        conn.id = int(element.getAttribute('id'))
        conn.name = str(element.getAttribute('name'))
        conn.host = str(element.getAttribute('host'))
        conn.port = int(element.getAttribute('port'))
        conn.user = str(element.getAttribute('user'))
        conn.passwd = str(element.getAttribute('passwd'))
        conn.database = str(element.getAttribute('database'))
        conn.dbtype = str(element.getAttribute('dbtype'))
        return conn

    def __eq__(self, other):
        """ __eq__(other: DBConnection) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if other is None:
            return False
        if self.type != other.type:
            return False
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.host != other.host:
            return False
        if self.port != other.port:
            return False
        if self.user != other.user:
            return False
        if self.passwd != other.passwd:
            return False
        if self.database != other.database:
            return False
        if self.dbtype != other.dbtype:
            return False
        return True

    def __ne__(self, other):
        return not (self == other)

ExtConnection.parseDispatch[str(ConnectionType.DB)] = DBConnection.parse

class ExtConnectionList(XMLWrapper):
    """Class to store and manage a list of connections.

    """
    _instance = None
    @staticmethod
    def getInstance(*args, **kwargs):
        if ExtConnectionList._instance is None:
            obj = ExtConnectionList(*args, **kwargs)
            ExtConnectionList._instance = obj
        return ExtConnectionList._instance
    
    def __init__(self, filename=''):
        """ __init__() -> ExtConnectionList """
        if not ExtConnectionList._instance:
            self.__connections = {}
            self.changed = False
            self.current_id = 1
            self.filename = filename
            self.load_connections()
            ExtConnectionList._instance = self
        else:
            raise RuntimeError, 'Only one instance of ExtConnectionList is \
allowed!'

    def load_connections(self):
        """load_connections()-> None
        Load connections from its internal filename

        """
        if os.path.exists(self.filename):
            self.parse(self.filename)

    def add_connection(self, conn):
        """add_connection(conn: ExtConnection) -> None
        Adds a connection to the list

        """
        if self.__connections.has_key(conn.id):
            msg = "External Connection '%s' with repeated id" % conn.name
            raise VistrailsInternalError(msg)
        self.__connections[conn.id] = conn
        self.current_id = max(self.current_id, conn.id+1)
        self.serialize()

    def get_connection(self, id):
        """get_connection(id: int) -> ExtConnection
        Returns connection object associated with id

        """
        if self.__connections.has_key(id):
            return self.__connections[id]
        else:
            return None

    def has_connection(self, id):
        """has_connection(id: int) -> Boolean
        Returns True if connection with id exists """
        return self.__connections.has_key(id)

    def find_db_connection(self, host, port, db):
        """find_db_connection(host: str, port: int, db: str) -> id
        Returns the id of the first connection that matches the provided
        parameters. It will return -1 if not found

        """
        for conn in self.__connections.itervalues():
            if conn.host == host and conn.port == port and conn.database == db:
                return conn.id
        return -1
    
    def set_connection(self, id, conn):
        """set_connection(id: int, conn: ExtConnection)- > None
        Updates the connection with id to be conn

        """
        if self.__connections.has_key(id):
            self.__connections[id] = conn
            self.serialize()
            
    def remove_connection(self, id):
        """remove_connection(id: int) -> None 
        Remove connection with id 'id'
        
        """
        if self.__connections.has_key(id):
            del self.__connections[id]
            self.serialize()
        
    def clear(self):
        """ clear() -> None 
        Remove current connections """
        self.__connections.clear()
        self.current_id = 1

    def count(self):
        """count() -> int - Returns the number of connections """
        return len(self.__connections)

    def items(self):
        """ items() -> - Returns the connections """
        return self.__connections.items()

    def parse(self, filename):
        """parse(filename: str) -> None  
        Loads a list of connections from a XML file, appending it to
        self.__connections.
        
        """
        self.open_file(filename)
        root = self.dom.documentElement
        for element in named_elements(root, 'connection'):
            self.add_connection(ExtConnection.parse(element))
        self.refresh_current_id()

    def serialize(self):
        """serialize(filename:str) -> None 
        Writes connection list to given filename.
          
        """
        dom = self.create_document('connections')
        root = dom.documentElement
        
        for conn in self.__connections.values():
            conn.serialize(dom, root)

        self.write_document(root, self.filename)

    def refresh_current_id(self):
        """refresh_current_id() -> None
        Recomputes the next unused id from scratch
        
        """
        self.current_id = max([0] + self.__connections.keys()) + 1

    def get_fresh_id(self):
        """get_fresh_id() -> int - Returns an unused id. """
        return self.current_id


###############################################################################

class TestConnectionList(unittest.TestCase):
    def test1(self):
        """ Exercising writing and reading a file """
        fd, filename = tempfile.mkstemp(prefix='vt_', suffix='_connections.xml')
        os.close(fd)
        try:
            conns = ExtConnectionList.getInstance()
            conns.filename = filename
            conns.clear()
            conn = DBConnection()
            conn.id = 1
            conn.name = 'test'
            conn.host = 'somehost.com'
            conn.port = 1234
            conn.user = 'nobody'
            conn.passwd = '123'
            conn.database = 'anydatabase'
            conn.dbtype = 'MySQL'

            conns.add_connection(conn)

            #reading it again
            conns.clear()
            self.assertEquals(conns.count(),0)
            conns.load_connections()
            self.assertEquals(conns.count(),1)
            newconn = conns.get_connection(1)
            self.assertEqual(conn, newconn)
        finally:
            #remove created file
            os.unlink(filename)

if __name__ == '__main__':
    unittest.main()
