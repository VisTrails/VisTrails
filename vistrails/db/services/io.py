###############################################################################
##
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
from __future__ import with_statement

from datetime import datetime
from vistrails.core import debug
from vistrails.core.bundles import py_import
from vistrails.core.system import get_elementtree_library, strftime
from vistrails.core.utils import Chdir
from vistrails.core.mashup.mashup_trail import Mashuptrail
from vistrails.core.modules.sub_module import get_cur_abs_namespace,\
    parse_abstraction_name, read_vistrail_from_db

import vistrails.core.requirements

import os.path
import shutil
import tempfile
import copy
import zipfile

from vistrails.db import VistrailsDBException
from vistrails.db.domain import DBVistrail, DBWorkflow, DBLog, DBAbstraction, DBGroup, \
    DBRegistry, DBWorkflowExec, DBOpmGraph, DBProvDocument, DBAnnotation, \
    DBMashuptrail, DBStartup
import vistrails.db.services.abstraction
import vistrails.db.services.log
import vistrails.db.services.opm
import vistrails.db.services.prov
import vistrails.db.services.registry
import vistrails.db.services.workflow
import vistrails.db.services.vistrail
from vistrails.db.versions import getVersionDAO, currentVersion, getVersionSchemaDir, \
    translate_vistrail, translate_workflow, translate_log, translate_registry, translate_startup

import unittest
import vistrails.core.system

ElementTree = get_elementtree_library()

CONNECT_TIMEOUT = 15

_db_lib = None
def get_db_lib():
    global _db_lib
    if _db_lib is None:
        MySQLdb = py_import('MySQLdb', {
                'pip': 'mysql-python',
                'linux-debian': 'python-mysqldb',
                'linux-ubuntu': 'python-mysqldb',
                'linux-fedora': 'MySQL-python'})
        # import sqlite3
        _db_lib = MySQLdb
    return _db_lib
def set_db_lib(lib):
    global _db_lib
    _db_lib = lib


class SaveBundle(object):
    """Transient bundle of objects to be saved or loaded.
       The bundle type MUST be specified in the constructor; it should be
       the the vtType of the primary object in the bundle. This parameter
       identifies which object is the primary object when mutiple objects
       are stored in the bundle.

       Args is the (unordered) list of objects to be included in the bundle
       (vistrail, workflow, log, registry, opm_graph).  Any args without a
       'vtType' attribute are explicitly ignored (including any args=None).

       As kwargs, you can specify 'abstractions=[]' or 'thumbnails=[]',
       both of which should be a list of filenames as strings.  You can also
       specify the other bundle objects as kwargs, but abstractions and
       thumbnails cannot be args, since they are both lists, and there is no
       vtType to differentiate between them.

       As a final option, you can directly set the objects in the bundle,
       self.vistrail = vistrail_object, self.thumbnails = thumbs_list, etc.,
       before passing the SaveBundle to a locator.  Both abstractions and
       thumbnails are intialized for convenience so that you can directly
       append to them when using this step-by-step bundle creation method.

    """

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
        return [obj for obj in self.__dict__.itervalues() if obj is not None and not isinstance(obj, (list, basestring))]

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

        for m in self.mashups:
            cp.mashups.append(m)
        
        return cp

def format_prepared_statement(statement):
    """format_prepared_statement(statement: str) -> str
    Formats a prepared statement for compatibility with the currently
    loaded database library's paramstyle.

    Currently only supports 'qmark' and 'format' paramstyles.
    May be expanded later to allow for more compatibility options
    on input and output.  See PEP 249 for more info.

    """
    style = get_db_lib().paramstyle
    if style == 'format':
        return statement.replace("?", "%s")
    elif style == 'qmark':
        return statement.replace("%s", "?")
    return statement

def open_db_connection(config):

    if config is None:
        msg = "You need to provide valid config dictionary"
        raise VistrailsDBException(msg)
    if 'connect_timeout' not in config:
        config['connect_timeout'] = CONNECT_TIMEOUT
    try:
        # FIXME allow config to be kwargs and args?
        db_connection = get_db_lib().connect(**config)
        #db_connection = get_db_lib().connect(config)
        return db_connection
    except get_db_lib().Error, e:
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
    #print "Testing config", config
    if 'connect_timeout' not in config:
        config['connect_timeout'] = CONNECT_TIMEOUT
    try:
        db_connection = get_db_lib().connect(**config)
        close_db_connection(db_connection)
    except get_db_lib().Error, e:
        msg = "connection test failed (%d: %s)" % (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    except TypeError, e:
        msg = "connection test failed (%s)" %str(e)
        raise VistrailsDBException(msg)

def ping_db_connection(db_connection):
    """ping_db_connection(db_connection) -> boolean 
    It will ping the database to check if the connection is alive.
    It returns True if it is, False otherwise. 
    This can be used for preventing the "MySQL Server has gone away" error. 
    """
    try:
        db_connection.ping()
    except get_db_lib().OperationalError:
        return False
    return True
    
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

def date_to_str(date):
    return strftime(date, '%Y-%m-%d %H:%M:%S')

def get_db_object_list(config, obj_type):
    
    result = []    
    db = open_db_connection(config)

    #FIXME Create a DBGetVistrailListSQLDAOBase for this
    # and maybe there's another way to build this query
    command = """SELECT o.id, o.name, o.last_modified
    FROM %s o ORDER BY o.name"""

    # if it is a vistrail we need to remove abstractions
    if obj_type == DBVistrail.vtType:
        id_key = '__abstraction_uuid__'
        command = """SELECT o.id, o.name, o.last_modified
        FROM %s o"""
        command += """ WHERE o.id not in ( SELECT o.id
          FROM %s o, %s a
          WHERE o.id = a.parent_id AND '%s' = a.parent_type AND a.akey = '%s')
        ORDER BY o.name""" % (translate_to_tbl_name(obj_type),
                              translate_to_tbl_name(DBAnnotation.vtType),
                              translate_to_tbl_name(obj_type),
                              id_key)
#     command = """SELECT o.id, v.name, a.date, a.user
#     FROM %s o, action a,
#     (SELECT a.entity_id, MAX(a.date) as recent, a.user
#     FROM action a
#     GROUP BY entity_id) latest
#     WHERE o.id = latest.entity_id 
#     AND a.entity_id = o.id
#     AND a.date = latest.recent 
#     """ % obj_type

    try:
        c = db.cursor()
        c.execute(command % translate_to_tbl_name(obj_type))
        rows = c.fetchall()
        result = rows
        c.close()
        close_db_connection(db)
        
    except get_db_lib().Error, e:
        msg = "Couldn't get list of vistrails objects from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return result

def get_db_object_modification_time(db_connection, obj_id, obj_type):
    command = """
    SELECT o.last_modified
    FROM %s o
    WHERE o.id = %s
    """

    try:
        db_connection.begin()
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(obj_type), obj_id))
        db_connection.commit()
        time = c.fetchall()[0][0]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get object modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return time

def get_db_object_version(db_connection, obj_id, obj_type):
    command = """
    SELECT o.version
    FROM %s o
    WHERE o.id = %s
    """

    try:
        c = db_connection.cursor()
        #print command % (translate_to_tbl_name(obj_type), obj_id)
        c.execute(command % (translate_to_tbl_name(obj_type), obj_id))
        version = c.fetchall()[0][0]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get object version from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return version

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
    except get_db_lib().Error, e:
        # just return None if we hit an error
        return None
    return version

def get_db_id_from_name(db_connection, obj_type, name):
    command = """
    SELECT o.id 
    FROM %s o
    WHERE o.name = '%s'
    """

    try:
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(obj_type), name))
        rows = c.fetchall()
        if len(rows) != 1:
            if len(rows) == 0:
                c.close()
                msg = "Cannot find object of type '%s' named '%s'" % \
                    (obj_type, name)
                raise VistrailsDBException(msg)
            elif len(rows) > 1:
                c.close()
                msg = "Found more than one object of type '%s' named '%s'" % \
                    (obj_type, name)
                raise VistrailsDBException(msg)
        else:
            c.close()
            return int(rows[0][0])
    except get_db_lib().Error, e:
        c.close()
        msg = "Connection error when trying to get db id from name"
        raise VistrailsDBException(msg)

