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
from core.system import get_elementtree_library, temporary_directory,\
     execute_cmdline
import core.requirements
ElementTree = get_elementtree_library()

import sys
import os
import os.path
import shutil
import tempfile

from db import VistrailsDBException
from db.domain import DBVistrail, DBWorkflow, DBLog, DBAbstraction, DBGroup, \
    DBRegistry
import db.services.abstraction
import db.services.log
import db.services.registry
import db.services.workflow
import db.services.vistrail
from db.versions import getVersionDAO, currentVersion, getVersionSchemaDir, \
    translate_object, translate_vistrail, translate_workflow, translate_log, \
    translate_registry

def open_db_connection(config):
    import MySQLdb

    if config is None:
        msg = "You need to provide valid config dictionary"
        raise VistrailsDBException(msg)
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
        db_connection = MySQLdb.connect(**config)
        close_db_connection(db_connection)
    except MySQLdb.Error, e:
        msg = "connection test failed (%d: %s)" % (e.args[0], e.args[1])
        raise VistrailsDBException(msg)

def translate_to_tbl_name(obj_type):
    map = {DBVistrail.vtType: 'vistrail',
           DBWorkflow.vtType: 'workflow',
           DBLog.vtType: 'log_tbl',
           DBAbstraction.vtType: 'abstraction',
           }
    return map[obj_type]

def date_to_str(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

def get_db_object_list(config, obj_type):
    
    import MySQLdb

    result = []    
    db = open_db_connection(config)

    #FIXME Create a DBGetVistrailListSQLDAOBase for this
    # and maybe there's another way to build this query
    command = """SELECT o.id, o.name, o.last_modified
    FROM %s o
    ORDER BY o.name
    """
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
        
    except MySQLdb.Error, e:
        msg = "Couldn't get list of vistrails objects from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return result

def get_db_object_modification_time(db_connection, obj_id, obj_type):
    import MySQLdb

    command = """
    SELECT o.last_modified
    FROM %s o
    WHERE o.id = %s
    """

    try:
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(obj_type), obj_id))
        time = c.fetchall()[0][0]
        c.close()
    except MySQLdb.Error, e:
        msg = "Couldn't get object modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return time

def get_db_object_version(db_connection, obj_id, obj_type):
    import MySQLdb

    command = """
    SELECT o.version
    FROM %s o
    WHERE o.id = %s
    """

    try:
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(obj_type), obj_id))
        version = c.fetchall()[0][0]
        c.close()
    except MySQLdb.Error, e:
        msg = "Couldn't get object version from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return version

def get_db_version(db_connection):
    import MySQLdb

    command = """
    SELECT `version`
    FROM `vistrails_version`
    """

    try:
        c = db_connection.cursor()
        c.execute(command)
        version = c.fetchall()[0][0]
        c.close()
    except MySQLdb.Error, e:
        # just return None if we hit an error
        return None
    return version

def get_matching_abstraction_id(db_connection, abstraction):
    import MySQLdb

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
            print 'got result:', result
            id = result[0][0]
    except MySQLdb.Error, e:
        msg = "Couldn't get object modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return id

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

def save_to_xml(obj, filename):
    if obj.vtType == DBVistrail.vtType:
        return save_vistrail_to_xml(obj, filename)
    elif obj.vtType == DBWorkflow.vtType:
        return save_workflow_to_xml(obj, filename)
    elif obj.vtType == DBLog.vtType:
        return save_log_to_xml(obj, filename)
    elif obj.vtType == DBRegistry.vtType:
        return save_registry_to_xml(obj, filename)
    else:
        raise VistrailsDBException("cannot save object of type "
                                   "'%s' to xml" % type)

def append_to_xml(obj, filename):
    if obj.vtType == DBLog.vtType:
        return append_log_to_xml(obj, filename)
    else:
        raise VistrailsDBException("cannot append object of type '%s'" % \
                                       obj.vtType)

