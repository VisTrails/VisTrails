############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
from core import debug
from core.system import get_elementtree_library, temporary_directory,\
     execute_cmdline, systemType
import core.requirements
ElementTree = get_elementtree_library()

import sys
import os
import os.path
import shutil
import tempfile

from db import VistrailsDBException
from db.domain import DBVistrail, DBWorkflow, DBLog, DBAbstraction, DBGroup, \
    DBRegistry, DBWorkflowExec, DBOpmGraph
import db.services.abstraction
import db.services.log
import db.services.opm
import db.services.registry
import db.services.workflow
import db.services.vistrail
from db.versions import getVersionDAO, currentVersion, getVersionSchemaDir, \
    translate_object, translate_vistrail, translate_workflow, translate_log, \
    translate_registry

_db_lib = None
def get_db_lib():
    global _db_lib
    if _db_lib is None:
        import MySQLdb
        # import sqlite3
        _db_lib = MySQLdb
    return _db_lib
def set_db_lib(lib):
    global _db_lib
    _db_lib = lib

def open_db_connection(config):

    if config is None:
        msg = "You need to provide valid config dictionary"
        raise VistrailsDBException(msg)
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
    try:
        db_connection = get_db_lib().connect(**config)
        close_db_connection(db_connection)
    except get_db_lib().Error, e:
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
        c = db_connection.cursor()
        c.execute(command % (translate_to_tbl_name(obj_type), obj_id))
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
            print 'got result:', result
            id = result[0][0]
    except get_db_lib().Error, e:
        msg = "Couldn't get object modification time from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return id

def setup_db_tables(db_connection, version=None):
    schemaDir = getVersionSchemaDir(version)
    try:
        def execute_file(c, f):
            cmd = ""
            auto_inc_str = 'auto_increment'
            not_null_str = 'not null'
            engine_str = 'engine=InnoDB;'
            for line in f:
                if line.find(auto_inc_str) > 0:
                    num = line.find(auto_inc_str)
                    line = line[:num] + line[num+len(auto_inc_str):]
                if line.find(not_null_str) > 0:
                    num = line.find(not_null_str)
                    line = line[:num] + line[num+len(not_null_str):]
                cmd += line
                ending = line.rstrip()
                if ending and ending[-1] == ';':
                    # FIXME engine stuff switch for MySQLdb, sqlite3
                    cmd = cmd.rstrip()
                    if cmd.endswith(engine_str):
                        cmd = cmd[:-len(engine_str)] + ';'
                    print cmd
                    c.execute(cmd)
                    cmd = ""

        # delete tables
        c = db_connection.cursor()
        f = open(os.path.join(schemaDir, 'vistrails_drop.sql'))
        execute_file(c, f)
#         db_script = f.read()
#         c.execute(db_script)
        c.close()
        f.close()

        # create tables        
        c = db_connection.cursor()
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
    else:
        raise VistrailsDBException("cannot save object of type "
                                   "'%s' to xml" % type)

def open_from_zip_xml(filename, type):
    if type == DBVistrail.vtType:
        return open_vistrail_from_zip_xml(filename)
    else:
        raise VistrailsDBException("cannot open object of type '%s' from zip" %\
                                       type)

