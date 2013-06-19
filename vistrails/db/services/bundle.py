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

import copy

from vistrails.core import debug
from vistrails.core.external_connection import DBConnection
import vistrails.core.requirements
from vistrails.core.system import execute_cmdline, systemType, \
    get_executable_path, get_elementtree_library
from vistrails.core.utils import Chdir
from vistrails.db import VistrailsDBException
from vistrails.db.domain import DBLog, DBVistrail, DBWorkflowExec
import vistrails.db.versions
from vistrails.db.services.db_utils import MySQLDBConnection, SQLite3Connection
from vistrails.db.services.io import open_db_connection
from vistrails.db.services.locator import DirectoryLocator, XMLFileLocator, \
    ZIPFileLocator

ElementTree = get_elementtree_library()

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

class Bundle(BundleObjDictionary):
    """Assume a bundle contains a set of objects.  If an object is a list
    or dictionary, we serialize these to a directory."""

    # def __init__(self, *args, **kwargs):
    #     # Make all args into attrs using vtType as attr name
    #     # This requires that attr names in this class match the vtTypes
    #     # i.e. if arg's vtType is 'vistrail', self.vistrail = arg, etc...
    #     for arg in args:
    #         if hasattr(arg, 'vtType'):
    #             self.add_object(arg.vtType, arg)
    #     # Make all keyword args directly into attrs
    #     for (k,v) in kwargs.iteritems():
    #         self.add_object(k, v)
       
    def add_object(self, obj):
        if not isinstance(obj, BundleObj):
            raise VistrailsDBException('Can only add BundleObj objects.')
        self.add_entry(obj, obj)

    def remove_object(self, obj):
        self.remove_entry(obj)

    def change_object(self, obj):
        if isinstance(obj, BundleObj):
            raise VistrailsDBException('Can only change BundleObj objects.')
        self.change_entry(obj)

    def get_object(self, obj_type, obj_id=None):
        return self.get_value((obj_type, obj_id))

    def get_primary_obj(self):
        raise NotImplementedError("Subclass must implement get_primary_obj")