def open_from_zip_xml(filename, type):
    if type == DBVistrail.vtType:
        return open_vistrail_from_zip_xml(filename)
    else:
        raise VistrailsDBException("cannot open object of type '%s' from zip" %\
                                       type)

def save_to_zip_xml(objs, filename, tmp_dir=None):
    obj_type = objs[0][0]
    if obj_type == DBVistrail.vtType:
        return save_vistrail_to_zip_xml(objs, filename, tmp_dir)
    else:
        raise VistrailsDBException("cannot save object of type '%s' to zip" % \
                                       obj_type)

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
        vistrail = daoList.open_from_xml(filename, DBVistrail.vtType)
        vistrail = translate_vistrail(vistrail, version)
        db.services.vistrail.update_id_scope(vistrail)
    except VistrailsDBException, e:
        msg = "This vistrail was created by a newer version of VisTrails "
        msg += "and cannot be opened."
        raise VistrailsDBException(msg)
    return vistrail

def open_vistrail_from_zip_xml(filename):
    """open_vistrail_from_zip_xml(filename) -> Vistrail
    Open a vistrail from a zip compressed format.
    It expects that the file inside archive has name vistrail

    """

    core.requirements.require_executable('unzip')

    vt_save_dir = tempfile.mkdtemp(prefix='vt_save')
    output = []
    cmdline = ['unzip', '-q','-o','-d', vt_save_dir, filename]
    result = execute_cmdline(cmdline, output)
    
    if result != 0 and len(output) != 0:
        raise VistrailsDBException("Unzip of '%s' failed" % filename)

    vistrail = None
    log = None
    abstraction_files = []
    unknown_files = []
    try:
        for root, dirs, files in os.walk(vt_save_dir):
            for fname in files:
                if fname == 'vistrail' and root == vt_save_dir:
                    vistrail = open_vistrail_from_xml(os.path.join(root, fname))
                elif fname == 'log' and root == vt_save_dir:
                    # FIXME read log to get execution info
                    # right now, just ignore the file
                    log = None 
                    # log = open_log_from_xml(os.path.join(root, fname))
                    # objs.append(DBLog.vtType, log)
                elif fname.startswith('abstraction_'):
                    abstraction_file = os.path.join(root, fname)
                    abstraction_files.append(abstraction_file)
                else:
                    unknown_files.append(os.path.join(root, fname))
    except OSError, e:
        raise VistrailsDBException("Error when reading vt file")
    if len(unknown_files) > 0:
        raise VistrailsDBException("Unknown files in vt file: %s" % \
                                       unknown_files)
    if vistrail is None:
        raise VistrailsDBException("vt file does not contain vistrail")
    
    objs = [(DBVistrail.vtType, vistrail)]
    if log is not None:
        objs.append((DBLog.vtType, log))
    for abstraction_file in abstraction_files:
        objs.append(('__file__', abstraction_file))

    return (objs, vt_save_dir)
            
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
    db.services.vistrail.update_id_scope(vistrail)
    return vistrail

def save_vistrail_to_xml(vistrail, filename, version=None):
    tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.vistrails.org/vistrail.xsd'
            }
    if version is None:
        version = currentVersion
    if not vistrail.db_version:
        vistrail.db_version = currentVersion
    vistrail = translate_vistrail(vistrail, vistrail.db_version, version)

    daoList = getVersionDAO(version)        
    daoList.save_to_xml(vistrail, filename, tags, currentVersion)
    return vistrail

