############################################################################
##
## Copyright (C) 2006-2011 University of Utah. All rights reserved.
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
from db import VistrailsDBException
from db.services.io import open_db_connection, close_db_connection, get_db_lib

class LogQuery:
    """ Builds a SQL log query with joins """
    def __init__(self, db_connection):
        self.db_connection = db_connection

        # a statement is a ('table', )
        self.tables = ['workflow_exec']
        self.conditions = []
        self.limit = 'LIMIT 10'

    def execute(self):
        """ Executes query and returns list of (vt_id, log_id, workflow_exec_id) """
        query = 'SELECT parent_id, log_id, id FROM '
        query += ', '.join(self.tables)
        if len(self.conditions):
            query += ' WHERE ' + ' AND '.join(self.conditions)
        query += ' ' + self.limit
        return []
    
def retrieve(config, vistrail=None, version=None, fromTime=None, toTime=None,
             user=None, completed=None, offset=0, limit=100, modules=[]):
    result = []
    db = open_db_connection(config)
    select_part = \
    """SELECT v.name, v.id, w.entity_id,
              w.parent_version, a1.value, w.id,
              w.ts_start, w.ts_end, w.user, w.completed, t.image_bytes"""
    from_part = \
    """FROM workflow_exec w JOIN
            log_tbl l ON (l.id = w.entity_id) JOIN
            vistrail v ON (l.vistrail_id = v.id) LEFT JOIN
            action_annotation a1 ON (a1.entity_id=v.id AND
                                     a1.action_id=w.parent_version) LEFT JOIN
            action_annotation a2 ON (a2.entity_id=v.id AND
                                     a2.action_id=w.parent_version) LEFT JOIN
            thumbnail t ON a2.value=t.file_name"""
    where_part = \
    """WHERE w.parent_type='vistrail' AND
             w.entity_type='log' AND
             (a1.akey='__tag__' OR a1.akey IS NULL) AND
             (a2.akey='__thumb__' OR a2.akey IS NULL)"""
    limit_part = 'LIMIT %s, %s' % (int(offset), int(limit))

    if vistrail:
        try:
            where_part += " AND v.id=%s" % int(vistrail)
        except ValueError:
            where_part += " AND v.name=%s" % \
                   db.escape(vistrail, get_db_lib().converters.conversions)
    if version:
        try:
            where_part += " AND w.parent_version=%s" % int(version)
        except ValueError:
            where_part += " AND a.value=%s" % \
                   db.escape(version, get_db_lib().converters.conversions)
    if fromTime:
        where_part += " AND w.ts_end>%s" % \
               db.escape(fromTime, get_db_lib().converters.conversions)
    if toTime:
        where_part += " AND w.ts_start<%s" % \
               db.escape(toTime, get_db_lib().converters.conversions)
    if user:
        where_part += " AND w.user=%s" % \
               db.escape(user, get_db_lib().converters.conversions)
    completed_dict = {'no':0, 'yes':1, 'ok':1}
    if completed is not None:
        try:
            int(completed)
        except ValueError:
            completed = completed_dict.get(str(completed).lower(), -1)
        where_part += " AND w.completed=%s" % completed
    # TODO nested module executions are not detected
    for i, module, mCompleted in zip(range(1,len(modules)+1), *zip(*modules)):
        alias = "m%s"%i
        from_part += \
        """ JOIN module_exec %s ON
                (%s.parent_id=w.id AND
                 %s.entity_id=w.entity_id AND
                 %s.entity_type=w.entity_type)
        """.replace('%s', alias)
        where_part += \
        """ AND %s.parent_type='workflow_exec'
            AND %s.module_name=%s """ % (alias, alias,
              db.escape(module.lower(), get_db_lib().converters.conversions) )
        if mCompleted is not None:
            mCompleted = completed_dict.get(str(mCompleted).lower(), -1)
            where_part += """ AND %s.completed=%s""" % (alias, mCompleted)
            
    command = ' '.join([select_part, from_part, where_part, limit_part]) + ';'
    print command
    try:
        c = db.cursor()
        c.execute(command)
        rows = c.fetchall()
        result = rows
        c.close()
    except get_db_lib().Error, e:
        msg = "Couldn't perform query on db (%d : %s)" % \
            (e.args[0], e.args[1])
        raise VistrailsDBException(msg)

    # count all rows when offset = 0
    if 0 == offset:
        select_part = 'SELECT count(0)'
        command = ' '.join([select_part,from_part,where_part]) +';'
        print command
        try:
            c = db.cursor()
            c.execute(command)
            res = c.fetchall()
            result= (result, res[0][0])
            c.close()
        except get_db_lib().Error, e:
            msg = "Couldn't perform query on db (%d : %s)" % \
                (e.args[0], e.args[1])
            raise VistrailsDBException(msg)

    close_db_connection(db)
    return result
