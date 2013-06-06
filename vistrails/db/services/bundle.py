###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

from vistrails.core import debug
from vistrails.core.external_connection import DBConnection
import vistrails.core.requirements
from vistrails.core.system import execute_cmdline, systemType, \
    get_executable_path
from vistrails.core.utils import Chdir
from vistrails.db import VistrailsDBException
from vistrails.db.services.db import MySQLDBConnection, SQLite3Connection
from vistrails.db.services.io import open_db_connection
from vistrails.db.services.locator import DirectoryLocator, XMLFileLocator, \
    ZIPFileLocator

"""Want {"vistrail": VistrailBundleObj, "log": LogBundleObj}, then serialize using a persistence class."""

class BundleObj(object):
    def __init__(self, obj, obj_type=None, id=None, changed=False):
        self.obj = obj
        if obj_type is None:
            if hasattr(obj, 'vtType'):
                self.obj_type = obj.vtType
            else:
                raise VistrailsDBException("Must have vtType or specify "
                                           "obj_type.")
        else:
            self.obj_type = obj_type
        self.id = id
        self.changed = changed
        
    @staticmethod
    def allows_multiples():
        return True

class BundleObjDictionary(object):
    def __init__(self):
        self._objs = {}

    @staticmethod
    def _translate_args(obj):
        if isinstance(obj, BundleObj):
            obj_type = obj.obj_type
            if obj.allows_multiples():
                obj_id = obj.id
            else:
                obj_id = None
        elif isinstance(obj, tuple):
            (obj_type, obj_id) = obj
        else:
            obj_type = obj
            obj_id = None
        return (obj_type, obj_id)

    def has_entry(self, obj_type, obj_id):
        if obj_type in self._objs:
            return obj_id in self._objs[obj_type]
        return False

    def add_entry(self, obj, value):
        obj_type, obj_id = self._translate_args(obj)
        if self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Use change_entry to overwrite.')
        
        if obj_type not in self._objs:
            self._objs[obj_type] = {}
        self._objs[obj_type][obj_id] = value
        
    def remove_entry(self, obj):
        obj_type, obj_id = self._translate_args(obj)
        if not self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Entry does not exist.')
        del self._objs[obj_type][obj_id]

    def change_entry(self, obj, value):
        # not the most efficient, but that's ok
        BundleObjDictionary.remove_entry(self, obj)
        BundleObjDictionary.add_entry(self, obj, value)
        
    def get_value(self, obj):
        obj_type, obj_id = self._translate_args(obj)
        if not self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Entry does not exist.')
        return self._objs[obj_type][obj_id]

    def get_items(self):
        return [(k1, k2, v) for k1, k2_dict in self._objs.iteritems() 
                for k2, v in k2_dict.iteritems()]

class Bundle(object):
    """Assume a bundle contains a set of objects.  If an object is a list
    or dictionary, we serialize these to a directory."""

    def __init__(self, *args, **kwargs):
        self._objs = BundleObjDictionary()
        self.serializers = {}

        # Make all args into attrs using vtType as attr name
        # This requires that attr names in this class match the vtTypes
        # i.e. if arg's vtType is 'vistrail', self.vistrail = arg, etc...
        for arg in args:
            if hasattr(arg, 'vtType'):
                self.add_object(arg.vtType, arg)
        # Make all keyword args directly into attrs
        for (k,v) in kwargs.iteritems():
            self.add_object(k, v)
       
    def cleanup(self):
        pass
 
    def add_object(self, obj):
        if not isinstance(obj, BundleObj):
            raise VistrailsDBException('Can only add BundleObj objects.')
        self._objs.add_entry(obj, obj)

    def remove_object(self, obj):
        self._objs.remove_entry(obj)

    def change_object(self, obj):
        if isinstance(obj, BundleObj):
            raise VistrailsDBException('Can only change BundleObj objects.')
        self._objs.change_entry(obj)

    def get_object(self, obj_type, obj_id=None):
        return self._objs.get_value((obj_type, obj_id))

    def get_items(self):
        return self._objs.get_items()

    def get_primary_obj(self):
        raise NotImplementedError("Subclass must implement get_primary_obj")

    def add_serializer(self, obj_key, cls):
        serializer_type = cls.get_serializer_type()
        if obj_key not in self.serializers:
            self.serializers[obj_key] = {}
        elif serializer_type in self.serializers[obj_key]:
            raise VistrailsDBException('Bundle already has serializer "%s" '
                                       'for "%s" registered.' %
                                       (serializer_type, obj_key))
            
        self.serializers[obj_key][serializer_type] = cls

    def remove_serializer(self, obj_key, serializer_type):
        if obj_key not in self.serializers or \
           serializer_type not in self.serializers[obj_key]:
            raise VistrailsDBException('Bundle does not have serializer "%s" '
                                       'for "%s" registered.' % 
                                       (serializer_type, obj_key))
        del self.serializers[obj_key][serializer_type]
        
    def get_serializer(self, obj_key, serializer_type):
        if obj_key not in self.serializers or \
           serializer_type not in self.serializers[obj_key]:
            raise VistrailsDBException('Bundle does not have serializer "%s" '
                                       'for "%s" registered.' % 
                                       (serializer_type, obj_key))
        return self.serializers[obj_key][serializer_type]