def get_db_abstraction_modification_time(db_connection, abstraction):
    id_key = '__abstraction_vistrail_id__'
    command = """
    SELECT o.last_modified
    FROM %s o, %s a
    WHERE o.id = %s AND
          o.id = a.parent_id AND
          '%s' = a.parent_type AND
          a.akey = '""" + id_key + """' AND
          a.value = '%s'
    """

    if abstraction.db_has_annotation_with_key(id_key):
        id_value = abstraction.db_get_annotation_by_key(id_key).db_value
    else:
        return None

    try:
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(DBVistrail.vtType), 
                             translate_to_tbl_name(DBAnnotation.vtType),
                             abstraction.db_id,
                             translate_to_tbl_name(DBVistrail.vtType),
                             id_value))
        modtime = c.fetchall()[0][0]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return modtime

def get_db_abstraction_ids_from_vistrail(db_connection, vt_id):
    """ get_db_abstractions_from_vistrail(db_connection: DBConnection,
                                          vt_id: int): List
        Returns abstractions associated with a vistrail
    """
    
    id_key = '__abstraction_vistrail_id__'
    return get_db_ids_from_vistrail(db_connection, vt_id, id_key)

def get_db_mashuptrail_ids_from_vistrail(db_connection, vt_id):
    """ get_db_mashuptrail_ids_from_vistrail(db_connection: DBConnection,
                                          vt_id: int): List
        Returns mashuptrails associated with a vistrail
    """
    id_key = '__mashuptrail_vistrail_id__'
    return get_db_ids_from_vistrail(db_connection, vt_id, id_key)
    
def get_db_ids_from_vistrail(db_connection, vt_id, id_key):
    """ get_db_ids_from_vistrail(db_connection: DBConnection,
                                 vt_id: int, id_key: str): List
        Returns object ids associated with a vistrail by an annotation
    """
    command = """
    SELECT a.parent_id FROM %s a
    WHERE a.akey = '%s' AND a.value = '%s'"""

    try:
        c = db_connection.cursor()
        c.execute(command%(translate_to_tbl_name(DBAnnotation.vtType), id_key, vt_id))
        abs_ids = c.fetchall()
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get object ids from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return [i[0] for i in abs_ids]

def get_matching_abstraction_id(db_connection, abstraction):
    last_action_id = -1
    last_action = None
    for action in abstraction.db_actions:
        if action.db_id > last_action_id:
            last_action_id = action.db_id
            last_action = action

    command = """
    SELECT g.id 
    FROM abstraction g, action a
    WHERE g.name = '%s'
    AND a.entity_type = 'abstraction'
    AND a.entity_id = g.id
    AND a.user = '%s'
    AND a.date = '%s'
    AND a.id = %s
    """
    
    id = None
    try:
        c = db_connection.cursor()
        c.execute(command % (abstraction.db_name,
                             last_action.db_user,
                             date_to_str(last_action.db_date),
                             last_action.db_id))
        result = c.fetchall()
        c.close()
        if len(result) > 0:
            #print 'got result:', result
            id = result[0][0]
    except get_db_lib().Error, e:
        msg = "Couldn't get object modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return id

def setup_db_tables(db_connection, version=None, old_version=None):
    if version is None:
        version = currentVersion
    if old_version is None:
        old_version = version
    try:
        def execute_file(c, f):
            cmd = ""
#             auto_inc_str = 'auto_increment'
#             not_null_str = 'not null'
#             engine_str = 'engine=InnoDB;'
            for line in f:
#                 if line.find(auto_inc_str) > 0:
#                     num = line.find(auto_inc_str)
#                     line = line[:num] + line[num+len(auto_inc_str):]
#                 if line.find(not_null_str) > 0:
#                     num = line.find(not_null_str)
#                     line = line[:num] + line[num+len(not_null_str):]
                line = line.strip()
                if cmd or not line.startswith('--'):
                    cmd += line
                    ending = line
                else:
                    ending = None
                if ending and ending[-1] == ';':
                    # FIXME engine stuff switch for MySQLdb, sqlite3
                    cmd = cmd.rstrip()
#                     if cmd.endswith(engine_str):
#                         cmd = cmd[:-len(engine_str)] + ';'
                    #print cmd
                    c.execute(cmd)
                    cmd = ""

        # delete tables
        c = db_connection.cursor()
        schemaDir = getVersionSchemaDir(old_version)
        f = open(os.path.join(schemaDir, 'vistrails_drop.sql'))
        execute_file(c, f)
#         db_script = f.read()
#         c.execute(db_script)
        c.close()
        f.close()

        # create tables        
        c = db_connection.cursor()
        schemaDir = getVersionSchemaDir(version)
        f = open(os.path.join(schemaDir, 'vistrails.sql'))
        execute_file(c, f)
#         db_script = f.read()
#         c.execute(db_script)
        f.close()
        c.close()
    except get_db_lib().Error, e:
        raise VistrailsDBException("unable to create tables: " + str(e))

##############################################################################
# General I/O

def open_from_xml(filename, type):
    if type == DBVistrail.vtType:
        return open_vistrail_from_xml(filename)
    elif type == DBWorkflow.vtType:
        return open_workflow_from_xml(filename)
    elif type == DBLog.vtType:
        return open_log_from_xml(filename)
    elif type == DBRegistry.vtType:
        return open_registry_from_xml(filename)
    else:
        raise VistrailsDBException("cannot open object of type "
                                   "'%s' from xml" % type)

def save_to_xml(obj, filename, version=None):
    if obj.vtType == DBVistrail.vtType:
        return save_vistrail_to_xml(obj, filename, version)
    elif obj.vtType == DBWorkflow.vtType:
        return save_workflow_to_xml(obj, filename, version)
    elif obj.vtType == DBLog.vtType:
        return save_log_to_xml(obj, filename, version)
    elif obj.vtType == DBRegistry.vtType:
        return save_registry_to_xml(obj, filename, version)
    elif obj.vtType == DBOpmGraph.vtType:
        return save_opm_to_xml(obj, filename, version)
    elif obj.vtType == DBProvDocument.vtType:
        return save_prov_to_xml(obj, filename, version)
    else:
        raise VistrailsDBException("cannot save object of type "
                                   "'%s' to xml" % type)

def open_bundle_from_zip_xml(bundle_type, filename):
    if bundle_type == DBVistrail.vtType:
        return open_vistrail_bundle_from_zip_xml(filename)
    else:
        raise VistrailsDBException("cannot open bundle of type '%s' from zip" %\
                                       bundle_type)

def save_bundle_to_zip_xml(save_bundle, filename, tmp_dir=None, version=None):
    bundle_type = save_bundle.bundle_type
    if bundle_type == DBVistrail.vtType:
        return save_vistrail_bundle_to_zip_xml(save_bundle, filename, tmp_dir, version)
    elif bundle_type == DBLog.vtType:
        return save_log_bundle_to_xml(save_bundle, filename, version)
    elif bundle_type == DBWorkflow.vtType:
        return save_workflow_bundle_to_xml(save_bundle, filename, version)
    elif bundle_type == DBRegistry.vtType:
        return save_registry_bundle_to_xml(save_bundle, filename, version)
    else:
        raise VistrailsDBException("cannot save bundle of type '%s' to zip" % \
                                       bundle_type)

def open_bundle_from_db(bundle_type, connection, primary_obj_id, tmp_dir=None):
    if bundle_type == DBVistrail.vtType:
        return open_vistrail_bundle_from_db(connection, primary_obj_id, tmp_dir)
    else:
        raise VistrailsDBException("cannot open bundle of type '%s' from db" %\
                                       bundle_type)