def save_to_zip_xml(objs, filename, tmp_dir=None, version=None):
    obj_type = objs[0][0]
    if obj_type == DBVistrail.vtType:
        return save_vistrail_to_zip_xml(objs, filename, tmp_dir, version)
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
        vistrail = daoList.open_from_xml(filename, DBVistrail.vtType, tree)
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
    log_fname = None
    abstraction_files = []
    unknown_files = []
    thumbnail_files = []
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
                else:
                    unknown_files.append(os.path.join(root, fname))
    except OSError, e:
        raise VistrailsDBException("Error when reading vt file")
    if len(unknown_files) > 0:
        raise VistrailsDBException("Unknown files in vt file: %s" % \
                                       unknown_files)
    if vistrail is None:
        raise VistrailsDBException("vt file does not contain vistrail")
    vistrail.db_log_filename = log_fname

    objs = [(DBVistrail.vtType, vistrail)]
    if log is not None:
        objs.append((DBLog.vtType, log))
    for abstraction_file in abstraction_files:
        objs.append(('__file__', abstraction_file))
    for thumbnail_file in thumbnail_files:
        objs.append(('__thumb__', thumbnail_file))
        
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
    thumbnail_dir = os.path.join(vt_save_dir, 'thumbs')
    
    for (obj_type, obj) in objs:
        if obj_type == '__file__':
            if type(obj) == type(""):
                # FIXME we should have an abstraction directory here instead
                # of the abstraction_ prefix...
                if not os.path.basename(obj).startswith('abstraction_'):
                    obj_fname = 'abstraction_' + os.path.basename(obj)
                else:
                    obj_fname = os.path.basename(obj)
                # xml_fname = os.path.join(abstraction_dir, obj_fname)
                xml_fname = os.path.join(vt_save_dir, obj_fname)
                # if not os.path.exists(abstraction_dir):
                #     os.mkdir(abstraction_dir)
                # print "obj:", obj
                # print "xml_fname:", xml_fname
                if obj != xml_fname:
                    # print 'copying %s -> %s' % (obj, xml_fname)
                    try:
                        shutil.copyfile(obj, xml_fname)
                    except Exception, e:
                        debug.critical('copying %s -> %s failed: %s' % \
                                           (obj, xml_fname, str(e)))
            else:
                raise VistrailsDBException('save_vistrail_to_zip_xml failed, '
                                           '__file__ must have a filename '
                                           'as obj')
        elif obj_type == '__thumb__':
            if type(obj) == type(""):
                obj_fname = os.path.basename(obj)
                png_fname = os.path.join(thumbnail_dir, obj_fname)
                if not os.path.exists(thumbnail_dir):
                    os.mkdir(thumbnail_dir)
                if not os.path.exists(png_fname):
                    #print 'copying %s -> %s' %(obj, png_fname)
                    try:
                        shutil.copyfile(obj, png_fname)
                    except Exception, e:
                        debug.critical('copying %s -> %s failed: %s' % \
                                           (obj, png_fname, str(e))) 
            else:
                raise VistrailsDBException('save_vistrail_to_zip_xml failed, '
                                           '__thumb__ must have a filename '
                                           'as obj')
        elif obj_type == DBLog.vtType:
            xml_fname = os.path.join(vt_save_dir, 'log')
            save_log_to_xml(obj, xml_fname, version, True)
        elif obj_type == DBVistrail.vtType:
            xml_fname = os.path.join(vt_save_dir, 'vistrail')
            save_vistrail_to_xml(obj, xml_fname, version)
        else:
            raise VistrailsDBException('save_vistrail_to_zip_xml failed, '
                                       "type '%s' unrecognized" % obj_type)
        

    tmp_zip_dir = tempfile.mkdtemp(prefix='vt_zip')
    tmp_zip_file = os.path.join(tmp_zip_dir, "vt.zip")
    output = []
    rel_vt_save_dir = os.path.split(vt_save_dir)[1]
    cur_dir = os.getcwd()
    # on windows, we assume zip.exe is in the current directory when
    # running from the binary install
    zipcmd = 'zip'
    if systemType in ['Windows', 'Microsoft']:
        zipcmd = os.path.join(cur_dir,'zip')
        if not os.path.exists(zipcmd):
            zipcmd = 'zip' #assume zip is in path
    cmdline = [zipcmd, '-r', '-q', tmp_zip_file, '.']
    try:
        #if we want that directories are also stored in the zip file
        # we need to run from the vt directory
        os.chdir(vt_save_dir)
        result = execute_cmdline(cmdline,output)
        os.chdir(cur_dir)
        #print result, output
        if result != 0 or len(output) != 0:
            for line in output:
                if line.find('deflated') == -1:
                    raise VistrailsDBException(" ".join(output))
        shutil.copyfile(tmp_zip_file, filename)
    finally:
        os.unlink(tmp_zip_file)
        os.rmdir(tmp_zip_dir)
    
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
                db.services.vistrail.synchronize(old_vistrail, vistrail, 
                                                 current_action)
            vistrail = old_vistrail
    vistrail.db_last_modified = get_current_time(db_connection)

    vistrail = translate_vistrail(vistrail, vistrail.db_version, version)
    dao_list.save_to_db(db_connection, vistrail, do_copy)
    db_connection.commit()
    vistrail = translate_vistrail(vistrail, version)
    vistrail.db_currentVersion = current_action
    return vistrail

##############################################################################
# Workflow I/O

def open_workflow_from_xml(filename):
    """open_workflow_from_xml(filename) -> DBWorkflow"""
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    workflow = daoList.open_from_xml(filename, DBWorkflow.vtType, tree)
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
    daoList.save_to_xml(workflow, filename, tags, version)
    workflow = translate_workflow(workflow, version)
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
    workflow = translate_workflow(workflow, version)
    return workflow

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
        db.services.log.update_ids(log)
    else:
        tree = ElementTree.parse(filename)
        version = get_version_for_xml(tree.getroot())
        daoList = getVersionDAO(version)
        log = daoList.open_from_xml(filename, DBLog.vtType, tree)
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

def save_log_to_xml(log, filename, version=None, do_append=False):
    if version is None:
        version = currentVersion
    if not log.db_version:
        log.db_version = currentVersion
    log = translate_log(log, log.db_version, version)

    daoList = getVersionDAO(version)
    if do_append:
        log_file = open(filename, 'ab')
        for workflow_exec in log.workflow_execs:
            # cannot do correct numbering here...
            workflow_exec.db_id = -1L
            daoList.save_to_xml(workflow_exec, log_file, {}, version)
        log_file.close()
    else:
        tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xsi:schemaLocation': 'http://www.vistrails.org/log.xsd'
                }
        daoList.save_to_xml(log, filename, tags, version)
    log = translate_log(log, version)
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
    log = translate_log(log, version)
    return log

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
    opm_graph = db.services.opm.create_opm(opm_graph.workflow, 
                                           opm_graph.version,
                                           opm_graph.log,
                                           opm_graph.registry)
    daoList.save_to_xml(opm_graph, filename, tags, version)
    return opm_graph

##############################################################################
# Registry I/O

def open_registry_from_xml(filename):
    tree = ElementTree.parse(filename)
    version = get_version_for_xml(tree.getroot())
    daoList = getVersionDAO(version)
    registry = daoList.open_from_xml(filename, DBRegistry.vtType, tree)
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
    daoList.save_to_xml(registry, filename, tags, version)
    registry = translate_registry(registry, version)
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
    registry = translate_registry(registry, version)
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
            db.services.vistrail.synchronize(old_abstraction, abstraction,
                                             0L)
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
                # timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            c.close()
        except get_db_lib().Error, e:
            print "Logger Error %d: %s" % (e.args[0], e.args[1])

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
        