class BundleSerializer(object):
    def __init__(self, bundle=None):
        self._bundle = bundle
        self._serializers = {}

    def load(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement load.")

    def save(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement save.")

    def cleanup(self):
        pass
 
    def add_serializer(self, obj_key, cls):
        serializer_type = cls.get_serializer_type()
        if obj_key not in self._serializers:
            self._serializers[obj_key] = {}
        elif serializer_type in self._serializers[obj_key]:
            raise VistrailsDBException('Bundle already has serializer "%s" '
                                       'for "%s" registered.' %
                                       (serializer_type, obj_key))
            
        self._serializers[obj_key][serializer_type] = cls

    def remove_serializer(self, obj_key, serializer_type):
        if obj_key not in self._serializers or \
           serializer_type not in self._serializers[obj_key]:
            raise VistrailsDBException('Bundle does not have serializer "%s" '
                                       'for "%s" registered.' % 
                                       (serializer_type, obj_key))
        del self._serializers[obj_key][serializer_type]
        
    def get_serializer(self, obj_key, serializer_type):
        if obj_key not in self._serializers or \
           serializer_type not in self._serializers[obj_key]:
            raise VistrailsDBException('Bundle does not have serializer "%s" '
                                       'for "%s" registered.' % 
                                       (serializer_type, obj_key))
        return self._serializers[obj_key][serializer_type]

class Serializer(object):
    @classmethod
    def load(cls, *args, **kwargs):
        raise NotImplementedError("Subclass must implement load.")

    @classmethod
    def save(cls, *args, **kwargs):
        raise NotImplementedError("Subclass must implement save.")

class FileSerializer(Serializer):
    @classmethod
    def get_serializer_type(cls):
        return 'file'

    @classmethod
    def load(cls, filename):
        if not os.path.exists(filename):
            raise VistrailsDBException('Cannot open file "%s".' % filename)
        with open(filename, 'rb') as f:
            data = f.read()
            obj = BundleObj(data, 'data')
            return obj
    
    @classmethod
    def save(cls, obj, rootdir):
        fname = os.path.join(rootdir, obj.id)
        with open(fname, 'wb') as f:
            f.write(obj.obj)
        return fname

class FileRefSerializer(FileSerializer):
    @classmethod
    def load(cls, filename, obj_type, inner_dir_name=None):
        if inner_dir_name:
            full_dir = os.path.dirname(filename)
            if not full_dir.endswith(inner_dir_name):
                raise VistrailsDBException('Expected "%s" to end with "%s".' % \
                                           (filename, inner_dir_name))
        obj_id = os.path.basename(filename)
        obj = BundleObj(filename, obj_type, obj_id)
        return obj

    @classmethod
    def save(cls, obj, rootdir, inner_dir_name=None):
        if inner_dir_name:
            inner_dir = os.path.join(rootdir, inner_dir_name)
            if os.path.exists(inner_dir):
                if not os.path.isdir(inner_dir):
                    raise VistrailsDBException("%s exists and is not a "
                                               "directory" % inner_dir_name)
            else:
                os.mkdir(inner_dir)
            rootdir = inner_dir
        fname = os.path.join(rootdir, obj.id)
        shutil.copyfile(obj.obj, fname)
        return fname

class ThumbnailFileSerializer(FileRefSerializer):
    @classmethod
    def load(cls, filename):
        return super(ThumbnailFileSerializer, cls).load(filename, 'thumbnail', 
                                                        'thumbs')

    @classmethod
    def save(cls, obj, rootdir):
        return super(ThumbnailFileSerializer, cls).save(obj, rootdir, 'thumbs')

class AbstractionFileSerializer(FileRefSerializer):
    @classmethod
    def load(self, filename):
        return super(AbstractionFileSerializer, cls).load(cls, filename, 
                                                          'abstraction', 
                                                          'abstractions')

    @classmethod
    def save(cls, obj, rootdir):
        return super(AbstractionFileSerializer, cls).save(cls, obj, rootdir, 
                                                          'abstractions')

class XMLFileSerializer(FileSerializer):
    @classmethod
    def load(cls, filename, obj_type, translator_f, inner_dir_name=None):
        if inner_dir_name:
            full_dir = os.path.dirname(filename)
            if not full_dir.endswith(inner_dir_name):
                raise VistrailsDBException('Expected "%s" to end with "%s".' % \
                                           (filename, inner_dir_name))
        tree = ElementTree.parse(filename)
        version = cls.get_version_for_xml(tree.getroot())
        daoList = vistrails.db.versions.getVersionDAO(version)
        vt_obj = daoList.open_from_xml(filename, obj_type, tree)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                        version)
        obj_id = cls.get_obj_id(vt_obj)
        obj = BundleObj(vt_obj, obj_type, obj_id)
        return obj

    @classmethod
    def save(cls, obj, rootdir, version, schema, translator_f, 
             inner_dir_name=None):
        if inner_dir_name:
            inner_dir = os.path.join(rootdir, inner_dir_name)
            if os.path.exists(inner_dir):
                if not os.path.isdir(inner_dir):
                    raise VistrailsDBException("%s exists and is not a "
                                               "directory" % inner_dir_name)
            else:
                os.mkdir(inner_dir)
            rootdir = inner_dir
        vt_obj = obj.obj
        obj_path = cls.get_obj_path(vt_obj)
        filename = os.path.join(rootdir, obj_path)
        obj = cls.save_file(obj, filename, version, schema, translator_f)
        return filename

    @classmethod
    def save_file(cls, obj, file_obj, version, schema, translator_f, 
                  inner_dir_name=None):
        vt_obj = obj.obj
        tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xsi:schemaLocation': schema}
        if version is None:
            version = vistrails.db.versions.currentVersion
        if not hasattr(vt_obj, 'db_version') or not vt_obj.db_version:
            vt_obj.db_version = vistrails.db.versions.currentVersion
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                        vt_obj.db_version, 
                                                        version)

        daoList = vistrails.db.versions.getVersionDAO(version)
        daoList.save_to_xml(vt_obj, file_obj, tags, version)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                        version)
        obj.obj = vt_obj
        cls.finish_save(vt_obj)
        return obj

    @classmethod
    def get_version_for_xml(cls, root):
        version = root.get('version', None)
        if version is not None:
            return version
        msg = "Cannot find version information"
        raise VistrailsDBException(msg)
        
    @classmethod
    def get_obj_path(cls, vt_obj):
        """Return the id by default."""
        return cls.get_obj_id(vt_obj)

    @classmethod
    def get_obj_id(cls, vt_obj):
        return vt_obj.id

    @classmethod
    def finish_save(cls, vt_obj):
        pass