def save_bundle_to_db(save_bundle, connection, do_copy=False, version=None):
    bundle_type = save_bundle.bundle_type
    if bundle_type == DBVistrail.vtType:
        return save_vistrail_bundle_to_db(save_bundle, connection, do_copy, version)
    elif bundle_type == DBLog.vtType:
        return save_log_bundle_to_db(save_bundle, connection, do_copy, version)
    elif bundle_type == DBWorkflow.vtType:
        return save_workflow_bundle_to_db(save_bundle, connection, do_copy, version)
    elif bundle_type == DBRegistry.vtType:
        return save_registry_bundle_to_db(save_bundle, connection, do_copy, version)
    else:
        raise VistrailsDBException("cannot save bundle of type '%s' to db" % \
                                       bundle_type)

def open_from_db(db_connection, type, obj_id):
    if type == DBVistrail.vtType:
        return open_vistrail_from_db(db_connection, obj_id)
    elif type == DBWorkflow.vtType:
        return open_workflow_from_db(db_connection, obj_id)
    elif type == DBLog.vtType:
        return open_log_from_db(db_connection, obj_id)
    elif type == DBRegistry.vtType:
        return open_registry_from_db(db_connection, obj_id)
    else:
        raise VistrailsDBException("cannot open object of type '%s' from db" % \
                                       type)

def save_to_db(obj, db_connection, do_copy=False):
    if obj.vtType == DBVistrail.vtType:
        return save_vistrail_to_db(obj, db_connection, do_copy)
    elif obj.vtType == DBWorkflow.vtType:
        return save_workflow_to_db(obj, db_connection, do_copy)
    elif obj.vtType == DBLog.vtType:
        return save_log_to_db(obj, db_connection, do_copy)
    elif obj.vtType == DBRegistry.vtType:
        return save_registry_to_db(obj, db_connection, do_copy)
    else:
        raise VistrailsDBException("cannot save object of type '%s' to db" % \
                                       type)

def delete_from_db(db_connection, type, obj_id):
    if type in [DBVistrail.vtType, DBWorkflow.vtType, DBLog.vtType,
                DBRegistry.vtType]:
        return delete_entity_from_db(db_connection, type, obj_id)

def close_zip_xml(temp_dir):
    """close_zip_xml(temp_dir: string) -> None
    Removes any temporary files for a vistrails file

    temp_dir: directory storing any persistent files
    """
    if temp_dir is None:
        return
    if not os.path.isdir(temp_dir):
        if os.path.isfile(temp_dir):
            os.remove(temp_dir)

        # cleanup has already happened
        return
    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
    except OSError, e:
        raise VistrailsDBException("Can't remove %s: %s" % (temp_dir, str(e)))

def serialize(object):
    daoList = getVersionDAO(currentVersion)
    return daoList.serialize(object)

def unserialize(str, obj_type):
    daoList = getVersionDAO(currentVersion)
    return daoList.unserialize(str, obj_type)
 
##############################################################################
# Vistrail I/O

def open_vistrail_from_xml(filename):
    """open_vistrail_from_xml(filename) -> Vistrail"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    try:
        daoList = getVersionDAO(version)
        vistrail = daoList.open_from_xml(filename, DBVistrail.vtType, tree)
        if vistrail is None:
            raise VistrailsDBException("Couldn't read vistrail from XML")
        vistrail = translate_vistrail(vistrail, version)
        vistrails.db.services.vistrail.update_id_scope(vistrail)
    except VistrailsDBException, e:
        if str(e).startswith('VistrailsDBException: Cannot find DAO for'):
            raise VistrailsDBException(
                "This vistrail was created by a newer version of VisTrails "
                "and cannot be opened.")
        raise e

    return vistrail

def open_vistrail_bundle_from_zip_xml(filename):
    """open_vistrail_bundle_from_zip_xml(filename) -> SaveBundle
    Open a vistrail from a zip compressed format.
    It expects that the vistrail file inside archive has name 'vistrail',
    the log inside archive has name 'log',
    abstractions inside archive have prefix 'abstraction_',
    and thumbnails inside archive are '.png' files in 'thumbs' dir

    """
    vt_save_dir = tempfile.mkdtemp(prefix='vt_save')

    z = zipfile.ZipFile(filename)
    try:
        z.extractall(vt_save_dir)
    finally:
        z.close()

    vistrail = None
    log = None
    log_fname = None
    abstraction_files = []
    unknown_files = []
    thumbnail_files = []
    mashups = []
    try:
        for root, dirs, files in os.walk(vt_save_dir):
            for fname in files:
                if fname == 'vistrail' and root == vt_save_dir:
                    vistrail = open_vistrail_from_xml(os.path.join(root, fname))
                elif fname == 'log' and root == vt_save_dir:
                    # FIXME read log to get execution info
                    # right now, just ignore the file
                    log = None 
                    log_fname = os.path.join(root, fname)
                    # log = open_log_from_xml(os.path.join(root, fname))
                    # objs.append(DBLog.vtType, log)
                elif fname.startswith('abstraction_'):
                    abstraction_file = os.path.join(root, fname)
                    abstraction_files.append(abstraction_file)
                elif (fname.endswith('.png') and
                      root == os.path.join(vt_save_dir,'thumbs')):
                    thumbnail_file = os.path.join(root, fname)
                    thumbnail_files.append(thumbnail_file)
                elif root == os.path.join(vt_save_dir,'mashups'):
                    mashup_file = os.path.join(root, fname)
                    mashup = open_mashuptrail_from_xml(mashup_file)
                    mashups.append(mashup)
                else:
                    handled = False
                    from vistrails.core.packagemanager import get_package_manager
                    pm = get_package_manager()
                    for package in pm.enabled_package_list():
                        if package.can_handle_vt_file(fname):
                            handled = True
                            continue
                    if not handled:
                        unknown_files.append(os.path.join(root, fname))
    except OSError, e:
        raise VistrailsDBException("Error when reading vt file")
    if len(unknown_files) > 0:
        raise VistrailsDBException("Unknown files in vt file: %s" % \
                                       unknown_files)
    if vistrail is None:
        raise VistrailsDBException("vt file does not contain vistrail")
    vistrail.db_log_filename = log_fname

    # call package hooks
    from vistrails.core.packagemanager import get_package_manager
    pm = get_package_manager()
    for package in pm.enabled_package_list():
        package.loadVistrailFileHook(vistrail, vt_save_dir)

    save_bundle = SaveBundle(DBVistrail.vtType, vistrail, log, 
                             abstractions=abstraction_files, 
                             thumbnails=thumbnail_files, mashups=mashups)
    return (save_bundle, vt_save_dir)

def open_vistrail_bundle_from_db(db_connection, vistrail_id, tmp_dir=None):
    """open_vistrail_bundle_from_db(db_connection, id: long, tmp_dir: str) -> SaveBundle
       Open a vistrail bundle from the database.

    """
    vt_abs_dir = tempfile.mkdtemp(prefix='vt_abs')
    vistrail = open_vistrail_from_db(db_connection, vistrail_id)
    # FIXME open log from db
    log = None
    # open abstractions from db
    abstractions = []
    try:
        for abs_id in get_db_abstraction_ids_from_vistrail(db_connection, vistrail.db_id):
            abs = read_vistrail_from_db(db_connection, abs_id, vistrail.db_version)
            abs_fname = '%s%s(%s)%s' % ('abstraction_', abs.db_name, 
                                      get_cur_abs_namespace(abs), '.xml')
            fname = os.path.join(vt_abs_dir, abs_fname)
            save_vistrail_to_xml(abs, fname)
            abstractions.append(fname)
    except Exception, e:
        import traceback
        debug.critical('Could not load abstraction from database: %s' % str(e),
                                              traceback.format_exc())
    # open mashuptrails from db
    mashuptrails = []
    try:
        for mashup_id in get_db_mashuptrail_ids_from_vistrail(db_connection, vistrail.db_id):
            mashup = open_mashuptrail_from_db(db_connection, mashup_id)
            mashuptrails.append(mashup)
    except Exception, e:
        import traceback
        debug.critical('Could not load mashuptrail from database: %s' % str(e),
                                              traceback.format_exc())
    thumbnails = open_thumbnails_from_db(db_connection, DBVistrail.vtType,
                                         vistrail_id, tmp_dir)
    return SaveBundle(DBVistrail.vtType, vistrail, log,
                      abstractions=abstractions, thumbnails=thumbnails,
                      mashups=mashuptrails)

def open_vistrail_from_db(db_connection, id, lock=False, version=None):
    """open_vistrail_from_db(db_connection, id : long, lock: bool, 
                             version: str) 
         -> DBVistrail 

    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_object_version(db_connection, id, DBVistrail.vtType)
    dao_list = getVersionDAO(version)
    vistrail = \
        dao_list.open_from_db(db_connection, DBVistrail.vtType, id, lock)
    vistrail = translate_vistrail(vistrail, version)
    for db_action in vistrail.db_get_actions():
        db_action.db_operations.sort(key=lambda x: x.db_id)
    vistrails.db.services.vistrail.update_id_scope(vistrail)
    return vistrail

