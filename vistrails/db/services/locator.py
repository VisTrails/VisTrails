###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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

import os.path
import core.configuration
import core.system
from db.services import io
from db.services.io import SaveBundle
from db.domain import DBVistrail
import urllib
import urlparse
import cgi
from db import VistrailsDBException
from core import debug
from core.system import get_elementtree_library, systemType

ElementTree = get_elementtree_library()
import hashlib
from time import strptime
from datetime import datetime

class BaseLocator(object):

    def load(self):
        pass # returns an object

    def save(self, obj, do_copy=True, version=None):
        pass # saves an object in the given place

    def save_as(self, obj, version=None):
        return self.save(obj, True, version) # calls save by default

    def close(self):
        pass # closes locator

    def is_valid(self):
        pass # Returns true if locator refers to a valid object

    def save_temporary(self, obj):
        pass # Saves a temporary file (useful for making crashes less horrible)

    def clean_temporaries(self):
        pass # Cleans up temporary files

    def has_temporaries(self):
        pass # True if temporaries are present

    def serialize(self, dom, element):
        pass #Serializes this locator to XML

    def to_xml(self, node=None): #ElementTree port od serialize
        pass
    
    @staticmethod
    def parse(element):
        pass #Parse an XML object representing a locator and returns a Locator
    
    @staticmethod
    def from_url(url):
        # FIXME works only with absolute paths right now...
        # FIXME are ? or / in filenames problematic?
        if '://' in url:
            scheme, rest = url.split('://', 1)
        else:
            scheme = 'file'
            rest = url
        if scheme == 'db':
            return DBLocator.from_url(url)
        elif scheme == 'file':
            filename = urlparse.urlsplit('http://' + rest)[2]
            if filename.endswith('.vt'):
                return ZIPFileLocator.from_url(url)
            elif filename.endswith('.xml'):
                return XMLFileLocator.from_url(url)
        return None

    @staticmethod
    def parse_args(arg_str):
        args = {}
        parsed_dict = cgi.parse_qs(arg_str)
        if 'type' in parsed_dict:
            args['obj_type'] = parsed_dict['type'][0]
        if 'id' in parsed_dict:
            args['obj_id'] = parsed_dict['id'][0]
        args['version_node'] = None
        args['version_tag'] = None
        if 'workflow' in parsed_dict:
            workflow_arg = parsed_dict['workflow'][0]
            try:
                args['version_node'] = int(workflow_arg)
            except ValueError:
                args['version_tag'] = workflow_arg
        if 'workflow_exec' in parsed_dict:
            args['workflow_exec'] = parsed_dict['workflow_exec'][0]
        return args

    @staticmethod
    def generate_args(args):
        generate_dict = {}
        if 'obj_type' in args and args['obj_type']:
            generate_dict['type'] = args['obj_type']
        if 'obj_id' in args and args['obj_id']:
            generate_dict['id'] = args['obj_id']
        if 'version_node' in args and args['version_node']:
            generate_dict['workflow'] = args['version_node']
        elif 'version_tag' in args and args['version_tag']:
            generate_dict['workflow'] = args['version_tag']
        return urllib.urlencode(generate_dict)


    def _get_name(self):
        return None # Returns a name that will be displayed for the object
    name = property(_get_name)

    def _get_short_name(self):
        return None # Returns a short name that can be used for display
    short_name = property(_get_short_name)

    ###########################################################################
    # Operators

    def __eq__(self, other):
        pass # Implement equality

    def __ne__(self, other):
        pass # Implement nonequality