class VistrailXMLSerializer(XMLFileSerializer):
    @classmethod
    def load(cls, filename):
        obj = super(VistrailXMLSerializer, cls).load(filename, 
                                                     DBVistrail.vtType,
                                                     "translateVistrail")
        vistrails.db.services.vistrail.update_id_scope(obj.obj)
        return obj

    @classmethod
    def save(cls, obj, rootdir):
        version = vistrails.db.versions.currentVersion
        return super(VistrailXMLSerializer, cls).save(obj, rootdir, version, 
                                    "http://www.vistrails.org/vistrail.xsd",
                                                      "translateVistrail")

    @classmethod
    def get_obj_id(cls, vt_obj):
        return 'vistrail'


class MashupXMLSerializer(XMLFileSerializer):
    @classmethod
    def load(cls, filename):
        return super(MashupXMLSerializer, cls).load(filename, 
                                                  DBMashuptrail.vtType,
                                                  "translateMashup", "mashups")
        
    def save(cls, obj, rootdir):
        version = vistrails.db.versions.currentVersion
        return super(MashupXMLSerializer, cls).save(obj, rootdir, version, 
                                    "http://www.vistrails.org/mashup.xsd",
                                                  "translateVistrail",
                                                  "mashups")

class RegistryXMLSerializer(XMLFileSerializer):
    @classmethod
    def load(cls, filename):
        obj = super(RegistryXMLSerializer, cls).load(filename, 
                                                     DBRegistry.vtType, 
                                                     "translateRegistry")
        vistrails.db.services.regsitry.update_id_scope(obj.obj)
        return obj

    @classmethod
    def save(cls, obj, filename, version):
        version = vistrails.db.versions.currentVersion
        return super(RegistryXMLSerializer, cls).save(cls, obj, filename, 
                                                      version,
                                    "http://www.vistrails.org/registry.xsd",
                                                      "translateRegistry")

    @classmethod
    def get_obj_id(cls, vt_obj):
        return 'registry'
                               
class XMLAppendSerializer(XMLFileSerializer):
    @classmethod
    def load(cls, filename, obj_type, obj_tag, inner_obj_type, translator_f):
        parser = ElementTree.XMLTreeBuilder()
        parser.feed("<%s>\n" % obj_tag)
        f = open(filename, "rb")
        parser.feed(f.read())
        parser.feed("</%s>\n" % obj_tag)
        root = parser.close()
        obj_list = []
        for node in root:
            version = cls.get_version_for_xml(node)
            daoList = vistrails.db.versions.getVersionDAO(version)
            inner_obj = daoList.read_xml_object(inner_obj_type, node)
            currentVersion = vistrails.db.versions.currentVersion
            if version != currentVersion:
                # if version is wrong, dump this into a dummy object, 
                # then translate, then get inner_obj back
                vt_obj = cls.create_obj()
                vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                       currentVersion, version)
                cls.add_inner_obj(vt_obj, inner_obj)
                vt_obj = vistrails.db.versions.translate_object(vt_obj, 
                                                                translator_f, 
                                                                version)
                inner_obj = cls.get_inner_objs(vt_obj)[0]
            obj_list.append(inner_obj)
        vt_obj = cls.create_obj(obj_list)
        obj_id = cls.get_obj_id(vt_obj)
        obj = BundleObj(vt_obj, obj_type, obj_id)
        return obj

    @classmethod
    def save(cls, obj, rootdir, version, schema, translator_f):
        """Here, we assume that obj.obj is a **list**"""

        vt_obj = obj.obj
        obj_path = cls.get_obj_path(obj)
        filename = os.path.join(rootdir, obj_path)
        file_obj = open(filename, 'ab')
        for inner_obj in cls.get_inner_objs(vt_obj):
            cur_id = inner_obj.db_id
            inner_obj.db_id = -1
            inner_bundle_obj = BundleObj(inner_obj, DBWorkflowExec.vtType, -1)
            XMLAppendSerializer.save_file(inner_bundle_obj, 
                                          file_obj, version, 
                                          schema, translator_f)
            inner_obj.db_id = cur_id
        vistrails.db.versions.translate_object(obj, translator_f, version)
        return filename

    @classmethod
    def create_obj(cls, inner_obj_list):
        raise NotImplementedError("Subclass must implement create_obj")

    @classmethod
    def add_inner_obj(cls, vt_obj, inner_obj):
        raise NotImplementedError("Subclass must implement add_inner_obj")

    @classmethod
    def get_inner_obj(cls, vt_obj):
        raise NotImplementedError("Subclass must implment get_inner_obj")