class Serializer(object):
    def load(self):
        raise NotImplementedError("Subclass must implement load.")

    def save(self):
        raise NotImplementedError("Subclass must implement save.")

class FileSerializer(Serializer):
    @staticmethod
    def get_serializer_type():
        return 'file'

    @staticmethod
    def load(filename):
        if not os.path.exists(filename):
            raise VistrailsDBException('Cannot open file "%s".' % filename)
        with open(filename, 'rb') as f:
            data = f.read()
            obj = BundleObj(data, 'data', os.path.basename(filename))
            return obj
    
    @staticmethod
    def save(obj, rootdir):
        fname = os.path.join(rootdir, obj.id)
        with open(fname, 'wb') as f:
            f.write(obj.obj)
        return fname

class DBSerializer(Serializer):
    SCHEMA = """
    CREATE TABLE blobdata(
        id integer not null primary key auto_increment,
        data mediumblob
    );

    """

    DROP_SCHEMA = """DROP TABLE IF EXISTS blobdata;"""
    
    STMTS = {"load": "SELECT data FROM blobdata WHERE id=%s;",
             "delete": "DELETE FROM blobdata WHERE id=%s;",
             "insert": "INSERT INTO blobdata (data) VALUES (%s);",
             "update": "UPDATE blobdata SET data=%s WHERE id=%s;"}

    @staticmethod
    def get_serializer_type():
        return 'db'

    @staticmethod
    def load(db_id, connection_obj):
        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(DBSerializer.STMTS["load"]), 
                  (db_id,))
        rows = c.fetchall()
        data = rows[0][0]
        obj = BundleObj(data, 'data', db_id)
        return obj

    @staticmethod
    def save(obj, connection_obj):
        import sqlite3
        c = connection_obj.get_connection().cursor()

        c.execute(connection_obj.format_stmt(DBSerializer.STMTS["insert"]), 
                  (sqlite3.Binary(obj.obj),))
        db_id = c.lastrowid
        connection_obj.get_connection().commit()
        return db_id

class ThumbnailFileSerializer(Serializer):
    def load(self, filename):
        pass

    def save(self, obj, filename):
        pass

class AbstractionFileSerializer(Serializer):
    def load(self, filename):
        pass

    def save(self, obj, filename):
        pass
    

class XMLFileSerializer(Serializer):
    def load(self, filename, obj_type, translator_f, update_id_scope_f):
        tree = ElementTree.parse(filename)
        version = get_version_for_xml(tree.getroot())
        daoList = getVersionDAO(version)
        obj = daoList.open_from_xml(filename, obj_type, tree)
        obj = translate_object(obj, translator_f, version)
        update_id_scope_f(obj)
        return obj

    def save(self, obj, filename, version, schema, translator_f):
        tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xsi:schemaLocation': schema}
        if version is None:
            version = currentVersion
        if not obj.db_version:
            obj.db_version = currentVersion
        obj = translate_object(obj, translator_f, obj.db_version, version)

        daoList = getVersionDAO(version)
        daoList.save_to_xml(obj, filename, tags, version)
        obj = translate_object(obj, translator_f, version)
        return obj

class RegistryXMLSerializer(XMLFileSerializer):
    def load(self, filename):
        XMLFileSerializer.load(self, filename, DBRegistry.vtType, 
                               "translateRegistry", 
                               vistrails.db.services.regsitry.update_id_scope)

    def save(self, obj, filename, version):
        XMLFileSerializer.save(self, obj, filename, version,
                               "http://www.vistrails.org/registry.xsd",
                               "translateRegistry")