def save_vistrail_to_xml(vistrail, filename, version=None):
    tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.vistrails.org/vistrail.xsd'
            }
    if version is None:
        version = currentVersion
    if not vistrail.db_version:
        vistrail.db_version = currentVersion

    # current_action holds the current action id 
    # (used by the controller--write_vistrail)
    current_action = 0L
    if hasattr(vistrail, 'db_currentVersion'):
        current_action = vistrail.db_currentVersion

    vistrail = translate_vistrail(vistrail, vistrail.db_version, version)

    daoList = getVersionDAO(version)        
    daoList.save_to_xml(vistrail, filename, tags, version)
    vistrail = translate_vistrail(vistrail, version)
    vistrail.db_currentVersion = current_action
    return vistrail

def save_vistrail_bundle_to_zip_xml(save_bundle, filename, vt_save_dir=None, version=None):
    """save_vistrail_bundle_to_zip_xml(save_bundle: SaveBundle, filename: str,
                                vt_save_dir: str, version: str)
         -> (save_bundle: SaveBundle, vt_save_dir: str)

    save_bundle: a SaveBundle object containing vistrail data to save
    filename: filename to save to
    vt_save_dir: directory storing any previous files

    Generates a zip compressed version of vistrail.
    It raises an Exception if there was an error.

    """

    if save_bundle.vistrail is None:
        raise VistrailsDBException('save_vistrail_bundle_to_zip_xml failed, '
                                   'bundle does not contain a vistrail')
    if not vt_save_dir:
        vt_save_dir = tempfile.mkdtemp(prefix='vt_save')
    # abstractions are saved in the root of the zip file
    # abstraction_dir = os.path.join(vt_save_dir, 'abstractions')
    #thumbnails and mashups have their own folder
    thumbnail_dir = os.path.join(vt_save_dir, 'thumbs')
    mashup_dir = os.path.join(vt_save_dir, 'mashups')
    
    # Save Vistrail
    xml_fname = os.path.join(vt_save_dir, 'vistrail')
    save_vistrail_to_xml(save_bundle.vistrail, xml_fname, version)

    # Save Log
    if save_bundle.vistrail.db_log_filename is not None:
        xml_fname = os.path.join(vt_save_dir, 'log')
        if save_bundle.vistrail.db_log_filename != xml_fname:
            shutil.copyfile(save_bundle.vistrail.db_log_filename, xml_fname)
            save_bundle.vistrail.db_log_filename = xml_fname

    if save_bundle.log is not None:
        xml_fname = os.path.join(vt_save_dir, 'log')
        save_log_to_xml(save_bundle.log, xml_fname, version, True)
        save_bundle.vistrail.db_log_filename = xml_fname

    # Save Abstractions
    saved_abstractions = []
    for obj in save_bundle.abstractions:
        if isinstance(obj, basestring):
            # FIXME we should have an abstraction directory here instead
            # of the abstraction_ prefix...
            if not os.path.basename(obj).startswith('abstraction_'):
                obj_fname = 'abstraction_' + os.path.basename(obj)
            else:
                obj_fname = os.path.basename(obj)
            # xml_fname = os.path.join(abstraction_dir, obj_fname)
            xml_fname = os.path.join(vt_save_dir, obj_fname)
            saved_abstractions.append(xml_fname)
            # if not os.path.exists(abstraction_dir):
            #     os.mkdir(abstraction_dir)
            # print "obj:", obj
            # print "xml_fname:", xml_fname
            if obj != xml_fname:
                # print 'copying %s -> %s' % (obj, xml_fname)
                try:
                    shutil.copyfile(obj, xml_fname)
                except Exception, e:
                    saved_abstractions.pop()
                    debug.critical('copying %s -> %s failed: %s' % \
                                       (obj, xml_fname, str(e)))
        else:
            raise VistrailsDBException('save_vistrail_bundle_to_zip_xml failed, '
                                       'abstraction list entry must be a filename')
    # Save Thumbnails
    saved_thumbnails = []
    for obj in save_bundle.thumbnails:
        if isinstance(obj, basestring):
            obj_fname = os.path.basename(obj)
            png_fname = os.path.join(thumbnail_dir, obj_fname)
            saved_thumbnails.append(png_fname)
            if not os.path.exists(thumbnail_dir):
                os.mkdir(thumbnail_dir)
            
            try:
                shutil.copyfile(obj, png_fname)
            except shutil.Error, e:
                #files are the same no need to show warning
                saved_thumbnails.pop()
            except IOError, e2:
                saved_thumbnails.pop()
                debug.warning('copying thumbnail %s -> %s failed: %s' % \
                              (obj, png_fname, str(e2)))
        else:
            raise VistrailsDBException('save_vistrail_bundle_to_zip_xml failed, '
                                       'thumbnail list entry must be a filename')
    # Save Mashups
    saved_mashups = []
    #print " mashups:"
    if len(save_bundle.mashups) > 0 and not os.path.exists(mashup_dir):
        os.mkdir(mashup_dir)
    for obj in save_bundle.mashups:
        #print "  ", obj
        try:
            xml_fname = os.path.join(mashup_dir, str(obj.id))
            save_mashuptrail_to_xml(obj, xml_fname)
            saved_mashups.append(obj)
        except Exception, e:
            raise VistrailsDBException('save_vistrail_bundle_to_zip_xml failed, '
                                       'when saving mashup: %s'%str(e))

    # call package hooks
    # it will fail if package manager has not been constructed yet
    try:
        from vistrails.core.packagemanager import get_package_manager
        pm = get_package_manager()
        for package in pm.enabled_package_list():
            package.saveVistrailFileHook(save_bundle.vistrail, vt_save_dir)
    except Exception, e:
        debug.warning("Could not call package hooks", str(e))
    tmp_zip_dir = tempfile.mkdtemp(prefix='vt_zip')
    tmp_zip_file = os.path.join(tmp_zip_dir, "vt.zip")

    z = zipfile.ZipFile(tmp_zip_file, 'w')
    try:
        with Chdir(vt_save_dir):
            # zip current directory
            for root, dirs, files in os.walk('.'):
                for f in files:
                    z.write(os.path.join(root, f))
        z.close()
        shutil.copyfile(tmp_zip_file, filename)
    finally:
        os.unlink(tmp_zip_file)
        os.rmdir(tmp_zip_dir)
    save_bundle = SaveBundle(save_bundle.bundle_type, save_bundle.vistrail,
                             save_bundle.log, thumbnails=saved_thumbnails,
                             abstractions=saved_abstractions,
                             mashups=saved_mashups)
    return (save_bundle, vt_save_dir)