class LogXMLSerializer(XMLAppendSerializer):
    @classmethod
    def load(cls, filename):
        obj = super(LogXMLSerializer, cls).load(filename, DBLog.vtType, 'log',
                                                DBWorkflowExec.vtType,
                                                "translateLog")
        vistrails.db.services.log.update_ids(obj.obj)
        return obj

    @classmethod
    def save(cls, obj, rootdir):
        version = vistrails.db.versions.currentVersion
        return super(LogXMLSerializer, cls).save(obj, rootdir, version,
                                                 "http://www.vistrails.org/log.xsd",
                                                 "translateLog")
        
    @classmethod
    def create_obj(cls, inner_obj_list=None):
        if inner_obj_list:
            return DBLog(workflow_execs=inner_obj_list)
        return DBLog()

    @classmethod
    def get_obj_id(cls, obj):
        return "log"

    @classmethod
    def add_inner_obj(cls, vt_obj, inner_obj):
        vt_obj.db_add_workflow_exec(inner_obj)

    @classmethod
    def get_inner_objs(cls, vt_obj):
        return vt_obj.db_workflow_execs

class DBDataSerializer(Serializer):
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
        c.execute(connection_obj.format_stmt(DBDataSerializer.STMTS["load"]), 
                  (db_id,))
        rows = c.fetchall()
        data = rows[0][0]
        obj = BundleObj(data, 'data')
        return obj

    @staticmethod
    def save(obj, connection_obj):
        import sqlite3
        c = connection_obj.get_connection().cursor()

        c.execute(connection_obj.format_stmt(DBDataSerializer.STMTS["insert"]), 
                  (sqlite3.Binary(obj.obj),))
        db_id = c.lastrowid
        connection_obj.get_connection().commit()
        return db_id

class BaseDBSerializer(DBDataSerializer):
    @classmethod
    def load(cls, db_id, connection_obj, obj_type, translator_f, lock=False, 
             version=None):
        db_connection = connection_obj.get_connection()
        if version is None:
            version = get_db_object_version(db_connection, db_id, obj_type)
        dao_list = vistrails.db.versions.getVersionDAO(version)
        vt_obj = dao_list.open_from_db(db_connection, obj_type, db_id, lock)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                        version)
        obj_id = cls.get_obj_id(vt_obj)
        obj = BundleObj(vt_obj, obj_type, obj_id)
        return obj

    @classmethod
    def save(cls, obj, connection_obj, translator_f, overwrite=True,
             version=None):
        db_connection = connection_obj.get_connection()
        if version is None:
            version = cls.get_db_version(db_connection)
            if version is None:
                version = vistrails.db.versions.currentVersion

        # if not vt_obj.db_version:
        #     vt_obj.db_version = currentVersion

        vt_obj = obj.obj

        dao_list = vistrails.db.versions.getVersionDAO(version)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f,
                                                        vt_obj.db_version, 
                                                        version)
        dao_list.save_to_db(db_connection, vt_obj, overwrite)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, version,
                                        vistrails.db.versions.currentVersion)

        cls.finish_save(vt_obj, db_connection, dao_list)
        db_connection.commit()
        return vt_obj.db_id
    
    @staticmethod
    def translate_to_tbl_name(obj_type):
        map = {DBVistrail.vtType: 'vistrail',
               DBWorkflow.vtType: 'workflow',
               DBLog.vtType: 'log_tbl',
               DBRegistry.vtType: 'registry',
               DBAbstraction.vtType: 'abstraction',
               DBMashuptrail.vtType: 'mashuptrail',
               DBAnnotation.vtType: 'annotation',
               }
        return map[obj_type]

    @classmethod
    def get_db_object_version(db_connection, obj_id, obj_type):
        command = """
        SELECT o.version
        FROM %s o
        WHERE o.id = %s
        """

        version = vistrails.db.versions.currentVersion
        try:
            c = db_connection.cursor()
            #print command % (cls.translate_to_tbl_name(obj_type), obj_id)
            c.execute(command % (cls.translate_to_tbl_name(obj_type), obj_id))
            version = c.fetchall()[0][0]
            c.close()
        finally:
            return version

    @staticmethod
    def get_db_version(db_connection):
        command = """
        SELECT `version`
        FROM `vistrails_version`
        """

        try:
            c = db_connection.cursor()
            c.execute(command)
            version = c.fetchall()[0][0]
            c.close()
        finally:
            # just return None if we hit an error
            return None
        return version

    @classmethod
    def get_obj_path(cls, vt_obj):
        """Return the id by default."""
        return cls.get_obj_id(vt_obj)

    @classmethod
    def get_obj_id(cls, vt_obj):
        return vt_obj.id

    @classmethod
    def finish_save(cls, obj, db_connection, dao_list):
        pass