class LogXMLSerializer(XMLFileSerializer):
    def load(self, filename):
        XMLFileSerializer.load(self, filename, DBLog.vtType,
                               "translateLog",
                               vistrails.db.services.log.update_id_scope)

    def save(self, obj, filename, version):
        XMLFileSerializer.save(self, obj, filename, version,
                               "http://www.vistrails.org/log.xsd",
                               "translateLog")

class Manifest(BundleObjDictionary):
    def load(self):
        raise NotImplementedError("Subclass must define load.")
    
    def save(self):
        raise NotImplementedError("Subclass must define save.")

    def add_entry(self, obj_type, obj_id, value):
        if not obj_id:
            obj_id = None
        BundleObjDictionary.add_entry(self, (obj_type, obj_id), value)

    def remove_entry(self, obj_type, obj_id=None):
        BundleObjDictionary.remove_entry(self, (obj_type, obj_id))

    def change_entry(self, obj_type, obj_id, value):
        BundleObjDictionary.change_entry(self, (obj_type, obj_id), value)

    def get_value(self, obj_type, obj_id=None):
        return BundleObjDictionary.get_value(self, (obj_type, obj_id))

    def get_items(self):
        return [(i1, i2 if i2 else "", i3) 
                for (i1, i2, i3) in BundleObjDictionary.get_items(self)]

class FileManifest(Manifest):
    def __init__(self, fname=None):
        Manifest.__init__(self)
        self._fname = fname

    def load(self):
        with open(self._fname, 'rU') as f:
            for line in f:
                args = line.strip().split('\t')
                self.add_entry(*args)
    
    def save(self):
        with open(self._fname, 'w') as f:
            for obj_type, obj_id, fname in sorted(self.get_items()):
                print >>f, obj_type + "\t" + obj_id + "\t" + fname

class DirectoryBundle(Bundle):
    def __init__(self, dir_path, overwrite=False, *args, **kwargs):
        Bundle.__init__(self, *args, **kwargs)
        self._dir_path = dir_path
        self._manifest = None
        self._overwrite = overwrite
        
    def create_manifest(self, dir_path=None, fname=None):
        if dir_path is None:
            dir_path = self._dir_path
        if fname is None:
            fname = os.path.join(dir_path, "MANIFEST")
        self._manifest = FileManifest(fname)

    def load_manifest(self, dir_path=None, fname=None):
        self.create_manifest(dir_path, fname)
        self._manifest.load()        

    def load(self, dir_path=None):
        if dir_path is None:
            dir_path = self._dir_path
        self.load_manifest(dir_path)
        for obj_type, obj_id, fname in self._manifest.get_items():
            serializer = self.get_serializer(obj_type, 
                                        FileSerializer.get_serializer_type())
            path = os.path.join(dir_path, fname)
            obj = serializer.load(path)
            if obj is not None:
                self.add_object(obj)

    def save(self, dir_path=None, overwrite=None):
        if dir_path is None:
            dir_path = self._dir_path
        if overwrite is None:
            overwrite = self._overwrite
        if self._manifest is None:
            self.create_manifest(dir_path)
        all_files = []
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                if not overwrite:
                    raise VistrailsDBException('Directory "%s" already '
                                               'exists and overwrite is '
                                               'off.' % dir_path)
                for path, subdirs, fnames in os.walk(dir_path):
                    all_files.extend(os.path.join(path, fname) for fname in fnames)
            elif not overwrite:
                raise VistrailsDBException('Directory "%s" already '
                                           'exists and overwrite is '
                                           'off.' % dir_path)
            else:
                os.unlink(dir_path)
        else:
            parent_dir = os.path.dirname(dir_path)
            if not os.path.exists(parent_dir) or not os.path.isdir(parent_dir):
                raise VistrailsDBException('Parent directory "%s" does not '
                                           'exist.' % parent_dir)
            os.mkdir(dir_path)

        for obj_type, obj_id, obj in self._objs.get_items():
            try:
                serializer = self.get_serializer(obj_type, 
                                        FileSerializer.get_serializer_type())
                if not dir_path.endswith(os.sep):
                    dir_path = dir_path + os.sep
                else:
                    dir_path = dir_path
                path = serializer.save(obj, dir_path)
                fname = path[len(dir_path):]
                self._manifest.add_entry(obj_type, obj_id, fname)
            except VistrailsDBException:
                # cannot serialize object
                print 'cannot serialize obj', obj_type
                debug.warning('Cannot serialize object(s) of type "%s"' % \
                              obj_type)
        self._manifest.save()

    def cleanup(self):
        pass

