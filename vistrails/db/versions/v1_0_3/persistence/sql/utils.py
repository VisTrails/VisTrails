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
from __future__ import with_statement

from datetime import datetime
import os

from vistrails.core import debug
from vistrails.core.bundles import py_import

from vistrails.db.versions.v1_0_3 import version as my_version
from vistrails.db.versions.v1_0_3.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBAbstraction, DBAnnotation


from vistrails.db import VistrailsDBException

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
    try:
        to_remove = []
        for k, v in config.iteritems():
            if v is None:
                to_remove.append(k)
        map(config.__delitem__, to_remove)

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
            debug.critical("Logger Error %d: %s" % (e.args[0], e.args[1]))

    return timestamp


def execute_file(c, f):
    cmd = ""
    for line in f:
        line = line.strip()
        if cmd or not line.startswith('--'):
            cmd += line
            ending = line
        else:
            ending = None
        if ending and ending[-1] == ';':
            cmd = cmd.rstrip()
            #print cmd
            c.execute(cmd)
            cmd = ""

def create_db_tables(db_connection):
    from vistrails.db.versions import getVersionSchemaDir

    try:
        c = db_connection.cursor()
        schemaDir = getVersionSchemaDir(my_version)
        f = open(os.path.join(schemaDir, 'vistrails.sql'))
        execute_file(c, f)
        f.close()
        c.close()
    except get_db_lib().Error, e:
        raise VistrailsDBException("unable to create tables: " + str(e))

def drop_db_tables(db_connection):
    from vistrails.db.versions import getVersionSchemaDir

    try:
        c = db_connection.cursor()
        schemaDir = getVersionSchemaDir(my_version)
        f = open(os.path.join(schemaDir, 'vistrails_drop.sql'))
        execute_file(c, f)
        c.close()
        f.close()
    except get_db_lib().Error, e:
        raise VistrailsDBException("unable to create tables: " + str(e))

def start_transaction(db_connection):
    return db_connection.begin()

def commit_transaction(db_connection, trans=None):
    db_connection.commit()

def rollback_transaction(db_connection, trans=None):
    db_connection.rollback()

def translate_to_tbl_name(obj_type):
    map = {DBVistrail.vtType: 'vistrail',
           DBWorkflow.vtType: 'workflow',
           DBLog.vtType: 'log_tbl',
           DBRegistry.vtType: 'registry',
           DBAbstraction.vtType: 'abstraction',
           DBAnnotation.vtType: 'annotation',
           }
    return map[obj_type]

def date_to_str(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

def get_db_object_list(db_connection, obj_type):
    
    result = []    

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
        c = db_connection.cursor()
        c.execute(command % translate_to_tbl_name(obj_type))
        rows = c.fetchall()
        result = rows
        c.close()
        
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

def get_db_ids_from_log(db_connection, vt_id):
    command = """SELECT id FROM log_tbl WHERE vistrail_id=%s;"""
    ids = []
    try:
        c = db_connection.cursor()
        res = c.execute(command, (vt_id,))
        ids = [i[0] for i in c.fetchall()]
        c.close()
    except get_db_lib().Error, e:
        debug.critical("Error getting log id:s %d: %s" % (e.args[0], e.args[1]))
    return ids

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

def get_saved_workflows(db_connection, vistrail_id):
    """ Returns list of action id:s representing populated workflows """
    if not vistrail_id:
        return []
    c = db_connection.cursor()
    c.execute("SELECT parent_id FROM workflow WHERE vistrail_id=%s;", 
              (vistrail_id,))
    ids = [i[0] for i in c.fetchall()]
    c.close()
    return ids

##############################################################################
# Thumbnail I/O

def get_thumbnail_fnames_from_db(db_connection, obj_id, obj_type):
    prepared_statement = format_prepared_statement(
    """
    SELECT a.value
    FROM annotation a
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
    return file_names

def get_thumbnail_data_from_db(db_connection, fname):
    prepared_statement = format_prepared_statement(
    """
    SELECT t.image_bytes
    FROM thumbnail t
    WHERE t.file_name = ?
    """)
    try:
        c = db_connection.cursor()
        c.execute(prepared_statement, (fname,))
        row = c.fetchone()
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't get thumbnail from db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    if row is not None:
        return row[0]
    return None

def get_existing_thumbnails_in_db(db_connection, fnames):
    statement = """
    SELECT t.file_name
    FROM thumbnail t
    WHERE t.file_name IN %s
    """
    # SQL syntax needs SOMETHING if list is empty - use filename that's illegal on all platforms
    fnames.append(':/')
    sql_in_token = str(tuple(fnames + [':/',]))
    try:
        c = db_connection.cursor()
        c.execute(statement % sql_in_token)
        db_file_names = [file_name for (file_name,) in c.fetchall()]
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't check which thumbnails already exist in db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
    return db_file_names

def insert_thumbnails_into_db(db_connection, abs_fnames):
    prepared_statement = format_prepared_statement(
    """
    INSERT INTO thumbnail(file_name, image_bytes, last_modified)
    VALUES (?, ?, ?)
    """)
    try:
        c = db_connection.cursor()
        for absfname in abs_fnames:
            image_file = open(absfname, 'rb')
            image_bytes = image_file.read()
            image_file.close()
            c.execute(prepared_statement, (os.path.basename(absfname), image_bytes, get_current_time(db_connection).strftime('%Y-%m-%d %H:%M:%S')))
            db_connection.commit()
        c.close()
    except IOError, e:
        msg = "Couldn't read thumbnail file for writing to db: %s" % absfname
        raise VistrailsDBException(msg)
    except get_db_lib().Error, e:
        msg = "Couldn't insert thumbnail into db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)