class VistrailDBSerializer(BaseDBSerializer):
    @classmethod
    def load(cls, db_id, connection_obj, lock=False, version=None):
        obj = super(VistrailDBSerializer, cls).load(db_id, connection_obj, 
                                                    DBVistrail.vtType, 
                                                    "translateVistrail", lock, 
                                                    version)
        for db_action in obj.obj.db_get_actions():
            db_action.db_operations.sort(key=lambda x: x.db_id)
        vistrails.db.services.vistrail.update_id_scope(obj.obj)
        return obj

    @classmethod
    def save(cls, obj, connection_obj, overwrite=True):
        # current_action holds the current action id 
        # (used by the controller--write_vistrail)
        version = vistrails.db.versions.currentVersion
        vt_obj = obj.obj
        current_action = vt_obj.db_currentVersion

        if overwrite and vt_obj.db_last_modified is not None:
            new_time = get_db_object_modification_time(db_connection, 
                                                       vt_obj.db_id,
                                                       DBVistrail.vtType)
            if new_time > vt_obj.db_last_modified:
                # need synchronization
                old_vistrail = open_vistrail_from_db(db_connection,
                                                     vt_obj.db_id,
                                                     True, version)
                old_vistrail = vistrails.db.version.translate_vistrail(
                    old_vistrail, version)
                # the "old" one is modified and changes integrated
                current_action = \
                    vistrails.db.services.vistrail.synchronize(old_vistrail, 
                                                               vt_obj, 
                                                               current_action)
                obj.obj = old_vistrail
                obj.obj.db_currentVersion = current_action
        obj.obj.db_last_modified = connection_obj.get_current_time()
        
        db_id = super(VistrailDBSerializer, cls).save(obj, connection_obj, 
                                                      "translateVistrail", 
                                                      overwrite, version)
        return db_id

    @staticmethod
    def get_saved_workflows(vistrail, db_connection):
        """ Returns list of action id:s representing populated workflows.
        """
        if not vistrail.db_id:
            return []
        c = db_connection.cursor()
        c.execute("SELECT parent_id FROM workflow WHERE vistrail_id=%s;", 
                  (vistrail.db_id,))
        ids = [i[0] for i in c.fetchall()]
        c.close()
        return ids

    @classmethod
    def finish_save(cls, vt_obj, db_connection, dao_list):
        # update all missing tagged workflows
        # get saved workflows from db
        workflowIds = cls.get_saved_workflows(vt_obj, db_connection)
        #print "Workflows already saved:", workflowIds
        tagMap = {}
        for annotation in vt_obj.db_actionAnnotations:
            if annotation.db_key == '__tag__':
                tagMap[annotation.db_action_id] = annotation.db_value
        wfToSave = []
        for id, name in tagMap.iteritems():
            if id not in workflowIds:
                #print "creating workflow", vt_obj.db_id, id, name,
                workflow = vistrails.db.services.vistrail.materializeWorkflow(vt_obj, id)
                workflow.db_id = None
                workflow.db_vistrail_id = vt_obj.db_id
                workflow.db_parent_id = id
                workflow.db_group = id
                workflow.db_last_modified = \
                                    vt_obj.db_get_action_by_id(id).db_date
                workflow.db_name = name
                wfToSave.append(workflow)
        if wfToSave:
            dao_list.save_many_to_db(db_connection, wfToSave, True)
        # vt_obj.db_currentVersion = current_action

class WorkflowDBSerializer(BaseDBSerializer):
    @classmethod
    def load(cls, db_id, connection_obj):
        pass

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

class DirectorySerializer(BundleSerializer):
    def __init__(self, dir_path, bundle=None, overwrite=False, *args, **kwargs):
        BundleSerializer.__init__(self, bundle, *args, **kwargs)
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
        if self._bundle is None:
            self._bundle = Bundle()
        self.load_manifest(dir_path)
        for obj_type, obj_id, fname in self._manifest.get_items():
            serializer = self.get_serializer(obj_type, 
                                        FileSerializer.get_serializer_type())
            path = os.path.join(dir_path, fname)
            obj = serializer.load(path)
            if obj is not None:
                if obj.id is None:
                    obj.id = obj_id
                if obj.obj_type is None:
                    obj.obj_type = obj_type
                self._bundle.add_object(obj)
        return self._bundle

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

        for obj_type, obj_id, obj in self._bundle.get_items():
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