class ZIPBundle(Bundle):
    # a zipped version of a directory bundle
    def __init__(self, file_path, overwrite=False, *args, **kwargs):
        Bundle.__init__(self, *args, **kwargs)
        self._file_path = file_path
        self._dir_bundle = None

    def load(self, file_path=None):
        # have path and temp dir 
        #
        # first unzip it to a temporary directory and then
        # treat it like a directory bundle
        if file_path is None:
            file_path = self._file_path

        vistrails.core.requirements.require_executable('unzip')

        if self._dir_bundle is None:
            save_dir = tempfile.mkdtemp(prefix='vt_save')
            self._dir_bundle = DirectoryBundle(save_dir)
            # need to link objs from dir bundle to this bundle
            self._dir_bundle._objs = self._objs
            self._dir_bundle.serializers = self.serializers
        else:
            save_dir = self._dir_bundle._dir_path

        output = []
        cmdline = ['unzip', '-q','-o','-d', save_dir, file_path]
        result = execute_cmdline(cmdline, output)

        if result != 0 and len(output) != 0:
            raise VistrailsDBException("Unzip of '%s' failed" % file_path)

        self._dir_bundle.load()

    def save(self, file_path=None):
        # first save everything to a temporary directory as a
        # directory bundle and then zip it
        if file_path is None:
            file_path = self._file_path
        if self._dir_bundle is None:
            save_dir = tempfile.mkdtemp(prefix='vt_save')
            self._dir_bundle = DirectoryBundle(save_dir)
            # need to link objs from dir bundle to this bundle
            self._dir_bundle._objs = self._objs
            self._dir_bundle.serializers = self.serializers
        self._dir_bundle.save(overwrite=True)

        tmp_zip_dir = tempfile.mkdtemp(prefix='vt_zip')
        tmp_zip_file = os.path.join(tmp_zip_dir, "vt.zip")
        output = []
        rel_vt_save_dir = os.path.split(save_dir)[1]

        # on windows, we assume zip.exe is in the current directory when
        # running from the binary install
        zipcmd = 'zip'
        if systemType in ['Windows', 'Microsoft']:
            zipcmd = get_executable_path('zip.exe')
            if not zipcmd or not os.path.exists(zipcmd):
                zipcmd = 'zip.exe' #assume zip is in path
        cmdline = [zipcmd, '-r', '-q', tmp_zip_file, '.']
        try:
            #if we want that directories are also stored in the zip file
            # we need to run from the vt directory
            with Chdir(save_dir):
                result = execute_cmdline(cmdline,output)
            if result != 0 or len(output) != 0:
                for line in output:
                    if line.find('deflated') == -1:
                        raise VistrailsDBException(" ".join(output))
            shutil.copyfile(tmp_zip_file, file_path)
        finally:
            os.unlink(tmp_zip_file)
            os.rmdir(tmp_zip_dir)

    def cleanup(self):
        if (self._dir_bundle is not None and
            self._dir_bundle._dir_path is not None):
            shutil.rmtree(self._dir_bundle._dir_path)

class DBManifest(Manifest):
    SCHEMA = """
    CREATE TABLE manifest(
        bundle_id int not null,
        obj_type varchar(255),
        obj_id varchar(255),
        db_id int not null,
        PRIMARY KEY (bundle_id, obj_type, obj_id)
    );

    """
    #  engine=InnoDB;
    DROP_SCHEMA = """DROP TABLE IF EXISTS manifest;"""

    STMTS = {"load": ("SELECT obj_type, obj_id, db_id FROM manifest "
                      "WHERE bundle_id=%s;"),
             "delete": "DELETE FROM manifest WHERE bundle_id=%s;",
             "insert": ("INSERT INTO manifest (bundle_id, obj_type, "
                        "obj_id, db_id) VALUES (%s, %s, %s, %s);")}

    def __init__(self, connection_obj, bundle_id=None):
        Manifest.__init__(self)
        self._connection_obj = connection_obj
        self._bundle_id = bundle_id
        self._obj_db_ids = BundleObjDictionary()

    def set_bundle_id(self, bundle_id):
        self._bundle_id = bundle_id

    def load(self):
        c = self._connection_obj.get_connection().cursor()
        c.execute(self._connection_obj.format_stmt(self.STMTS["load"]), 
                  (self._bundle_id,))
        rows = c.fetchall()
        for row in rows:
            self.add_entry(*row)

    def save(self):
        c = self._connection_obj.get_connection().cursor()
        c.execute(self._connection_obj.format_stmt(self.STMTS["delete"]), 
                  (self._bundle_id,))
        c.executemany(self._connection_obj.format_stmt(self.STMTS["insert"]),
                      [(self._bundle_id,) + item 
                       for item in sorted(self.get_items())])