def save_vistrail_bundle_to_db(save_bundle, db_connection, do_copy=False, version=None):
    if save_bundle.vistrail is None:
        raise VistrailsDBException('save_vistrail_bundle_to_db failed, '
                                   'bundle does not contain a vistrail')
    vistrail = save_vistrail_to_db(save_bundle.vistrail, db_connection, do_copy, version)
    log = None
    if save_bundle.vistrail.db_log_filename is not None:
        if save_bundle.log is not None:
            log = merge_logs(save_bundle.log,
                             save_bundle.vistrail.db_log_filename)
        else:
            log = open_log_from_xml(save_bundle.vistrail.db_log_filename, True)
    elif save_bundle.log is not None:
        log = save_bundle.log
    if log is not None:
        # Set foreign key 'vistrail_id' for the log to point at its vistrail
        log.db_vistrail_id = vistrail.db_id
        log = save_log_to_db(log, db_connection, do_copy, version)
    save_abstractions_to_db(save_bundle.abstractions, vistrail.db_id, db_connection, do_copy)
    save_mashuptrails_to_db(save_bundle.mashups, vistrail.db_id, db_connection, do_copy)
    save_thumbnails_to_db(save_bundle.thumbnails, db_connection)
    return SaveBundle(DBVistrail.vtType, vistrail, log,
                      abstractions=list(save_bundle.abstractions),
                      thumbnails=list(save_bundle.thumbnails),
                      mashups=list(save_bundle.mashups))

def save_vistrail_to_db(vistrail, db_connection, do_copy=False, version=None):
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_version(db_connection)
        if version is None:
            version = currentVersion
    if not vistrail.db_version:
        vistrail.db_version = currentVersion

    dao_list = getVersionDAO(version)

    # db_connection.begin()
    
    # current_action holds the current action id 
    # (used by the controller--write_vistrail)
    current_action = 0L
    if hasattr(vistrail, 'db_currentVersion'):
        current_action = vistrail.db_currentVersion

    if not do_copy and vistrail.db_last_modified is not None:
        new_time = get_db_object_modification_time(db_connection, 
                                                   vistrail.db_id,
                                                   DBVistrail.vtType)
        if new_time > vistrail.db_last_modified:
            # need synchronization
            old_vistrail = open_vistrail_from_db(db_connection,
                                                 vistrail.db_id,
                                                 True, version)
            old_vistrail = translate_vistrail(old_vistrail, version)
            # the "old" one is modified and changes integrated
            current_action = \
                vistrails.db.services.vistrail.synchronize(old_vistrail, vistrail, 
                                                 current_action)
            vistrail = old_vistrail
    vistrail.db_last_modified = get_current_time(db_connection)

    vistrail = translate_vistrail(vistrail, vistrail.db_version, version)
    # get saved workflows from db
    workflowIds = get_saved_workflows(vistrail, db_connection)
    #print "Workflows already saved:", workflowIds
    dao_list.save_to_db(db_connection, vistrail, do_copy)
    vistrail = translate_vistrail(vistrail, version)
    vistrail.db_currentVersion = current_action

    # update all missing tagged workflows
    tagMap = {}
    for annotation in vistrail.db_actionAnnotations:
        if annotation.db_key == '__tag__':
            tagMap[annotation.db_action_id] = annotation.db_value
    wfToSave = []
    for id, name in tagMap.iteritems():
        if id not in workflowIds:
            #print "creating workflow", vistrail.db_id, id, name,
            workflow = vistrails.db.services.vistrail.materializeWorkflow(vistrail, id)
            workflow.db_id = None
            workflow.db_vistrail_id = vistrail.db_id
            workflow.db_parent_id = id
            workflow.db_group = id
            workflow.db_last_modified=vistrail.db_get_action_by_id(id).db_date
            workflow.db_name = name
            workflow = translate_workflow(workflow, currentVersion, version)
            wfToSave.append(workflow)
            #print "done"
    if wfToSave:
        dao_list.save_many_to_db(db_connection, wfToSave, True)
    db_connection.commit()
    return vistrail

##############################################################################
# Workflow I/O

def open_workflow_from_xml(filename):
    """open_workflow_from_xml(filename) -> DBWorkflow"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    workflow = daoList.open_from_xml(filename, DBWorkflow.vtType, tree)
    if workflow is None:
        raise VistrailsDBException("Couldn't read workflow from XML")
    workflow = translate_workflow(workflow, version)
    vistrails.db.services.workflow.update_id_scope(workflow)
    return workflow

def open_workflow_from_db(db_connection, id, lock=False, version=None):
    """open_workflow_from_db(db_connection, id : long: lock: bool, 
                             version: str) 
         -> DBWorkflow 
    
    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_object_version(db_connection, id, DBWorkflow.vtType)
    dao_list = getVersionDAO(version)
    workflow = \
        dao_list.open_from_db(db_connection, DBWorkflow.vtType, id, lock)
    workflow = translate_workflow(workflow, version)
    return workflow
    
def save_workflow_to_xml(workflow, filename, version=None):
    tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.vistrails.org/workflow.xsd'
            }
    if version is None:
        version = currentVersion
    if not workflow.db_version:
        workflow.db_version = currentVersion
    workflow = translate_workflow(workflow, workflow.db_version, version)

    daoList = getVersionDAO(version)
    daoList.save_to_xml(workflow, filename, tags, version)
    workflow = translate_workflow(workflow, version)
    return workflow

def save_workflow_bundle_to_xml(save_bundle, filename, version=None):
    if save_bundle.workflow is None:
        raise VistrailsDBException('save_workflow_bundle_to_xml failed, '
                                   'bundle does not contain a workflow')
    workflow = save_workflow_to_xml(save_bundle.workflow, filename, version)
    return SaveBundle(DBWorkflow.vtType, workflow=workflow)

def save_workflow_to_db(workflow, db_connection, do_copy=False, version=None):
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_version(db_connection)
        if version is None:
            version = currentVersion
    if not workflow.db_version:
        workflow.db_version = currentVersion
    workflow = translate_workflow(workflow, workflow.db_version, version)
    dao_list = getVersionDAO(version)

    db_connection.begin()
    workflow.db_last_modified = get_current_time(db_connection)
    dao_list.save_to_db(db_connection, workflow, do_copy)
    db_connection.commit()
    workflow = translate_workflow(workflow, version)
    return workflow

def save_workflow_bundle_to_db(save_bundle, db_connection, do_copy=False, 
                               version=None):
    if save_bundle.workflow is None:
        raise VistrailsDBException('save_workflow_bundle_to_db failed, '
                                   'bundle does not contain a workflow')
    workflow = save_workflow_to_db(save_bundle.workflow, db_connection, do_copy, 
                                   version)
    return SaveBundle(DBWorkflow.vtType, workflow=workflow)

def get_saved_workflows(vistrail, db_connection):
    """ Returns list of action id:s representing populated workflows """
    if not vistrail.db_id:
        return []
    c = db_connection.cursor()
    c.execute("SELECT parent_id FROM workflow WHERE vistrail_id=%s;", (vistrail.db_id,))
    ids = [i[0] for i in c.fetchall()]
    c.close()
    return ids

##############################################################################
# Logging I/O

def open_log_from_xml(filename, was_appended=False):
    """open_log_from_xml(filename) -> DBLog"""
    if was_appended:
        parser = ElementTree.XMLTreeBuilder()
        parser.feed("<log>\n")
        f = open(filename, "rb")
        parser.feed(f.read())
        parser.feed("</log>\n")
        root = parser.close()
        workflow_execs = []
        for node in root:
            version = get_version_for_xml(node)
            daoList = getVersionDAO(version)
            workflow_exec = \
                daoList.read_xml_object(DBWorkflowExec.vtType, node)
            if version != currentVersion:
                # if version is wrong, dump this into a dummy log object, 
                # then translate, then get workflow_exec back
                log = DBLog()
                translate_log(log, currentVersion, version)
                log.db_add_workflow_exec(workflow_exec)
                log = translate_log(log, version)
                workflow_exec = log.db_workflow_execs[0]
            workflow_execs.append(workflow_exec)
        log = DBLog(workflow_execs=workflow_execs)
        vistrails.db.services.log.update_ids(log)
    else:
        tree = ElementTree.parse(filename)
        version = get_version_for_xml(tree.getroot())
        daoList = getVersionDAO(version)
        log = daoList.open_from_xml(filename, DBLog.vtType, tree)
        log = translate_log(log, version)
        vistrails.db.services.log.update_id_scope(log)
    return log