class ZIPSerializer(DirectorySerializer):
    # a zipped version of a directory bundle
    def __init__(self, file_path, bundle=None, overwrite=False, 
                 *args, **kwargs):
        DirectorySerializer.__init__(self, None, bundle, *args, **kwargs)
        self._file_path = file_path

    def load(self, file_path=None):
        # have path and temp dir 
        #
        # first unzip it to a temporary directory and then
        # treat it like a directory bundle
        if file_path is None:
            file_path = self._file_path

        vistrails.core.requirements.require_executable('unzip')

        if self._dir_path is None:
            self._dir_path = tempfile.mkdtemp(prefix='vt_save')

        output = []
        cmdline = ['unzip', '-q','-o','-d', self._dir_path, file_path]
        result = execute_cmdline(cmdline, output)

        if result != 0 and len(output) != 0:
            raise VistrailsDBException("Unzip of '%s' failed" % file_path)

        return DirectorySerializer.load(self)

    def save(self, file_path=None):
        # first save everything to a temporary directory as a
        # directory bundle and then zip it
        if file_path is None:
            file_path = self._file_path
        if self._dir_path is None:
            self._dir_path = tempfile.mkdtemp(prefix='vt_save')
        # FIXME should we overwrite?
        DirectorySerializer.save(self, overwrite=True)

        tmp_zip_dir = tempfile.mkdtemp(prefix='vt_zip')
        tmp_zip_file = os.path.join(tmp_zip_dir, "vt.zip")
        output = []
        rel_vt_save_dir = os.path.split(self._dir_path)[1]

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
            with Chdir(self._dir_path):
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
        if self._dir_path is not None:
            shutil.rmtree(self._dir_path)

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

class DBSerializer(BundleSerializer):
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

    def __init__(self, connection_obj, bundle_id=None, name="", bundle=None,
                 overwrite=False, *args, **kwargs):
        BundleSerializer.__init__(self, bundle, *args, **kwargs)
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
        if self._bundle is None:
            self._bundle = Bundle()
        self.load_manifest(connection_obj, bundle_id)

        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(self.STMTS["load"]), (bundle_id,))
        rows = c.fetchall()
        self._name = rows[0][0]

        for obj_type, obj_id, db_id in self._manifest.get_items():
            serializer = self.get_serializer(obj_type, 
                                        DBDataSerializer.get_serializer_type())
            obj = serializer.load(db_id, connection_obj)
            if obj is not None:
                if obj.id is None:
                    obj.id = obj_id
                if obj.obj_type is None:
                    obj.obj_type = obj_type
                self._bundle.add_object(obj)

        return self._bundle

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
        for obj_type, obj_id, obj in self._bundle.get_items():
            try:
                serializer = self.get_serializer(obj_type, 
                                    DBDataSerializer.get_serializer_type())
                db_id = serializer.save(obj, connection_obj)
                self._manifest.add_entry(obj_type, obj_id, db_id)
            except VistrailsDBException, e:
                import traceback
                traceback.print_exc()
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
        connection_obj.get_connection().commit()

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

class DefaultVistrailsDirSerializer(DirectorySerializer):
    def __init__(self, dir_path, bundle=None, overwrite=False, *args, **kwargs):
        DirectorySerializer.__init__(self, dir_path, bundle, overwrite, 
                                 *args, **kwargs)
        self.add_serializer("vistrail", VistrailXMLSerializer)
        self.add_serializer("log", LogXMLSerializer)
        self.add_serializer("mashup", MashupXMLSerializer)
        self.add_serializer("thumbnail", ThumbnailFileSerializer)
        self.add_serializer("abstraction", AbstractionFileSerializer)    

class DefaultVistrailsZIPSerializer(ZIPSerializer):
    def __init__(self, file_path, bundle=None, overwrite=False, 
                 *args, **kwargs):
        ZIPSerializer.__init__(self, file_path, bundle, overwrite, 
                               *args, **kwargs)
        self.add_serializer("vistrail", VistrailXMLSerializer)
        self.add_serializer("log", LogXMLSerializer)
        self.add_serializer("mashup", MashupXMLSerializer)
        self.add_serializer("thumbnail", ThumbnailFileSerializer)
        self.add_serializer("abstraction", AbstractionFileSerializer)    