class XMLFileLocator(BaseLocator):
    def __init__(self, filename, **kwargs):
        self._name = filename
        self._vnode = kwargs.get('version_node', None)
        self._vtag = kwargs.get('version_tag', '')
        self._mshptrail = kwargs.get('mashuptrail', None)
        self._mshpversion = kwargs.get('mashupVersion', None)
        config = core.configuration.get_vistrails_configuration()
        if config:
            self._dot_vistrails = config.dotVistrails
        else:
            self._dot_vistrails = core.system.default_dot_vistrails()
        self.kwargs = kwargs

    def load(self, type):
        fname = self._find_latest_temporary()
        if fname:
            obj = io.open_from_xml(fname, type)
        else:
            obj = io.open_from_xml(self._name, type)
        obj.locator = self
        return obj

    def save(self, obj, do_copy=True, version=None):
        is_bundle = False
        if type(obj) == type(SaveBundle(None)):
            is_bundle = True
            save_bundle = obj
            obj = save_bundle.get_primary_obj()
        obj = io.save_to_xml(obj, self._name, version)
        obj.locator = self
        # Only remove the temporaries if save succeeded!
        self.clean_temporaries()
        if is_bundle:
            return SaveBundle(save_bundle.bundle_type, obj)
        return obj

    def save_temporary(self, obj):
        fname = self._find_latest_temporary()
        new_temp_fname = self._next_temporary(fname)
        io.save_to_xml(obj, new_temp_fname)

    def is_valid(self):
        return os.path.isfile(self._name)

    def _get_name(self):
        return str(self._name)
    name = property(_get_name)

    def _get_short_name(self):
        return os.path.splitext(os.path.basename(self._name))[0]
    short_name = property(_get_short_name)

    @staticmethod
    def from_url(url):
        if '://' in url:
            scheme, rest = url.split('://', 1)
        else:
            scheme = 'file'
            rest = url
        url = 'http://' + rest
        (_, _, path, args_str, _) = urlparse.urlsplit(url)
        # "/c:/path" needs to be "c:/path"
        if systemType in ['Windows', 'Microsoft']:
            path = path[1:]
        kwargs = BaseLocator.parse_args(args_str)
        return XMLFileLocator(path, **kwargs)

    def to_url(self):
        args_str = BaseLocator.generate_args(self.kwargs)
        url_tuple = ('file', '', os.path.abspath(self._name), args_str, '')
        return urlparse.urlunsplit(url_tuple)

    def encode_name(self, filename):
        """encode_name(filename) -> str
        Encodes a file path using urllib.quoteplus

        """
        name = urllib.quote_plus(filename) + '_tmp_'
        return os.path.join(self._dot_vistrails, name)

    def serialize(self, dom, element):
        """serialize(dom, element) -> None
        Convert this object to an XML representation.

        """
        locator = dom.createElement('locator')
        locator.setAttribute('type', 'file')
        node = dom.createElement('name')
        filename = dom.createTextNode(str(self._name))
        node.appendChild(filename)
        locator.appendChild(node)
        element.appendChild(locator)

    @staticmethod
    def parse(element):
        """ parse(element) -> XMLFileLocator or None
        Parse an XML object representing a locator and returns a
        XMLFileLocator object.

        """
        if str(element.getAttribute('type')) == 'file':
            for n in element.childNodes:
                if n.localName == "name":
                    filename = str(n.firstChild.nodeValue).strip(" \n\t")
                    return XMLFileLocator(filename)
            return None
        else:
            return None

    #ElementTree port
    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
        Convert this object to an XML representation.
        """
        if node is None:
            node = ElementTree.Element('locator')

        node.set('type', 'file')
        childnode = ElementTree.SubElement(node,'name')
        childnode.text = str(self._name)
        return node

    @staticmethod
    def from_xml(node):
        """from_xml(node:ElementTree.Element) -> XMLFileLocator or None
        Parse an XML object representing a locator and returns a
        XMLFileLocator object."""
        if node.tag != 'locator':
            return None

        #read attributes
        data = node.get('type', '')
        type = str(data)
        if type == 'file':
            for child in node.getchildren():
                if child.tag == 'name':
                    filename = str(child.text).strip(" \n\t")
                    return XMLFileLocator(filename)
        return None

    def __str__(self):
        return '<%s vistrail_name=" %s/>' % (self.__class__.__name__, self._name)

    ##########################################################################

    def _iter_temporaries(self, f):
        """_iter_temporaries(f): calls f with each temporary file name, in
        sequence.

        """
        latest = None
        current = 0
        while True:
            fname = self.encode_name(self._name) + str(current)
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
            return self.encode_name(self._name) + '0'
        else:
            split = temporary.rfind('_')+1
            base = temporary[:split]
            number = int(temporary[split:])
            return base + str(number+1)

    ###########################################################################
    # Operators

    def __eq__(self, other):
        if type(other) != XMLFileLocator:
            return False
        return self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)

class ZIPFileLocator(XMLFileLocator):
    """Files are compressed in zip format. The temporaries are
    still in xml"""
    def __init__(self, filename, **kwargs):
        XMLFileLocator.__init__(self, filename, **kwargs)
        self.tmp_dir = None

    @staticmethod
    def from_url(url):
        if '://' in url:
            scheme, rest = url.split('://', 1)
        else:
            scheme = 'file'
            rest = url
        url = 'http://' + rest
        (_, _, path, args_str, _) = urlparse.urlsplit(url)
        # "/c:/path" needs to be "c:/path"
        if systemType in ['Windows', 'Microsoft']:
            path = path[1:]
        kwargs = BaseLocator.parse_args(args_str)
        return ZIPFileLocator(path, **kwargs)

    def to_url(self):
        args_str = BaseLocator.generate_args(self.kwargs)
        url_tuple = ('file', '', os.path.abspath(self._name), args_str, '')
        return urlparse.urlunsplit(url_tuple)

    def load(self, type):
        fname = self._find_latest_temporary()
        if fname:
            from db.domain import DBVistrail
            obj = io.open_from_xml(fname, type)
            return SaveBundle(DBVistrail.vtType, obj)
        else:
            (save_bundle, tmp_dir) = io.open_bundle_from_zip_xml(type, self._name)
            self.tmp_dir = tmp_dir
            for obj in save_bundle.get_db_objs():
                obj.locator = self
            return save_bundle

    def save(self, save_bundle, do_copy=True, version=None):
        if do_copy:
            # make sure we create a fresh temporary directory if we're
            # duplicating the vistrail
            tmp_dir = None
        else:
            # otherwise, use the existing temp directory if one is set
            tmp_dir = self.tmp_dir
        (save_bundle, tmp_dir) = io.save_bundle_to_zip_xml(save_bundle, self._name, tmp_dir, version)
        self.tmp_dir = tmp_dir
        for obj in save_bundle.get_db_objs():
            obj.locator = self
        # Only remove the temporaries if save succeeded!
        self.clean_temporaries()
        return save_bundle

    def close(self):
        if self.tmp_dir is not None:
            io.close_zip_xml(self.tmp_dir)
            self.tmp_dir = None

    ###########################################################################
    # Operators

    def __eq__(self, other):
        if type(other) != ZIPFileLocator:
            return False
        return self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def parse(element):
        """ parse(element) -> ZIPFileLocator or None
        Parse an XML object representing a locator and returns a
        ZIPFileLocator object.

        """
        if str(element.getAttribute('type')) == 'file':
            for n in element.childNodes:
                if n.localName == "name":
                    filename = str(n.firstChild.nodeValue).strip(" \n\t")
                    return ZIPFileLocator(filename)
            return None
        else:
            return None
        
    #ElementTree port    
    @staticmethod
    def from_xml(node):
        """from_xml(node:ElementTree.Element) -> ZIPFileLocator or None
        Parse an XML object representing a locator and returns a
        ZIPFileLocator object."""
        if node.tag != 'locator':
            return None

        #read attributes
        data = node.get('type', '')
        type = str(data)
        if type == 'file':
            for child in node.getchildren():
                if child.tag == 'name':
                    filename = str(child.text).strip(" \n\t")
                    return ZIPFileLocator(filename)
            return None
        return None

# class URLLocator(ZIPFileLocator):
#     def load(self, type):
        
class DBLocator(BaseLocator):
    cache = {}
    cache_timestamps = {}
    connections = {}
    cache_connections = {}
        
    def __init__(self, host, port, database, user, passwd, name=None,
                 **kwargs):
        self._host = host
        self._port = int(port)
        self._db = database
        self._user = user
        self._passwd = passwd
        self._name = name
        self._hash = ''
        self.kwargs = kwargs
        self._obj_id = self.kwargs.get('obj_id', None)
        self._obj_type = self.kwargs.get('obj_type', None)
        self._conn_id = self.kwargs.get('connection_id', None)
        self._vnode = self.kwargs.get('version_node', None)
        self._vtag = self.kwargs.get('version_tag', None)
        self._mshptrail = self.kwargs.get('mashuptrail', None)
        self._mshpversion = self.kwargs.get('mashupVersion', None)
        
    def _get_host(self):
        return self._host
    host = property(_get_host)

    def _get_port(self):
        return self._port
    port = property(_get_port)

    def _get_db(self):
        return self._db
    db = property(_get_db)
    
    def _get_obj_id(self):
        return self._obj_id
    obj_id = property(_get_obj_id)

    def _get_obj_type(self):
        return self._obj_type
    obj_type = property(_get_obj_type)

    def _get_connection_id(self):
        return self._conn_id
    connection_id = property(_get_connection_id)
    
    def _get_name(self):
        return self._host + ':' + str(self._port) + ':' + self._db + ':' + \
            str(self._name)
    name = property(_get_name)

    def _get_short_name(self):
        return str(self._name)
    short_name = property(_get_short_name)

    def hash(self):
        node = self.to_xml()
        xml_string = ElementTree.tostring(node)
        #print "hash", xml_string
        return hashlib.sha224(xml_string).hexdigest()
    
    def is_valid(self):
        if self._conn_id is not None \
                and self._conn_id in DBLocator.connections:
            return True
        try:
            self.get_connection()
        except:
            return False
        return True
        
    def get_connection(self):
        if self._conn_id is not None \
                and DBLocator.connections.has_key(self._conn_id):
            connection = DBLocator.connections[self._conn_id]
            if io.ping_db_connection(connection):
                return connection
        else:
            if self._conn_id is None:
                if DBLocator.cache_connections.has_key(self._hash):
                    connection = DBLocator.cache_connections[self._hash]
                    if io.ping_db_connection(connection):
                        debug.log("Reusing cached connection")
                        return connection

                if len(DBLocator.connections.keys()) == 0:
                    self._conn_id = 1
                else:
                    self._conn_id = max(DBLocator.connections.keys()) + 1
        config = {'host': self._host,
                  'port': self._port,
                  'db': self._db,
                  'user': self._user,
                  'passwd': self._passwd}
        #print "config:", config
        connection = io.open_db_connection(config)
            
        DBLocator.connections[self._conn_id] = connection
        DBLocator.cache_connections[self._hash] = connection
        return connection

    def load(self, type, tmp_dir=None):
        self._hash = self.hash()
        #print "LLoad Big|type", type
        if DBLocator.cache.has_key(self._hash):
            save_bundle = DBLocator.cache[self._hash]
            obj = save_bundle.get_primary_obj()

            ts = self.get_db_modification_time(obj.vtType)
            #debug.log("cached time: %s, db time: %s"%(DBLocator.cache_timestamps[self._hash],ts))
            if DBLocator.cache_timestamps[self._hash] == ts:
                #debug.log("using cached vistrail")
                self._name = obj.db_name
                # If thumbnail cache was cleared, get thumbs from db
                if tmp_dir is not None:
                    for absfname in save_bundle.thumbnails:
                        if not os.path.isfile(absfname):
                            save_bundle.thumbnails = io.open_thumbnails_from_db(self.get_connection(), type, self.obj_id, tmp_dir)
                            break
                return save_bundle
        #debug.log("loading vistrail from db")
        connection = self.get_connection()
        save_bundle = io.open_bundle_from_db(type, connection, self.obj_id, tmp_dir)
        primary_obj = save_bundle.get_primary_obj()
        self._name = primary_obj.db_name
        #print "locator db name:", self._name
        for obj in save_bundle.get_db_objs():
            obj.locator = self
        
        _hash = self.hash()
        DBLocator.cache[self._hash] = save_bundle.do_copy()
        DBLocator.cache_timestamps[self._hash] = primary_obj.db_last_modified
        return save_bundle

    def save(self, save_bundle, do_copy=False, version=None):
        connection = self.get_connection()
        for obj in save_bundle.get_db_objs():
            obj.db_name = self._name
        save_bundle = io.save_bundle_to_db(save_bundle, connection, do_copy, version)
        primary_obj = save_bundle.get_primary_obj()
        self._obj_id = primary_obj.db_id
        self._obj_type = primary_obj.vtType
        for obj in save_bundle.get_db_objs():
            obj.locator = self
        #update the cache with a copy of the new bundle
        self._hash = self.hash()
        DBLocator.cache[self._hash] = save_bundle.do_copy()
        DBLocator.cache_timestamps[self._hash] = primary_obj.db_last_modified
        return save_bundle

    def get_db_modification_time(self, obj_type=None):
        if obj_type is None:
            if self.obj_type is None:
                obj_type = DBVistrail.vtType 
            else:
                obj_type = self.obj_type

        ts = io.get_db_object_modification_time(self.get_connection(),
                                                self.obj_id,
                                                obj_type)
        ts = datetime(*strptime(str(ts).strip(), '%Y-%m-%d %H:%M:%S')[0:6])
        return ts
        
    def serialize(self, dom, element):
        """serialize(dom, element) -> None
        Convert this object to an XML representation.

        """
        locator = dom.createElement('locator')
        locator.setAttribute('type', 'db')
        locator.setAttribute('host', str(self._host))
        locator.setAttribute('port', str(self._port))
        locator.setAttribute('db', str(self._db))
        locator.setAttribute('vt_id', str(self._obj_id))
        node = dom.createElement('name')
        filename = dom.createTextNode(str(self._name))
        node.appendChild(filename)
        locator.appendChild(node)
        element.appendChild(locator)

    @staticmethod
    def parse(element):
        """ parse(element) -> DBFileLocator or None
        Parse an XML object representing a locator and returns a
        DBFileLocator object.

        """
        if str(element.getAttribute('type')) == 'db':
            host = str(element.getAttribute('host'))
            port = int(element.getAttribute('port'))
            database = str(element.getAttribute('db'))
            vt_id = str(element.getAttribute('vt_id'))
            user = ""
            passwd = ""
            for n in element.childNodes:
                if n.localName == "name":
                    name = str(n.firstChild.nodeValue).strip(" \n\t")
                    #print host, port, database, name, vt_id
                    return DBLocator(host, port, database,
                                     user, passwd, name, vt_id, None)
            return None
        else:
            return None
    
    @staticmethod
    def from_url(url):
        #FIXME may need some urllib.quote work here
        scheme, rest = url.split('://', 1)
        url = 'http://' + rest
        (_, net_loc, db_name, args_str, _) = urlparse.urlsplit(url)
        db_name = db_name[1:]
        host, port = net_loc.split(':', 1)
#        obj_type, obj_id = args_str.split('=', 1)
        kwargs = BaseLocator.parse_args(args_str)
        return DBLocator(host, port, db_name, None, '', **kwargs)
    
    def to_url(self):
        # FIXME may need some urllib.quote work here 
        # FIXME may also want to allow database type to be encoded in 
        # scheme (ie mysql://host/db, sqlite3://path/to)
        net_loc = '%s:%s' % (self._host, self._port)
        args_str = BaseLocator.generate_args(self.kwargs)
        # query_str = '%s=%s' % (self._obj_type, self._obj_id)
        url_tuple = ('db', net_loc, self._db, args_str, '')
        return urlparse.urlunsplit(url_tuple)

    #ElementTree port
    def to_xml(self, node=None, include_name = False):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
        Convert this object to an XML representation.
        """
        if node is None:
            node = ElementTree.Element('locator')

        node.set('type', 'db')
        node.set('host', str(self._host))
        node.set('port', str(self._port))
        node.set('db', str(self._db))
        node.set('vt_id', str(self._obj_id))
        node.set('user', str(self._user))
        if include_name:
            childnode = ElementTree.SubElement(node,'name')
            childnode.text = str(self._name)
        return node

    @staticmethod
    def from_xml(node, include_name=False):
        """from_xml(node:ElementTree.Element) -> DBLocator or None
        Parse an XML object representing a locator and returns a
        DBLocator object."""
        
        def convert_from_str(value,type):
            def bool_conv(x):
                s = str(x).upper()
                if s == 'TRUE':
                    return True
                if s == 'FALSE':
                    return False

            if value is not None:
                if type == 'str':
                    return str(value)
                elif value.strip() != '':
                    if type == 'long':
                        return long(value)
                    elif type == 'float':
                        return float(value)
                    elif type == 'int':
                        return int(value)
                    elif type == 'bool':
                        return bool_conv(value)
                    elif type == 'date':
                        return date(*strptime(value, '%Y-%m-%d')[0:3])
                    elif type == 'datetime':
                        return datetime(*strptime(value, '%Y-%m-%d %H:%M:%S')[0:6])
            return None
    
        if node.tag != 'locator':
            return None

        #read attributes
        data = node.get('type', '')
        type = convert_from_str(data, 'str')
        
        if type == 'db':
            data = node.get('host', None)
            host = convert_from_str(data, 'str')
            data = node.get('port', None)
            port = convert_from_str(data,'int')
            data = node.get('db', None)
            database = convert_from_str(data,'str')
            data = node.get('vt_id')
            vt_id = convert_from_str(data, 'str')
            data = node.get('user')
            user = convert_from_str(data, 'str')
            passwd = ""
            name = None
            if include_name:
                for child in node.getchildren():
                    if child.tag == 'name':
                        name = str(child.text).strip(" \n\t")
            return DBLocator(host, port, database,
                             user, passwd, name, obj_id=vt_id, obj_type='vistrail')
        else:
            return None

    def __str__(self):
        return '<DBLocator host="%s" port="%s" database="%s" vistrail_id="%s" \
vistrail_name="%s"/>' % ( self._host, self._port, self._db,
                          self._obj_id, self._name)

    ###########################################################################
    # Operators

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._host == other._host and
                self._port == other._port and
                self._db == other._db and
                self._user == other._user and
                #self._name == other._name and
                self._obj_id == other._obj_id and
                self._obj_type == other._obj_type)

    def __ne__(self, other):
        return not self.__eq__(other)