def save_vistrail_to_zip_xml(objs, filename, vt_save_dir=None, version=None):
    """save_vistrail_to_zip_xml(objs: (string, object, fname), filename:str,
                                vt_save_dir: str, version: str) -> None
    string: either the object's vtType or 'file' (we are copying a file)
    object: a DB* object or filename
    fname: the filename of the object in the zip file
    filename: filename to save to
    temp_dir: directory storing any previous files

    Generate a zip compressed version of vistrail.
    It raise an Exception if there was an error
    
    """

    core.requirements.require_executable('zip')

    vistrail = objs[0]
    if vistrail[1].vtType != DBVistrail.vtType or \
            vistrail[0] != DBVistrail.vtType:
        raise VistrailsDBException('save_vistrail_to_zip_xml failed, object '
                                   'is not a vistrail')
    if not vt_save_dir:
        vt_save_dir = tempfile.mkdtemp(prefix='vt_save')
    # saving zip files flat so we'll do without this dir for now
    # abstraction_dir = os.path.join(vt_save_dir, 'abstractions')

    for (obj_type, obj) in objs:
        if obj_type == '__file__':
            if type(obj) == type(""):
                obj_fname = 'abstraction_' + os.path.basename(obj)
                # xml_fname = os.path.join(abstraction_dir, obj_fname)
                xml_fname = os.path.join(vt_save_dir, obj_fname)
                # if not os.path.exists(abstraction_dir):
                #     os.mkdir(abstraction_dir)
                # print 'copying %s -> %s' % (obj, xml_fname)
                shutil.copyfile(obj, xml_fname)
            else:
                raise VistrailsDBException('save_vistrail_to_zip_xml failed, '
                                           '__file__ must have a filename '
                                           'as obj')
        elif obj_type == DBLog.vtType:
            xml_fname = os.path.join(vt_save_dir, 'log')
            if not os.path.exists(xml_fname):
                save_log_to_xml(obj, xml_fname, version)
            else:
                append_log_to_xml(obj, xml_fname, version)
        elif obj_type == DBVistrail.vtType:
            xml_fname = os.path.join(vt_save_dir, 'vistrail')
            save_vistrail_to_xml(obj, xml_fname, version)
        else:
            raise VistrailsDBException('save_vistrail_to_zip_xml failed, '
                                       "type '%s' unrecognized" % obj_type)
        

    output = []
    cmdline = ['zip', '-r', '-j', '-q', filename, vt_save_dir]
    result = execute_cmdline(cmdline,output)
    
    #print result, output
    if result != 0 and len(output) != 0:
        for line in output:
            if line.find('deflated') == -1:
                raise VistrailsDBException(" ".join(output))
    return (objs, vt_save_dir)
            
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
    vistrail = translate_vistrail(vistrail, vistrail.db_version, version)
    dao_list = getVersionDAO(version)

    db_connection.begin()
    if not do_copy and vistrail.db_last_modified is not None:
        new_time = get_db_object_modification_time(db_connection, 
                                                   vistrail.db_id,
                                                   DBVistrail.vtType)
        if new_time > vistrail.db_last_modified:
            # need synchronization
            old_vistrail = open_vistrail_from_db(db_connection, vistrail.db_id,
                                                 True, version)
            old_vistrail = translate_vistrail(old_vistrail, version)
            # the "old" one is modified and changes integrated
            db.services.vistrail.synchronize(old_vistrail, vistrail)
            vistrail = old_vistrail
    vistrail.db_last_modified = get_current_time(db_connection)
    dao_list.save_to_db(db_connection, vistrail, do_copy)
    db_connection.commit()
    return vistrail

##############################################################################
# Workflow I/O

def open_workflow_from_xml(filename):
    """open_workflow_from_xml(filename) -> DBWorkflow"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    workflow = daoList.open_from_xml(filename, DBWorkflow.vtType)
    workflow = translate_workflow(workflow, version)
    db.services.workflow.update_id_scope(workflow)
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
    daoList.save_to_xml(workflow, filename, tags, currentVersion)
    return workflow

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
    return workflow

##############################################################################
# Logging I/O

def open_log_from_xml(filename):
    """open_log_from_xml(filename) -> DBLog"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    log = daoList.open_from_xml(filename, DBLog.vtType)
    log = translate_log(log, version)
    db.services.log.update_id_scope(log)
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