def open_log_from_db(db_connection, id, lock=False, version=None):
    """open_log_from_db(db_connection, id : long: lock: bool, version: str) 
         -> DBLog 
    
    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_object_version(db_connection, id, DBLog.vtType)
    dao_list = getVersionDAO(version)
    log = dao_list.open_from_db(db_connection, DBLog.vtType, id, lock)
    log = translate_log(log, version)
    return log

def open_vt_log_from_db(db_connection, vt_id, version=None):
    """ return the logs for the specified vistrail """
    if version is None:
        version = get_db_object_version(db_connection, vt_id, DBVistrail.vtType)
    dao_list = getVersionDAO(version)
    ids = []
    if db_connection is not None:
        try:
            c = db_connection.cursor()
            # FIXME MySQL versus sqlite3
            res = c.execute("SELECT id FROM log_tbl WHERE vistrail_id=%s;", (vt_id,))
            ids = [i[0] for i in c.fetchall()]
            c.close()
        except get_db_lib().Error, e:
            debug.critical("Error getting log id:s %d: %s" % (e.args[0], e.args[1]))
    log = DBLog()
    if hasattr(dao_list, 'open_many_from_db'): # does not exist pre 1.0.2
        logs = dao_list.open_many_from_db(db_connection, DBLog.vtType, ids)
    else:
        logs = [dao_list.open_from_db(db_connection, DBLog.vtType, id) \
                for id in ids]
    for new_log in logs:
        for workflow_exec in new_log.db_workflow_execs:
            workflow_exec.db_id = log.id_scope.getNewId(DBWorkflowExec.vtType)
            log.db_add_workflow_exec(workflow_exec)
    log = translate_log(log, version)
    return log

def save_log_to_xml(log, filename, version=None, do_append=False):
    if version is None:
        version = currentVersion
    if not log.db_version:
        log.db_version = currentVersion
    log = translate_log(log, log.db_version, version)

    daoList = getVersionDAO(version)
    if do_append:
        log_file = open(filename, 'ab')
        for workflow_exec in log.db_workflow_execs:
            # cannot do correct numbering here...
            # but need to save so that we can use it for deletes
            wf_exec_id = workflow_exec.db_id
            workflow_exec.db_id = -1L
            daoList.save_to_xml(workflow_exec, log_file, {}, version)
            workflow_exec.db_id = wf_exec_id
        log_file.close()
    else:
        tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xsi:schemaLocation': 'http://www.vistrails.org/log.xsd'
                }
        daoList.save_to_xml(log, filename, tags, version)
    log = translate_log(log, version)
    return log

def save_log_bundle_to_xml(save_bundle, filename, version=None):
    if save_bundle.log is None:
        raise VistrailsDBException('save_log_bundle_to_xml failed, '
                                   'bundle does not contain a log')
        
    log = save_log_to_xml(save_bundle.log, filename, version)
    return SaveBundle(DBLog.vtType, log=log)

def save_log_to_db(log, db_connection, do_copy=False, version=None):
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_version(db_connection)
        if version is None:
            version = currentVersion
    if not log.db_version:
        log.db_version = currentVersion
    log = translate_log(log, log.db_version, version)
    dao_list = getVersionDAO(version)

    db_connection.begin()
    log.db_last_modified = get_current_time(db_connection)
    dao_list.save_to_db(db_connection, log, do_copy)
    db_connection.commit()
    log = translate_log(log, version)
    return log

def save_log_bundle_to_db(save_bundle, db_connection, do_copy=False, 
                          version=None):
    if save_bundle.log is None:
        raise VistrailsDBException('save_log_bundle_to_db failed, '
                                   'bundle does not contain a log')
        
    log = save_log_to_db(save_bundle.log, db_connection, do_copy, version)
    return SaveBundle(DBLog.vtType, log=log)

def merge_logs(new_log, vt_log_fname):
    log = open_log_from_xml(vt_log_fname, True)
    for workflow_exec in new_log.db_workflow_execs:
        workflow_exec.db_id = log.id_scope.getNewId(DBWorkflowExec.vtType)
        log.db_add_workflow_exec(workflow_exec)
    return log

##############################################################################
# OPM I/O

def save_opm_to_xml(opm_graph, filename, version=None):    
    # FIXME, we're using workflow, version, and log here...
    # which aren't in DBOpmGraph...
    if version is None:
        version = currentVersion
    daoList = getVersionDAO(version)
    tags = {'xmlns': 'http://openprovenance.org/model/v1.01.a',
            }
    opm_graph = vistrails.db.services.opm.create_opm(opm_graph.workflow, 
                                           opm_graph.version,
                                           opm_graph.log,
                                           opm_graph.registry)
    daoList.save_to_xml(opm_graph, filename, tags, version)
    return opm_graph

##############################################################################
# PROV I/O

def save_prov_to_xml(prov_document, filename, version=None):    
    # FIXME, we're using workflow, version, and log here...
    # which aren't in DBProvDocument...
    if version is None:
        version = currentVersion
    daoList = getVersionDAO(version)
    tags = {'xmlns:prov': 'http://www.w3.org/ns/prov#',
            'xmlns:dcterms': 'http://purl.org/dc/terms/',
            'xmlns:vt': 'http://www.vistrails.org/registry.xsd',
            }
    prov_document = vistrails.db.services.prov.create_prov(prov_document.workflow, 
                                                 prov_document.version,
                                                 prov_document.log)
    daoList.save_to_xml(prov_document, filename, tags, version)
    return prov_document

##############################################################################
# Registry I/O

def open_registry_from_xml(filename):
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    registry = daoList.open_from_xml(filename, DBRegistry.vtType, tree)
    if registry is None:
        raise VistrailsDBException("Couldn't read registry from XML")
    registry = translate_registry(registry, version)
    vistrails.db.services.registry.update_id_scope(registry)
    return registry

def open_registry_from_db(db_connection, id, lock=False, version=None):
    """open_registry_from_db(db_connection, id : long: lock: bool, 
                             version: str) -> DBRegistry 
    
    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_object_version(db_connection, id, DBRegistry.vtType)
    dao_list = getVersionDAO(version)
    registry = dao_list.open_from_db(db_connection, DBRegistry.vtType, id, lock)
    registry = translate_registry(registry, version)
    return registry

def save_registry_to_xml(registry, filename, version=None):
    tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.vistrails.org/registry.xsd'
            }
    if version is None:
        version = currentVersion
    if not registry.db_version:
        registry.db_version = currentVersion
    registry = translate_registry(registry, registry.db_version, version)

    daoList = getVersionDAO(version)
    daoList.save_to_xml(registry, filename, tags, version)
    registry = translate_registry(registry, version)
    return registry

def save_registry_bundle_to_xml(save_bundle, filename, version=None):
    if save_bundle.registry is None:
        raise VistrailsDBException('save_registry_bundle_to_xml failed, '
                                   'bundle does not contain a registry')
        
    registry = save_registry_to_xml(save_bundle.registry, filename, version)
    return SaveBundle(DBRegistry.vtType, registry=registry)

def save_registry_to_db(registry, db_connection, do_copy=False, version=None):
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if version is None:
        version = get_db_version(db_connection)
        if version is None:
            version = currentVersion
    if not registry.db_version:
        registry.db_version = currentVersion
    registry = translate_registry(registry, registry.db_version, version)
    dao_list = getVersionDAO(version)

    db_connection.begin()
    registry.db_last_modified = get_current_time(db_connection)
    dao_list.save_to_db(db_connection, registry, do_copy)
    db_connection.commit()
    registry = translate_registry(registry, version)
    return registry

def save_registry_bundle_to_db(save_bundle, db_connection, do_copy=False, 
                               version=None):
    if save_bundle.registry is None:
        raise VistrailsDBException('save_registry_bundle_to_db failed, '
                                   'bundle does not contain a registry')
        
    registry = save_registry_to_db(save_bundle.registry, db_connection, do_copy, 
                                   version)
    return SaveBundle(DBRegistry.vtType, registry=registry)

