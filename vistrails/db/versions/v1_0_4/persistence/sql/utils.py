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

from vistrails.core.bundles import py_import

sqlalchemy = py_import('sqlalchemy', 
                       {'pip': 'SQLAlchemy',
                        'linux-debian': 'python-sqlalchemy',
                        'linux-ubuntu': 'python-sqlalchemy',
                        'linux-fedora': 'python-sqlalchemy'})

from datetime import datetime
import inspect
import os

from vistrails.db.versions.v1_0_4 import version as my_version
from vistrails.db.versions.v1_0_4.domain import DBVistrail, \
    DBWorkflow, DBLog, DBRegistry, DBAbstraction, DBMashuptrail, DBAnnotation

import alchemy

def open_db_connection(config):
    # FIXME need to make this more general (just connect_str) here so
    # that it is more straightforward to support other types of
    # databases

    if config is None:
        msg = "Need to provide a valid configuration dictionary or string"
        raise VistrailsDBException(msg)
    if type(config) == dict:
        if config.get("dialect") is not None:
            driver = config["dialect"]
        else:
            driver = "mysql"
        if config.get("driver") is not None:
            driver += "+%s" % config["driver"]
        url = sqlalchemy.engine.url.URL(driver, 
                                        config.get("user"), 
                                        config.get("passwd"), 
                                        config.get("host"), 
                                        config.get("port"), 
                                        config.get("db"))
        connection = sqlalchemy.create_engine(url).connect()
    else:
        connection = sqlalchemy.create_engine(config).connect()
    return connection

def close_db_connection(db_connection):
    if db_connection is not None:
        db_connection.close()

def test_db_connection(config):
    """testDBConnection(config: dict) -> None
    Tests a connection raising an exception in case of error.
    
    """
    try:
        db_connection = open_db_connection(config)
        close_db_connection(db_connection)
    except Exception, e:
        msg = "connection test failed (%s)" %str(e)
        raise VistrailsDBException(msg)

def ping_db_connection(db_connection):
    """ping_db_connection(db_connection) -> boolean 
    It will ping the database to check if the connection is alive.
    It returns True if it is, False otherwise. 
    This can be used for preventing the "MySQL Server has gone away" error. 
    """

    # CHECK not sure if this works
    c = db_connection.connection.cursor()
    try:
        c.execute("SELECT 1")
    except:
        return False
    return True

def create_db_tables(db_connection):
    trans = db_connection.begin()
    alchemy.metadata.create_all(db_connection)
    ins = get_table_by_name("vistrails_version").insert()
    db_connection.execute(ins, version=my_version)
    trans.commit()
    
def drop_db_tables(db_connection):
    trans = db_connection.begin()
    alchemy.metadata.drop_all(db_connection)
    trans.commit()

def start_transaction(db_connection):
    return db_connection.begin()

def commit_transaction(db_connection, trans=None):
    trans.commit()

def rollback_transaction(db_connection, trans=None):
    trans.rollback()

##############################################################################
# Utility methods
##############################################################################

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

def get_table(obj_klass_or_type):
    if inspect.isclass(obj_klass_or_type):
        obj_type = obj_klass_or_type.vtType
    else:
        obj_type = obj_klass_or_type
        
    return alchemy.metadata.tables[translate_to_tbl_name(obj_type)]

def get_table_by_name(table_name):
    return alchemy.metadata.tables[table_name]

def get_current_time(db_connection=None):
    timestamp = datetime.now()
    if db_connection is not None:
        try:
            cmd = sqlalchemy.select([sqlalchemy.func.current_timestamp()])
            result = db_connection.execute(cmd)
            timestamp = result.first()[0]
        except Exception, e:
            debug.critical("Cannot obtain current time: %s" % str(e))
    return timestamp

##############################################################################
# Access methods
##############################################################################

def get_db_object_list(db_connection, obj_type):
    result = []    

    obj = get_table(obj_type)
    cmd = sqlalchemy.select([obj.c.id, obj.c.name, obj.c.last_modified])
    if obj_type == DBVistrail.vtType:
        annotation = get_table(DBAnnotation)
        cmd = cmd.where(obj.c.id.notin_(sqlalchemy.select([obj.c.id]).where(
            sqlalchemy.sql.and_(obj.c.id == annotation.c.parent_id, 
                                annotation.c.parent_type == \
                                    translate_to_tbl_name(obj_type),
                                annotation.c.akey == '__abstraction_uuid__'))))
    cmd = cmd.order_by(obj.c.name)

    result = db_connection.execute(cmd)
    return result.fetchall()

def get_db_object_modification_time(db_connection, obj_id, obj_type):
    obj = get_table(obj_type)
    cmd = sqlalchemy.select([obj.c.last_modified]).where(obj.c.id == obj_id)

    result = db_connection.execute(cmd)
    row = result.first()
    if row is not None:
        return row[0]
    return None

def get_db_object_version(db_connection, obj_id, obj_type):
    obj = get_table(obj_type)
    cmd = sqlalchemy.select([obj.c.version]).where(obj.c.id == obj_id)

    result = db_connection.execute(cmd)
    row = result.first()
    if row is not None:
        return row[0]
    return None