class DefaultVistrailsDBSerializer(DBSerializer):
    def __init__(self, connection_obj, bundle_id=None, name="", bundle=None,
                 overwrite=False, *args, **kwargs):
        DBSerializer.__init__(self, connection_obj, bundle_id, name, bundle,
                              overwrite, *args, **kwargs)
        self.add_serializer("vistrail", VistrailDBSerializer)

class NoManifestMixin(object):
    def load_manifest(self, dir_path=None, fname=None):
        if dir_path is None:
            dir_path = self._dir_path
        self._manifest = FileManifest()

        for root, dirs, files in os.walk(dir_path):
            for fname in files:
                if fname == 'vistrail' and root == dir_path:
                    self._manifest.add_entry('vistrail', 'vistrail', 'vistrail')
                elif fname == 'log' and root == dir_path:
                    self._manifest.add_entry('log', 'log', 'log')
                elif fname.startswith('abstraction_'):
                    abs_id = fname[len('abstraction_'):]
                    self._manifest.add_entry('abstraction', abs_id, fname)
                elif root == os.path.join(dir_path,'thumbs'):
                    self._manifest.add_entry('thumbnail', fname, 
                                             os.path.join('thumbs', fname))
                elif root == os.path.join(dir_path,'mashups'):
                    self._manifest.add_entry('mashup', fname,
                                             os.path.join('mashups', fname))

class NoManifestDirSerializer(DefaultVistrailsDirSerializer, NoManifestMixin):
    def load_manifest(self, dir_path=None, fname=None):
        NoManifestMixin.load_manifest(self, dir_path, fname)

class NoManifestZIPSerializer(DefaultVistrailsZIPSerializer, NoManifestMixin):
    def load_manifest(self, dir_path=None, fname=None):
        NoManifestMixin.load_manifest(self, dir_path, fname)
    
    

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

