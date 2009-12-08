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

from db import VistrailsDBException

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
                    return date(*strptime(str(value), '%Y-%m-%d')[0:3])
            elif type == 'datetime':
                if db_type == 'datetime':
                    return value
                else:
                    return datetime(*strptime(str(value), 
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
                return value.strftime('%Y-%m-%d %H:%M:%S')
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
# 	    if value is None:
# 		value = 'NULL'
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
            whereStr += '%s %s = %%s' % \
                (whereClause, column, value)
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
