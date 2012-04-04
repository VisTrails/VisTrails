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
from db import VistrailsDBException
from db.services.io import open_db_connection, close_db_connection, get_db_lib

def runWorkflowQuery(config, vistrail=None, version=None, fromTime=None,
        toTime=None, user=None, offset=0, limit=100, modules=[], thumbs=None):
    # returns list of workflows:
    #         (vistrail name, vistrail id, id, name, date, user, thumb)
    result = []
    db = open_db_connection(config)
    select_part = \
    """SELECT DISTINCT v.name, v.id, w.parent_id, a1.value,
              action.date, action.user"""
    from_part = \
    """FROM workflow w"""
    # "tag name" exist in workflow table but may have been changed
    # so we use value from the vistrail __tag__ annotation
    where_part = \
    """WHERE w.entity_type='workflow'"""
    limit_part = 'LIMIT %s, %s' % (int(offset), int(limit))

    if vistrail:
        try:
            where_part += " AND v.id=%s" % int(vistrail)
        except ValueError:
            where_part += " AND v.name=%s" % \
                   db.escape(vistrail, get_db_lib().converters.conversions)
    if version:
        try:
            where_part += " AND w.parent_id=%s" % int(version)
        except ValueError:
            where_part += " AND a1.value=%s" % \
                   db.escape(version, get_db_lib().converters.conversions)
    if fromTime:
        where_part += " AND w.last_modified>%s" % \
               db.escape(fromTime, get_db_lib().converters.conversions)
    if toTime:
        where_part += " AND w.last_modified<%s" % \
               db.escape(toTime, get_db_lib().converters.conversions)
    if user:
        where_part += " AND action.user=%s" % \
               db.escape(user, get_db_lib().converters.conversions)
    next_port = 1
    old_alias = None
    for i, module, connected in zip(range(1,len(modules)+1), *zip(*modules)):
        module = module.lower()
        alias = "m%s"%i
        from_part += \
        """ JOIN module {0} ON
                ({0}.parent_id=w.id AND {0}.entity_type=w.entity_type AND
                 {0}.name={1})
        """.format(alias,
                   db.escape(module, get_db_lib().converters.conversions))
        if connected:
            p1_alias, p2_alias=("port%s"%next_port), ("port%s"%(next_port+1))
            next_port += 2
            from_part += \
            """ JOIN port {0} ON
                ({0}.entity_id=w.id AND {0}.entity_type=w.entity_type AND
                 {0}.moduleId={1}.id AND {0}.type='source')""".format(
                 p1_alias, old_alias)
            from_part += \
            """ JOIN port {0} ON
                ({0}.entity_id=w.id AND {0}.entity_type=w.entity_type AND
                 {0}.moduleId={1}.id AND {0}.type='destination' AND
                 {0}.parent_id = {2}.parent_id)""".format(
                 p2_alias, alias, p1_alias)
        old_alias = alias
    from_part += \
    """ JOIN vistrail v ON w.vistrail_id = v.id JOIN
            action ON action.entity_id=w.vistrail_id AND
                       action.id=w.parent_id LEFT JOIN
            action_annotation a1 ON
                a1.entity_id=w.vistrail_id AND
                a1.action_id=w.parent_id AND
                (a1.akey='__tag__' OR a1.akey IS NULL)"""
    if thumbs:
        select_part += ', t.image_bytes'
        from_part += """ LEFT JOIN action_annotation a2 ON
                              (a2.entity_id=w.vistrail_id AND
                               a2.action_id=w.parent_id AND
                               (a2.akey='__thumb__' OR
                                a2.akey IS NULL)) LEFT JOIN
                         thumbnail t ON a2.value=t.file_name"""
    else:
        select_part += ', NULL'

    command = ' '.join([select_part, from_part, where_part, limit_part]) + ';'
    #print command
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
        #print command
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

def runLogQuery(config, vistrail=None, version=None, fromTime=None, toTime=None,
             user=None, completed=None, offset=0, limit=100, modules=[],
             thumbs=None):
    # returns list of workflow executions:
    #         (vistrail name, vistrail id, log id, workflow id, workflow name,
    #          execution id, start time, end time, user, completed, thumb)
    result = []
    db = open_db_connection(config)
    select_part = \
    """SELECT DISTINCT v.name, v.id, w.entity_id,
              w.parent_version, a1.value, w.id,
              w.ts_start, w.ts_end, w.user, w.completed"""
    from_part = \
    """FROM workflow_exec w JOIN
            log_tbl l ON (l.id = w.entity_id) JOIN
            vistrail v ON (l.vistrail_id = v.id) LEFT JOIN
            action_annotation a1 ON (a1.entity_id=v.id AND
                                     a1.action_id=w.parent_version)"""
    where_part = \
    """WHERE w.parent_type='vistrail' AND
             w.entity_type='log' AND
             (a1.akey='__tag__' OR a1.akey IS NULL)"""
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
            where_part += " AND a1.value=%s" % \
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
    if thumbs:
        select_part += ', t.image_bytes'
        from_part += """ LEFT JOIN action_annotation a2 ON
                              (a2.entity_id=v.id AND
                               a2.action_id=w.parent_version) LEFT JOIN
                         thumbnail t ON a2.value=t.file_name"""
        where_part += " AND (a2.akey='__thumb__' OR a2.akey IS NULL)"
    else:
        select_part += ', NULL'
        
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
    #print command
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
        #print command
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