from vistrails.core.system import resource_directory, vistrails_root_directory

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

    def create_bundle(self):
        b = Bundle()
        fname1 = os.path.join(resource_directory(), 'images', 'info.png')
        o1 = FileSerializer.load(fname1)
        o1.id = "abc"
        b.add_object(o1)
        fname2 = os.path.join(resource_directory(), 'images', 'left.png')
        o2 = FileSerializer.load(fname2)
        o2.id = "def"
        b.add_object(o2)
        return b

    def compare_bundles(self, b1, b2):
        self.assertEqual(len(b1.get_items()), len(b2.get_items()))
        for obj_type, obj_id, obj in b1.get_items():
            obj2 = b2.get_object(obj_type, obj_id)
            # not ideal, but fails when trying to compare objs without __eq__
            self.assertEqual(obj.__class__, obj2.__class__)
            # self.assertEqual(str(obj.obj), str(obj2.obj))

    def test_dir_bundle(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')
        try:
            b1 = self.create_bundle()
            s1 = DirectorySerializer(inner_d, b1)
            s1.add_serializer('data', FileSerializer)
            s1.save()

            s2 = DirectorySerializer(inner_d)
            s2.add_serializer('data', FileSerializer)
            b2 = s2.load()

            self.compare_bundles(b1, b2)
        finally:
            shutil.rmtree(d)
            # pass
        
    def test_zip_bundle(self):
        (h, fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)
        s1 = None
        s2 = None
        try:
            b1 = self.create_bundle()
            s1 = ZIPSerializer(fname, b1)
            s1.add_serializer('data', FileSerializer)
            s1.save()

            s2 = ZIPSerializer(fname)
            s2.add_serializer('data', FileSerializer)
            b2 = s2.load()
            
            self.compare_bundles(b1, b2)
        finally:
            if s1:
                s1.cleanup()
            if s2:
                s2.cleanup()
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
        c.execute(connection_obj.format_stmt(DBSerializer.SCHEMA))
        c.execute(connection_obj.format_stmt(DBDataSerializer.SCHEMA))

        s1 = None
        s2 = None
        try:
            b1 = self.create_bundle()
            s1 = DBSerializer(connection_obj, name="test", bundle=b1)
            s1.add_serializer('data', DBDataSerializer)
            s1.save()

            s2 = DBSerializer(connection_obj, bundle_id=1)
            s2.add_serializer('data', DBDataSerializer)
            b2 = s2.load()

            self.compare_bundles(b1, b2)
        finally:
            if s1:
                s1.cleanup()
            if s2:
                s2.cleanup()
            c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
            c.execute(connection_obj.format_stmt(DBSerializer.DROP_SCHEMA));
            c.execute(connection_obj.format_stmt(DBDataSerializer.DROP_SCHEMA));
            db.cleanup()

    def test_manifest_mysql(self):
        self.run_manifest_db(MySQLDatabaseTest)

    def test_manifest_sqlite3(self):
        self.run_manifest_db(SQLite3DatabaseTest)

    def test_bundle_mysql(self):
        self.run_bundle_db(MySQLDatabaseTest)

    def test_bundle_sqlite3(self):
        self.run_bundle_db(SQLite3DatabaseTest)

    def create_vt_bundle(self):
        from vistrails.db.domain import DBVistrail
        from vistrails.db.domain import DBLog

        b = Bundle()
        b.add_object(BundleObj(DBVistrail(), 'vistrail', 'vistrail'))
        b.add_object(BundleObj(DBLog(), 'log', 'log'))
        fname1 = os.path.join(resource_directory(), 'images', 'info.png')
        b.add_object(BundleObj(fname1, 'thumbnail', 'info.png'))
        fname2 = os.path.join(resource_directory(), 'images', 'left.png')
        b.add_object(BundleObj(fname2, 'thumbnail', 'left.png'))
        return b

    def test_vt_dir_bundle(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')

        s1 = None
        s2 = None
        try:
            b1 = self.create_vt_bundle()
            s1 = DefaultVistrailsDirSerializer(inner_d, b1)
            s1.save()

            s2 = DefaultVistrailsDirSerializer(inner_d)
            b2 = s2.load()
            
            self.compare_bundles(b1, b2)
        finally:
            shutil.rmtree(d)

    def test_vt_zip_bundle(self):
        (h, fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)

        s1 = None
        s2 = None
        try:
            b1 = self.create_vt_bundle()
            s1 = DefaultVistrailsZIPSerializer(fname, b1)
            s1.save()

            s2 = DefaultVistrailsZIPSerializer(fname)
            b2 = s2.load()
            
            self.compare_bundles(b1, b2)
        finally:
            if s1:
                s1.cleanup()
            if s2:
                s2.cleanup()
            os.unlink(fname)

    def test_old_vt_dir_load(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')

        s1 = None
        s2 = None
        try:
            s1 = NoManifestDirSerializer('/vistrails/tmp/terminator')
            b1 = s1.load()
            s2 = DefaultVistrailsDirSerializer(inner_d, b1)
            s2.save()
        finally:
            shutil.rmtree(d)

    def test_old_vt_zip_load(self):
        in_fname = os.path.join(vistrails_root_directory(),'tests', 
                                'resources', 'terminator.vt')
        (h, out_fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)

        s1 = None
        s2 = None
        try:
            s1 = NoManifestZIPSerializer(in_fname)
            b1 = s1.load()
            s2 = DefaultVistrailsZIPSerializer(out_fname, b1)
            s2.save()
        finally:
            os.unlink(out_fname)

    def run_vt_db_bundle(self, db_klass):
        in_fname = os.path.join(vistrails_root_directory(),'tests', 
                                'resources', 'terminator.vt')
        (h, out_fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)

        try:
            db = db_klass()
        except ImportError:
            self.skipTest("Cannot import dependencies for %s." % \
                          db_klass.__name__)
        db_version = vistrails.db.versions.currentVersion
        connection_obj = db.setup()
        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
        c.execute(connection_obj.format_stmt(DBSerializer.SCHEMA))
        schema_dir = vistrails.db.versions.getVersionSchemaDir(db_version)
        vt_schema = os.path.join(schema_dir, 'vistrails.sql')
        connection_obj.run_sql_file(vt_schema)

        s1 = None
        s2 = None
        try:
            s1 = NoManifestZIPSerializer(in_fname)
            b1 = s1.load()
            s2 = DefaultVistrailsDBSerializer(connection_obj, bundle=b1)
            s2.save()
        finally:
            if s1:
                s1.cleanup()
            if s2:
                s2.cleanup()
            c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
            c.execute(connection_obj.format_stmt(DBSerializer.DROP_SCHEMA));
            # schema_dir = vistrails.db.versions.getVersionSchemaDir(db_version)
            # vt_drop_schema = os.path.join(schema_dir, 'vistrails_drop.sql')
            # connection_obj.run_sql_file(vt_drop_schema)
            db.cleanup()

    def test_vt_bundle_mysql(self):
        self.run_vt_db_bundle(MySQLDatabaseTest)        

    def test_vt_bundle_sqlite(self):
        self.run_vt_db_bundle(SQLite3DatabaseTest)

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestBundles("test_vt_bundle_sqlite"))
    unittest.TextTestRunner().run(suite)
                  