##############################################################################
# Abstraction I/O

def open_abstraction_from_db(db_connection, id, lock=False):
    """open_abstraction_from_db(db_connection, id : long: lock: bool) 
         -> DBAbstraction 
    DEPRECATED
    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    abstraction = read_sql_objects(db_connection, DBAbstraction.vtType, 
                                   id, lock)[0]

    # not sure where this really should be done...
    # problem is that db reads the add ops, then change ops, then delete ops
    # need them ordered by their id
    for db_action in abstraction.db_get_actions():
        db_action.db_operations.sort(key=lambda x: x.db_id)
    vistrails.db.services.abstraction.update_id_scope(abstraction)
    return abstraction

def save_abstraction_to_db(abstraction, db_connection, do_copy=False):
    """ DEPRECATED """
    db_connection.begin()
    if abstraction.db_last_modified is None:
        do_copy = True
    if not do_copy:
        match_id = get_matching_abstraction_id(db_connection, abstraction)
        # FIXME remove print
        #print 'match_id:', match_id
        if match_id is not None:
            abstraction.db_id = match_id
            abstraction.is_new = False
        else:
            do_copy = True
        new_time = get_db_object_modification_time(db_connection, 
                                                   abstraction.db_id,
                                                   DBAbstraction.vtType)
        if new_time > abstraction.db_last_modified:
            # need synchronization
            # FIXME remove print
            #print '*** doing synchronization ***'
            old_abstraction = open_abstraction_from_db(db_connection, 
                                                       abstraction.db_id,
                                                       True)
            # the "old" one is modified and changes integrated
            vistrails.db.services.vistrail.synchronize(old_abstraction, abstraction,
                                             0L)
            abstraction = old_abstraction
    if do_copy:
        abstraction.db_id = None
    abstraction.db_last_modified = get_current_time(db_connection)
    write_sql_objects(db_connection, [abstraction], do_copy)
    db_connection.commit()
    return abstraction

def save_abstractions_to_db(abstractions, vt_id, db_connection, do_copy=False):
    """save_abstraction_to_db(abs: DBVistrail, db_connection) -> None
    Saves an abstraction to db, and updating existing abstractions

    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)

    for abs_name in abstractions:
        try: 
            abs = open_vistrail_from_xml(abs_name)
            abs.db_name = parse_abstraction_name(abs_name)
            id_key = '__abstraction_vistrail_id__'
            id_value = str(vt_id)
            if abs.db_has_annotation_with_key(id_key):
                annotation = abs.db_get_annotation_by_key(id_key)
                annotation.db_value = id_value
            else:
                annotation=DBAnnotation(abs.idScope.getNewId(DBAnnotation.vtType),
                                        id_key, id_value)
                abs.db_add_annotation(annotation)
            db_mod_time = None if not abs.db_id else \
                          get_db_abstraction_modification_time(db_connection, abs)

            if db_mod_time:
                delete_entity_from_db(db_connection, abs.vtType, abs.db_id)

            abs.db_id = None
            abs.db_last_modified = get_current_time(db_connection)
            version = get_db_version(db_connection)
            version = version if version else currentVersion
            if not abs.db_version:
                abs.db_version = currentVersion
            abs = translate_vistrail(abs, abs.db_version, version)
            # Always copy for now
            getVersionDAO(version).save_to_db(db_connection, abs, True)
            db_connection.commit()

        except Exception, e:
            debug.critical('Could not save abstraction to db: %s' % str(e))

##############################################################################
# Thumbnail I/O

def open_thumbnails_from_db(db_connection, obj_type, obj_id, tmp_dir=None):
    """open_thumbnails_from_db(db_connection, obj_type: DB*,
                            obj_id: long, tmp_dir: str) -> [str]

    Gets a list of all thumbnails associated with this object from the
    annotations table in the db (by comparing obj_type with the column
    'entity_type' and obj_id with the column 'entity_id') and for any
    thumbnails not found in tmp_dir, they are retreived from the db and
    saved into tmp_dir.
    Returns a list of absolute file paths for all thumbnails associated
    with this object that exist in tmp_dir after the function has run.

    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if tmp_dir is None:
        return []

    # First get associated file names from annotation table
    prepared_statement = format_prepared_statement(
    """
    SELECT a.value
    FROM action_annotation a
    WHERE a.akey = '__thumb__' AND a.entity_id = ? AND a.entity_type = ?
    """)
    try:
        c = db_connection.cursor()
        c.execute(prepared_statement, (obj_id, obj_type))
        file_names = [file_name for (file_name,) in c.fetchall()]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get thumbnails list from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    # Next get all thumbnails from the db that aren't already in tmp_dir
    get_db_file_names = [fname for fname in file_names if fname not in os.listdir(tmp_dir)]
    for file_name in get_db_file_names:
        prepared_statement = format_prepared_statement(
        """
        SELECT t.image_bytes
        FROM thumbnail t
        WHERE t.file_name = ?
        """)
        try:
            c = db_connection.cursor()
            c.execute(prepared_statement, (file_name,))
            row = c.fetchone()
            c.close()
        except get_db_lib().Error, e:
            msg = "Couldn't get thumbnail from db (%d : %s)" % \
                (e.args[0], e.args[1])
            raise VistrailsDBException(msg)
        if row is not None:
            image_bytes = row[0]
            try:
                absfname = os.path.join(tmp_dir, file_name)
                image_file = open(absfname, 'wb')
                image_file.write(image_bytes)
                image_file.close()
            except IOError, e:
                msg = "Couldn't write thumbnail file to disk: %s" % absfname
                raise VistrailsDBException(msg)
        else:
            debug.warning("db: Referenced thumbnail not found locally or in the database: '%s'" % file_name)
    # Return only thumbnails that now exist locally
    return [os.path.join(tmp_dir, file_name) for file_name in file_names if file_name in os.listdir(tmp_dir)]

def save_thumbnails_to_db(absfnames, db_connection):
    """save_thumbnails_to_db(absfnames: list, db_connection) -> None
    Saves all thumbnails from a list of local absolute file paths into the db,
    except those already present on the db.

    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    if absfnames is None or len(absfnames) == 0:
        return None

    # Determine which thumbnails already exist in db
    statement = """
    SELECT t.file_name
    FROM thumbnail t
    WHERE t.file_name IN %s
    """
    check_file_names = [os.path.basename(absfname).replace("'", "''").replace("\\", "\\\\") for absfname in absfnames]
    # SQL syntax needs SOMETHING if list is empty - use filename that's illegal on all platforms
    check_file_names.append(':/')
    sql_in_token = str(tuple(check_file_names))
    try:
        c = db_connection.cursor()
        c.execute(statement % sql_in_token)
        db_file_names = [file_name for (file_name,) in c.fetchall()]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't check which thumbnails already exist in db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    insert_absfnames = [absfname for absfname in absfnames if os.path.basename(absfname) not in db_file_names]

    # Save any thumbnails that don't already exist in db
    prepared_statement = format_prepared_statement(
    """
    INSERT INTO thumbnail(file_name, image_bytes, last_modified)
    VALUES (?, ?, ?)
    """)
    try:
        c = db_connection.cursor()
        for absfname in insert_absfnames:
            image_file = open(absfname, 'rb')
            image_bytes = image_file.read()
            image_file.close()
            c.execute(prepared_statement, (os.path.basename(absfname), image_bytes, strftime(get_current_time(db_connection), '%Y-%m-%d %H:%M:%S')))
            db_connection.commit()
        c.close()
    except IOError, e:
        msg = "Couldn't read thumbnail file for writing to db: %s" % absfname
        raise VistrailsDBException(msg)
    except get_db_lib().Error, e:
        msg = "Couldn't insert thumbnail into db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return None