def save_log_to_xml(log, filename, version=None):
#     tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
#             'xsi:schemaLocation': 'http://www.vistrails.org/log.xsd'
#             }
#     daoList.save_to_xml(log, filename, tags, currentVersion)

    if version is None:
        version = currentVersion
    if not log.db_version:
        log.db_version = currentVersion
    log = translate_log(log, log.db_version, version)

    daoList = getVersionDAO(version)
    log_file = open(filename, 'wb')
    for workflow_exec in log.workflow_execs:
        daoList.save_to_xml(workflow_exec, log_file, {}, currentVersion)
    log_file.close()
    return log

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
    return log

def append_log_to_xml(log, filename, version=None):
    if version is None:
        version = currentVersion
    if not log.db_version:
        log.db_version = currentVersion
    log = translate_log(log, log.db_version, version)

    daoList = getVersionDAO(version)
    log_file = open(filename, 'ab')

    for workflow_exec in log.workflow_execs:
        daoList.save_to_xml(workflow_exec, log_file, {}, currentVersion)
    log_file.close()
    return log

##############################################################################
# Registry I/O

def open_registry_from_xml(filename):
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    registry = daoList.open_from_xml(filename, DBRegistry.vtType)
    registry = translate_registry(registry, version)
    db.services.registry.update_id_scope(registry)
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
    daoList.save_to_xml(registry, filename, tags, currentVersion)
    return registry

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
    return registry

##############################################################################
# Abstraction I/O

def open_abstraction_from_db(db_connection, id, lock=False):
    """open_abstraction_from_db(db_connection, id : long: lock: bool) 
         -> DBAbstraction 
    
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
    db.services.abstraction.update_id_scope(abstraction)
    return abstraction

def save_abstraction_to_db(abstraction, db_connection, do_copy=False):
    db_connection.begin()
    if abstraction.db_last_modified is None:
        do_copy = True
    if not do_copy:
        match_id = get_matching_abstraction_id(db_connection, abstraction)
        # FIXME remove print
        print 'match_id:', match_id
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
            print '*** doing synchronization ***'
            old_abstraction = open_abstraction_from_db(db_connection, 
                                                       abstraction.db_id,
                                                       True)
            # the "old" one is modified and changes integrated
            db.services.vistrail.synchronize(old_abstraction, abstraction)
            abstraction = old_abstraction
    if do_copy:
        abstraction.db_id = None
    abstraction.db_last_modified = get_current_time(db_connection)
    write_sql_objects(db_connection, [abstraction], do_copy)
    db_connection.commit()
    return abstraction

##############################################################################
# I/O Utilities

def get_version_for_xml(root):
    version = root.get('version', None)
    if version is not None:
        return version
    msg = "Cannot find version information"
    raise VistrailsDBException(msg)

def get_current_time(db_connection=None):
    timestamp = datetime.now()
    if db_connection is not None:
        try:
            c = db_connection.cursor()
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
import core.system
import os

class TestDBIO(unittest.TestCase):
    def test1(self):
        """test importing an xml file"""

        vistrail = open_vistrail_from_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy.xml'))
        assert vistrail is not None
        
    def test2(self):
        """test importing an xml file"""

        vistrail = open_vistrail_from_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.xml'))
        assert vistrail is not None

    def test3(self):
        """test importing a vt file"""

        # FIXME include abstractions
        (objs, vt_save_dir) = open_vistrail_from_zip_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.vt'))
        assert objs[0][1] is not None

    def test4(self):
        """ test saving a vt file """

        # FIXME include abstractions
        filename = os.path.join(core.system.vistrails_root_directory(),
                                'tests/resources/dummy_new_temp.vt')
    
        (objs, vt_save_dir) = open_vistrail_from_zip_xml( \
            os.path.join(core.system.vistrails_root_directory(),
                         'tests/resources/dummy_new.vt'))
        try:
            save_vistrail_to_zip_xml(objs, filename, vt_save_dir)
            if os.path.isfile(filename):
                os.unlink(filename)
        except Exception, e:
            self.fail(str(e))
        