class DBBundle(Bundle):
    SCHEMA = """
    CREATE TABLE bundle(
        id integer not null primary key auto_increment,
        name varchar(1023)
    );

    """

    DROP_SCHEMA = """DROP TABLE IF EXISTS bundle;"""
    
    STMTS = {"load": "SELECT name FROM bundle WHERE id=%s;",
             "delete": "DELETE FROM bundle WHERE id=%s;",
             "insert": "INSERT INTO bundle (name) VALUES (%s);",
             "update": "UPDATE bundle SET name=%s WHERE id=%s;"}

    def __init__(self, connection_obj, bundle_id=None, name="",
                 overwrite=False, *args, **kwargs):
        Bundle.__init__(self, *args, **kwargs)
        self._connection_obj = connection_obj
        self._name = name
        self._bundle_id = bundle_id
        self._manifest = None
        self._overwrite = overwrite

    def create_manifest(self, connection_obj=None, bundle_id=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        self._manifest = DBManifest(connection_obj, bundle_id)

    def load_manifest(self, connection_obj=None, bundle_id=None):
        self.create_manifest(connection_obj, bundle_id)
        self._manifest.load()

    def load(self, connection_obj=None, bundle_id=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        if bundle_id is None:
            bundle_id = self._bundle_id
        self.load_manifest(connection_obj, bundle_id)

        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(self.STMTS["load"]), (bundle_id,))
        rows = c.fetchall()
        self._name = rows[0][0]

        for obj_type, obj_id, db_id in self._manifest.get_items():
            serializer = self.get_serializer(obj_type, 
                                        DBSerializer.get_serializer_type())
            obj = serializer.load(db_id, connection_obj)
            if obj is not None:
                self.add_object(obj)

    def save(self, connection_obj=None, bundle_id=None, name=None,
             overwrite=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        if bundle_id is None:
            bundle_id = self._bundle_id
        if name is None:
            name = self._name
        if overwrite is None:
            overwrite = self._overwrite
        
        if self._manifest is None:
            self.create_manifest(connection_obj, bundle_id)
        all_objs = []
        for obj_type, obj_id, obj in self._objs.get_items():
            try:
                serializer = self.get_serializer(obj_type, 
                                        DBSerializer.get_serializer_type())
                db_id = serializer.save(obj, connection_obj)
                self._manifest.add_entry(obj_type, obj_id, db_id)
            except VistrailsDBException:
                # cannot serialize object
                print 'cannot serialize obj', obj_type
                debug.warning('Cannot serialize object(s) of type "%s"' % \
                              obj_type)
        if self._bundle_id is None:
            c = connection_obj.get_connection().cursor()
            c.execute(connection_obj.format_stmt(self.STMTS['insert']), 
                      (self._name,))
            self._bundle_id = c.lastrowid
            self._manifest.set_bundle_id(self._bundle_id)
        else:
            c.execute(connection_obj.format_stmt(self.STMTS['update']), 
                      (self._name,))
        self._manifest.save()

class VistrailBundle(Bundle):
    def get_primary_obj(self):
        return self.get_object(DBVistrail.vtType)

class WorkflowBundle(Bundle):
    def get_primary_obj(self):
        return self.get_object(DBWorkflow.vtType)

class LogBundle(Bundle):
    def get_primary_obj(self):
        return self.get_object(DBLog.vtType)
        
class RegistryBundle(Bundle):
    def get_primary_obj(self):
        return self.get_object(DBRegistry.vtType)
        

    def __init__(self, bundle_type, *args, **kwargs):
        self.bundle_type = bundle_type
        self.vistrail = None
        self.workflow = None
        self.log = None
        self.registry = None
        self.opm_graph = None
        self.abstractions = []
        self.thumbnails = []
        self.mashups = []
        # Make all args into attrs using vtType as attr name
        # This requires that attr names in this class match the vtTypes
        # i.e. if arg's vtType is 'vistrail', self.vistrail = arg, etc...
        for arg in args:
            if hasattr(arg, 'vtType'):
                setattr(self, arg.vtType, arg)
        # Make all keyword args directly into attrs
        for (k,v) in kwargs.iteritems():
            setattr(self, k, v)

    def get_db_objs(self):
        """Gets a list containing only the DB* objects in the bundle"""
        return [obj for obj in self.__dict__.itervalues() if obj is not None and type(obj) not in [type([]), type('')]]

    def get_primary_obj(self):
        """get_primary_obj() -> DB*
           Gets the bundle's primary DB* object based on the bundle type.
        """
        return getattr(self, self.bundle_type)

    def __copy__(self):
        return SaveBundle.do_copy(self)
    
    def do_copy(self):
        cp = SaveBundle(self.bundle_type)
        cp.vistrail = copy.copy(self.vistrail)
        cp.workflow = copy.copy(self.workflow)
        cp.log = copy.copy(self.log)
        cp.registry = copy.copy(self.registry)
        cp.opm_graph = copy.copy(self.opm_graph)
        for a in self.abstractions:
            cp.abstractions.append(a)
        
        for t in self.thumbnails:
            cp.thumbnails.append(t)
        
        return cp

import unittest
import os
import shutil
import tempfile

class DatabaseTest(object):
    def __init__(self):
        self.connection_obj = None

    def setup(self):
        pass

    def cleanup(self):
        pass

class MySQLDatabaseTest(DatabaseTest):
    def setup(self):
        create_cmd = "CREATE DATABASE `vt_test`;"
        use_cmd = "USE `vt_test`;"

        db_config = {'host': 'localhost',
                     'port': 3306,
                     'user': 'vt_test',
                     }

        self.connection_obj = MySQLDBConnection(**db_config)
        c = self.connection_obj.get_connection().cursor()
        c.execute(create_cmd)
        c.execute(use_cmd)
        return self.connection_obj

    def cleanup(self):
        drop_cmd = "DROP DATABASE IF EXISTS `vt_test`;"

        c = self.connection_obj.get_connection().cursor()            
        c.execute(drop_cmd);
        self.connection_obj.close()

class SQLite3DatabaseTest(DatabaseTest):
    def setup(self):
        (h, self.fname) = \
                    tempfile.mkstemp(prefix='vt_test_db', suffix='.db')
        os.close(h)
        self.connection_obj = SQLite3Connection(self.fname)
        return self.connection_obj

    def cleanup(self):
        self.connection_obj.close()
        os.unlink(self.fname)

class TestBundles(unittest.TestCase):
    def test_manifest(self):
        manifest = Manifest()
        paths = [('vistrail', None, 'vistrail.xml'),
                 ('thumbnail', 'abc', 'thumbs/abc.png'),
                 ('thumbnail', 'def', 'thumbs/def.png')]
        for p in paths:
            manifest.add_entry(*p)
        manifest.remove_entry(paths[1][0], paths[1][1])
        self.assertEqual(len(manifest.get_items()), len(paths)-1)
        manifest.change_entry(paths[2][0], paths[2][1], 'thumbs/thumb-def.png')
        self.assertEqual(manifest.get_value(paths[2][0], paths[2][1]),
                         'thumbs/thumb-def.png')

    def test_manifest_file(self):
        d = tempfile.mkdtemp(prefix='vt_bundle_test')
        try:
            manifest = FileManifest(os.path.join(d, 'MANIFEST'))
            paths = [('vistrail', None, 'vistrail.xml'),
                     ('thumbnail', 'abc', 'thumbs/abc.png'),
                     ('thumbnail', 'def', 'thumbs/def.png')]
            for p in paths:
                manifest.add_entry(*p)
            manifest.save()
            self.assertTrue(os.path.exists(os.path.join(d, "MANIFEST")))

            manifest2 = FileManifest(os.path.join(d, 'MANIFEST'))
            manifest2.load()
            for p in paths:
                self.assertTrue(manifest2.has_entry(p[0], p[1]))
                self.assertEqual(manifest.get_value(p[0], p[1]),
                                 manifest2.get_value(p[0], p[1]))
        finally:
            shutil.rmtree(d)

    def create_bundle(self, b, ids, is_file=True):
        if is_file:
            b.add_serializer('data', FileSerializer)
        else:
            b.add_serializer('data', DBSerializer)
        o1 = FileSerializer.load('/Users/dakoop/Pictures/DSCF0723_OUT.JPG')
        o1.id = ids[0]
        b.add_object(o1)
        o2 = FileSerializer.load('/Users/dakoop/Pictures/DSCF0723_OUT2.JPG')
        o2.id = ids[1]
        b.add_object(o2)
        b.save()

    def load_bundle(self, b, is_file=True):
        if is_file:
            b.add_serializer('data', FileSerializer)
        else:
            b.add_serializer('data', DBSerializer)
        b.load()

    def compare_bundles(self, b1, b2):
        self.assertEqual(len(b1.get_items()), len(b2.get_items()))
        for obj_type, obj_id, obj in b1.get_items():
            obj2 = b2.get_object(obj_type, obj_id)
            # not ideal, but fails when trying to compare buffer obj with str
            # on db stuff without conversion
            self.assertEqual(str(obj.obj), str(obj2.obj))

    def test_dir_bundle(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')
        b1 = DirectoryBundle(inner_d)
        b2 = DirectoryBundle(inner_d)
        try:
            self.create_bundle(b1, ['abc', 'def'])
            self.load_bundle(b2)

            self.compare_bundles(b1, b2)
        finally:
            shutil.rmtree(d)
            # pass
        
    def test_zip_bundle(self):
        (h, fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)
        b1 = ZIPBundle(fname)
        b2 = ZIPBundle(fname)
        try:
            self.create_bundle(b1, ['abc', 'def'])
            self.load_bundle(b2)
            
            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            os.unlink(fname)

    def run_manifest_db(self, db_klass):
        """To run this, you need to create a user named "vt_test" on
        localhost:3306.  You also need to grant "vt_test" create table
        priviledges.

        > CREATE USER 'vt_test'@'localhost';
        > GRANT ALL PRIVILEGES ON `vt_test`.* TO 'vt_test'@'localhost';

        Note that autocommit mode is off (PEP 249).

        """

        try:
            db = db_klass()
        except ImportError:
            self.skipTest("Cannot import dependencies for %s." % \
                          db_klass.__name__)
            
        connection_obj = db.setup()
        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
        
        try:
            manifest = DBManifest(connection_obj, 0)

            entries = [('vistrail', None, 0),
                       ('thumbnail', 'abc', 23),
                       ('thumbnail', 'def', 34)]
            for e in entries:
                manifest.add_entry(*e)
            manifest.save()

            manifest2 = DBManifest(connection_obj, 0)
            manifest2.load()
            for e in entries:
                self.assertTrue(manifest2.has_entry(e[0], e[1]))
                self.assertEqual(manifest.get_value(e[0], e[1]),
                                 manifest2.get_value(e[0], e[1]))
            connection_obj.get_connection().commit()
        finally:
            c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
            db.cleanup()

    def run_bundle_db(self, db_klass):
        try:
            db = db_klass()
        except ImportError:
            self.skipTest("Cannot import dependencies for %s." % \
                          db_klass.__name__)
        connection_obj = db.setup()
        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
        c.execute(connection_obj.format_stmt(DBBundle.SCHEMA))
        c.execute(connection_obj.format_stmt(DBSerializer.SCHEMA))

        try:
            b1 = DBBundle(connection_obj, name="test")
            b2 = DBBundle(connection_obj, bundle_id=1)

            self.create_bundle(b1, [1,2], False)
            self.load_bundle(b2, False)
            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
            c.execute(connection_obj.format_stmt(DBBundle.DROP_SCHEMA));
            c.execute(connection_obj.format_stmt(DBSerializer.DROP_SCHEMA));
            db.cleanup()

    def test_manifest_mysql(self):
        self.run_manifest_db(MySQLDatabaseTest)

    def test_manifest_sqlite3(self):
        self.run_manifest_db(SQLite3DatabaseTest)

    def test_bundle_mysql(self):
        self.run_bundle_db(MySQLDatabaseTest)

    def test_bundle_sqlite3(self):
        self.run_bundle_db(SQLite3DatabaseTest)

if __name__ == '__main__':
    unittest.main()
                  