def get_db_id_from_name(db_connection, obj_type, name):
    obj = get_table(obj_type)
    cmd = sqlalchemy.select([obj.c.id]).where(obj.c.name == name)

    result = db_connection.execute(cmd)
    rows = result.fetchall()
    if len(rows) == 0:
        msg = "Cannot find object of type '%s' named '%s'" % \
              (obj_type, name)
        raise VistrailsDBException(msg)
    elif len(rows) > 1:
        msg = "Found more than one object of type '%s' named '%s'" % \
              (obj_type, name)
        raise VistrailsDBException(msg)
    
    return rows[0][0]
    
def get_db_abstraction_modification_time(db_connection, abstraction):
    if abstraction.db_has_annotation_with_key(id_key):
        id_value = abstraction.db_get_annotation_by_key(id_key).db_value
    else:
        return None

    vistrail_tbl_type = translate_to_tbl_name(DBVistrail.vtType)
    vistrail = get_table(DBVistrail)
    annotation = get_table(DBAnnotation)
    cmd = sqlalchemy.select([vistrail.last_modified]).where(
        sqlalchemy.sql.and_(vistrail.c.id == abstraction.db_id,
                            vistrail.c.id == annotation.c.parent_id,
                            annotation.c.parent_type == vistrail_tbl_type,
                            annotation.c.akey == '__abstraction_vistrail_id__',
                            annotation.c.value == id_value))
    result = db_connection.execute(cmd)
    return result.first()[0]

def get_db_ids_from_vistrail(db_connection, vt_id, id_key):
    """ get_db_ids_from_vistrail(db_connection: DBConnection,
                                 vt_id: int, id_key: str): List
        Returns object ids associated with a vistrail by an annotation
    """
    annotation = get_table(DBAnnotation)
    cmd = sqlalchemy.select([annotation.c.parent_id]).where(
        sqlalchemy.sql.and_(annotation.c.akey == id_key,
                            annotation.c.value == vt_id))

    result = db_connection.execute(cmd)
    return [row[0] for row in result.fetchall()]

def get_db_ids_from_log(db_connection, vt_id):
    log = get_table(DBLog)
    cmd = sqlalchemy.select([log.c.id]).where(log.c.vistrail_id == vt_id)
    
    result = db_connection.execute(cmd)
    return [row[0] for row in result.fetchall()]

def get_matching_abstraction_id(db_connection, abstraction):
    last_action_id = -1
    last_action = None
    for action in abstraction.db_actions:
        if action.db_id > last_action_id:
            last_action_id = action.db_id
            last_action = action

    abs_tbl = get_table(DBAbstraction)
    action = get_table(DBAction)
    cmd = sqlalchemy.select([abs_tbl.c.id]).where(
        sqlalchemy.sql.and_(abs_tbl.c.name == abstraction.db_name,
                            action.c.entity_type == 'abstraction',
                            action.c.entity_id == abs_tbl.c.id,
                            action.c.user == last_action.db_user,
                            action.c.date == last_action.db_date,
                            action.c.id == last_action.db_id))

    result = db_connection.execute(cmd)
    ids = result.fetchall()
    if len(ids) > 0:
        return ids[0][0]
    return None

def get_saved_workflows(db_connection, vistrail_id):
    """ Returns list of action ids representing populated workflows """
    if not vistrail_id:
        return []

    workflow = get_table(DBWorkflow)
    cmd = sqlalchemy.select([workflow.c.parent_id]).where(
        workflow.c.vistrail_id == vistrail_id)

    result = db_connection.execute(cmd)
    return [row[0] for row in result.fetchall()]

def get_thumbnail_fnames_from_db(db_connection, obj_id, obj_type):
    annotation = get_table(DBAnnotation)
    cmd = sqlalchemy.select([annotation.c.value]).where(
        sqlalchemy.sql.and_(annotation.c.akey == '__thumb___',
                            annotation.c.entity_id == obj_id,
                            annotation.c.entity_type == obj_type))
    
    result = db_connection.execute(cmd)
    return [row[0] for row in result.fetchall()]

def get_thumbnail_data_from_db(db_connection, fname):
    thumbnail = get_table_by_name("thumbnail")
    cmd = sqlalchemy.select([thumbnail.c.image_bytes]).where(
        thumbnail.c.file_name == fname)

    result = db_connection.execute(cmd)
    rows = result.first()
    if rows is None:
        return None
    else:
        return rows[0]

def get_existing_thumbnails_in_db(db_connection, fnames):
    thumbnail = get_table_by_name("thumbnail")
    cmd = sqlalchemy.select([thumbnail.c.file_name]).where(
        thumbnail.c.file_name.in_(fnames))

    result = db_connection.execute(cmd)
    return [row[0] for row in result.fetchall()]

def insert_thumbnails_into_db(db_connection, abs_fnames):
    thumbnail = get_table_by_name("thumbnail")
    cmd = thumbnail.insert()
    BUNDLE_SIZE = 50
    for start in xrange(0, len(abs_fnames), BUNDLE_SIZE):
        values = []
        for i in xrange(start, min(len(abs_fnames), start+BUNDLE_SIZE)):
            abs_fname = abs_fnames[i]
            image_file = open(abs_fname, 'rb')
            image_bytes = image_file.read()
            image_file.close()
            values.append({'file_name': os.path.basename(abs_fname),
                           'image_bytes': image_bytes,
                           'last_modified': get_current_time(db_connection)})
        db_connection.execute(cmd, values)