##############################################################################
# Mashup I/O
def open_mashuptrail_from_xml(filename):
    """open_mashuptrail_from_xml(filename) -> Mashuptrail"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    # this is here because initially the version in the mashuptrail file was 
    # independent of VisTrails schema version. So if the version was "0.1.0" we
    # can safely upgrade it directly to 1.0.3 as it was the first version when
    # the mashuptrail started to use the same vistrails schema version
    old_version = version
    if version == "0.1.0":
        version = "1.0.3"
    try:
        daoList = getVersionDAO(version)
        mashuptrail = daoList.open_from_xml(filename, DBMashuptrail.vtType, tree)
        if old_version == "0.1.0":
            mashuptrail.db_version = version
        Mashuptrail.convert(mashuptrail)
        mashuptrail.currentVersion = mashuptrail.getLatestVersion()
        mashuptrail.updateIdScope()
    except VistrailsDBException, e:
        msg = "There was a problem when reading mashups from the xml file: "
        msg += str(e)
        raise VistrailsDBException(msg)
    return mashuptrail

def save_mashuptrail_to_xml(mashuptrail, filename, version=None):
    tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.vistrails.org/mashup.xsd'
            }
    if version is None:
        version = currentVersion
    
    if not mashuptrail.db_version:
        mashuptrail.db_version = version
   
    #FIXME: This must be enabled at some point
    #mashuptrail = translate_mashuptrail(mashuptrail, mashuptrail.db_version, version)
    daoList = getVersionDAO(version)
    daoList.save_to_xml(mashuptrail, filename, tags, version)
    return mashuptrail

def open_mashuptrail_from_db(db_connection, mashup_id, lock=False):
    """open_mashuptrail_from_db(filename) -> Mashuptrail"""

    version = get_db_object_version(db_connection, mashup_id, DBMashuptrail.vtType)
    try:
        daoList = getVersionDAO(version)
        mashuptrail = daoList.open_from_db(db_connection, DBMashuptrail.vtType, mashup_id, lock)
        Mashuptrail.convert(mashuptrail)
        mashuptrail.currentVersion = mashuptrail.getLatestVersion()
        mashuptrail.updateIdScope()
    except VistrailsDBException, e:
        msg = "There was a problem when reading mashups from the db file: "
        msg += str(e)
        raise VistrailsDBException(msg)
    return mashuptrail

def save_mashuptrails_to_db(mashuptrails, vt_id, db_connection, do_copy=False):
    """save_mashuptrails_to_db(mashuptrails: DBMashuptrail, vt_id: int,
                               db_connection, do_copy: bool) -> None
    Saves a list of mashuptrails to the db, and replacing existing mashuptrails

    """
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)

    # for now we replace all mashups
    for old_id in get_db_mashuptrail_ids_from_vistrail(db_connection, vt_id):
        delete_entity_from_db(db_connection, Mashuptrail.vtType, old_id)

    for mashuptrail in mashuptrails:
        try: 
            id_key = '__mashuptrail_vistrail_id__'
            id_value = str(vt_id)
            if mashuptrail.db_has_annotation_with_key(id_key):
                annotation = mashuptrail.db_get_annotation_by_key(id_key)
                annotation.db_value = id_value
            else:
                annotation=DBAnnotation(mashuptrail.id_scope.getNewId(DBAnnotation.vtType),
                                        id_key, id_value)
                mashuptrail.db_add_annotation(annotation)

            # add vt_id to mashups
            for action in mashuptrail.db_actions:
                action.db_mashup.db_vtid = vt_id
            mashuptrail.db_last_modified = get_current_time(db_connection)
            mashuptrail.db_id = None
            version = get_db_version(db_connection)
            version = version if version else currentVersion
            if not mashuptrail.db_version:
                mashuptrail.db_version = currentVersion
            #FIXME: This must be enabled at some point
            #mashuptrail = translate_vistrail(mashuptrail, mashuptrail.db_version, version)
            # Always copy for now
            getVersionDAO(version).save_to_db(db_connection, mashuptrail, True)
            db_connection.commit()

        except Exception, e:
            debug.critical('Could not save mashuptrail to db: %s' % str(e))

def open_startup_from_xml(filename):
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    if version == '0.1':
        version = '1.0.3'
    daoList = getVersionDAO(version)
    startup = daoList.open_from_xml(filename, DBStartup.vtType, tree)
    # need this for translation...
    startup._filename = filename
    startup = translate_startup(startup, version)
    # vistrails.db.services.startup.update_id_scope(startup)
    return startup

def save_startup_to_xml(startup, filename, version=None):
    tags = {}
    if version is None:
        version = currentVersion
    if not startup.db_version:
        startup.db_version = currentVersion
    # FIXME add translation, etc.
    # startup = translate_startup(startup, startup.db_version, version)

    daoList = getVersionDAO(version)
    daoList.save_to_xml(startup, filename, tags, version)
    # startup = translate_startup(startup, version)
    return startup
    

##############################################################################
# I/O Utilities

def delete_entity_from_db(db_connection, type, obj_id):
    if db_connection is None:
        msg = "Need to call open_db_connection() before reading"
        raise VistrailsDBException(msg)
    version = get_db_version(db_connection)
    if version is None:
        version = currentVersion
    dao_list = getVersionDAO(version)
    dao_list.delete_from_db(db_connection, type, obj_id)
    db_connection.commit()
    
def get_version_for_xml(root):
    version = root.get('version', None)
    if version is not None:
        return version
    msg = "Cannot find version information"
    raise VistrailsDBException(msg)

def get_type_for_xml(root):
    return root.tag

def get_current_time(db_connection=None):
    timestamp = datetime.now()
    if db_connection is not None:
        try:
            c = db_connection.cursor()
            # FIXME MySQL versus sqlite3
            c.execute("SELECT NOW();")
            # c.execute("SELECT DATETIME('NOW');")
            row = c.fetchone()
            if row:
                # FIXME MySQL versus sqlite3
                timestamp = row[0]
                # timestamp = strptime(row[0], '%Y-%m-%d %H:%M:%S')
            c.close()
        except get_db_lib().Error, e:
            debug.critical("Logger Error %d: %s" % (e.args[0], e.args[1]))

    return timestamp

def create_temp_folder(prefix='vt_save'):
    return tempfile.mkdtemp(prefix=prefix)

def remove_temp_folder(temp_dir):
    if temp_dir is None:
        return
    if not os.path.isdir(temp_dir):
        if os.path.isfile(temp_dir):
            os.remove(temp_dir)

        # cleanup has already happened
        return
    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
    except OSError, e:
        raise VistrailsDBException("Can't remove %s: %s" % (temp_dir, str(e)))
    
##############################################################################
# Testing


class TestDBIO(unittest.TestCase):
    def test1(self):
        """test importing an xml file"""

        vistrail = open_vistrail_from_xml( \
            os.path.join(vistrails.core.system.vistrails_root_directory(),
                         'tests/resources/dummy.xml'))
        assert vistrail is not None
        
    def test2(self):
        """test importing an xml file"""

        vistrail = open_vistrail_from_xml( \
            os.path.join(vistrails.core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.xml'))
        assert vistrail is not None

    def test3(self):
        """test importing a vt file"""

        # FIXME include abstractions
        (save_bundle, vt_save_dir) = open_bundle_from_zip_xml( \
            DBVistrail.vtType,
            os.path.join(vistrails.core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.vt'))
        assert save_bundle.vistrail is not None

    def test4(self):
        """ test saving a vt file """

        # FIXME include abstractions
        testdir = tempfile.mkdtemp(prefix='vt_')
        filename = os.path.join(testdir, 'dummy_new.vt')

        try:
            (save_bundle, vt_save_dir) = open_bundle_from_zip_xml(
                DBVistrail.vtType,
                os.path.join(vistrails.core.system.vistrails_root_directory(),
                             'tests/resources/dummy_new.vt'))
            try:
                save_bundle_to_zip_xml(save_bundle, filename, vt_save_dir)
                if os.path.isfile(filename):
                    os.unlink(filename)
            except Exception, e:
                self.fail(str(e))
        finally:
            os.rmdir(testdir)
