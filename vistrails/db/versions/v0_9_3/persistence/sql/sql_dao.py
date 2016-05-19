###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from datetime import date, datetime

from vistrails.core.system import strftime, time_strptime
from vistrails.db import VistrailsDBException

class SQLDAO:
    def __init__(self):
        pass

    def convertFromDB(self, value, type, db_type):
        if value is not None:
            if type == 'str':
                return str(value)
            elif type == 'long':
                return long(value)
            elif type == 'float':
                return float(value)
            elif type == 'int':
                return int(value)
            elif type == 'date':
                if db_type == 'date':
                    return value
                else:
                    return date(*time_strptime(str(value), '%Y-%m-%d')[0:3])
            elif type == 'datetime':
                if db_type == 'datetime':
                    return value
                else:
                    return datetime(*time_strptime(str(value),
                                                   '%Y-%m-%d %H:%M:%S')[0:6])
        return None

    def convertToDB(self, value, type, db_type):
        if value is not None:
            if type == 'str':
                # return "'" + str(value).replace("'", "''") + "'"
                return str(value)
            elif type == 'long':
                return str(value)
            elif type == 'float':
                return str(value)
            elif type == 'int':
                return str(value)
            elif type == 'date':
                return value.isoformat()
            elif type == 'datetime':
                return strftime(value, '%Y-%m-%d %H:%M:%S')
            else:
                return str(value)

        return None

    def createSQLSelect(self, table, columns, whereMap, orderBy=None, 
                        forUpdate=False):
        columnStr = ', '.join(columns)
        whereStr = ''
        whereClause = ''
        values = []
        for column, value in whereMap.iteritems():
            whereStr += '%s%s = %%s' % \
                        (whereClause, column)
            values.append(value)
            whereClause = ' AND '
        dbCommand = """SELECT %s FROM %s WHERE %s""" % \
                    (columnStr, table, whereStr)
        if orderBy is not None:
            dbCommand += " ORDER BY " + orderBy
        if forUpdate:
            dbCommand += " FOR UPDATE"
        dbCommand += ";"
        return (dbCommand, tuple(values))

    def createSQLInsert(self, table, columnMap):
        columns = []
        values = []
        for column, value in columnMap.iteritems():
            if value is None:
                value = 'NULL'
            columns.append(column)
            values.append(value)
        columnStr = ', '.join(columns)
        # valueStr = '%s, '.join(values)
        valueStr = ''
        if len(values) > 1:
            valueStr = '%s,' * (len(values) - 1) + '%s'
        dbCommand = """INSERT INTO %s(%s) VALUES (%s);""" % \
                    (table, columnStr, valueStr)
        return (dbCommand, tuple(values))

    def createSQLUpdate(self, table, columnMap, whereMap):
        setStr = ''
        comma = ''
        values = []
        for column, value in columnMap.iteritems():
#            if value is None:
#                value = 'NULL'
            setStr += '%s%s = %%s' % (comma, column)
            comma = ', '
            values.append(value)
        whereStr = ''
        whereClause = ''
        for column, value in whereMap.iteritems():
            whereStr += '%s%s = %%s' % (whereClause, column)
            values.append(value)
            whereClause = ' AND '
        dbCommand = """UPDATE %s SET %s WHERE %s;""" % \
                    (table, setStr, whereStr)
        return (dbCommand, tuple(values))

    def createSQLDelete(self, table, whereMap):
        whereStr = ''
        whereClause = ''
        values = []
        for column, value in whereMap.iteritems():
            whereStr += '%s %s = %%s' % (whereClause, column)
            values.append(value)
            whereClause = ' AND '
        dbCommand = """DELETE FROM %s WHERE %s;""" % \
            (table, whereStr)
        return (dbCommand, tuple(values))

    def executeSQL(self, db, cmd_tuple, isFetch):
        dbCommand, values = cmd_tuple
        # print 'db: %s' % dbCommand
        # print 'values:', values
        data = None
        cursor = db.cursor()
        try:
            cursor.execute(dbCommand, values)
            if isFetch:
                data = cursor.fetchall()
            else:
                data = cursor.lastrowid
        except Exception, e:
            raise VistrailsDBException('Command "%s" with values "%s" '
                                       'failed: %s' % (dbCommand, values, e))
        finally:
            cursor.close()
        return data

    def start_transaction(self, db):
        db.begin()

    def commit_transaction(self, db):
        db.commit()

    def rollback_transaction(self, db):
        db.rollback()
