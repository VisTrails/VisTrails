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
from vistrails.db import VistrailsDBException
from vistrails.core import debug

import sqlalchemy
import sqlalchemy.sql
import alchemy

class SQLDAO:
    metadata = alchemy.metadata
    engine = None

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

    def convertWarning(self, before, after, _from, to):
        text = ["Value truncated when saving to database",
                "%s truncated to %s\nwhile converting '%s' to '%s'"]
        debug.warning(text[0], text[1] % (before, after, _from, to))

    def convertToDB(self, value, type, db_type):
        if value is not None:
            if type == 'str':
                value = str(value)
                if db_type.startswith('varchar'):
                    try:
                        length = int(db_type[8:-1])
                        if len(value) > length:
                            self.convertWarning(value, value[:length],
                                                type, db_type)
                            value = value[:length]
                    except Exception, e:
                        pass
                if db_type.startswith('char'):
                    try:
                        length = int(db_type[5:-1])
                        if len(value) > length:
                            self.convertWarning(value, value[:length],
                                                type, db_type)
                            value = value[:length]
                    except Exception, e:
                        pass
                # return "'" + str(value).replace("'", "''") + "'"
                return value
            elif type == 'long':
                return str(value)
            elif type == 'float':
                # necessary to avoid conversion warnings in MySQL
                if db_type.startswith('DECIMAL'):
                    try:
                        value="%%.%sf"%str(db_type[8:-1].split(',')[1])%value
                    except Exception, e:
                        pass
                return str(value)
            elif type == 'int':
                # note: on 64-bit machines int:s are 64-bit
                MIN_INT = -2147483648
                MAX_INT =  2147483647
                if db_type == 'int':
                    if int(value) < MIN_INT:
                        self.convertWarning(value, MIN_INT, type, db_type)
                        value = MIN_INT
                    if int(value) > MAX_INT:
                        self.convertWarning(value, MAX_INT, type, db_type)
                        value = MAX_INT
                return str(value)
            elif type == 'date':
                # return value.isoformat()
                return value
            elif type == 'datetime':
                # return value.strftime('%Y-%m-%d %H:%M:%S')
                return value
            else:
                return str(value)

        return None

    def createSQLSelect(self, table, columns, whereMap, orderBy=None, 
                        forUpdate=False):
        sql_table = self.metadata.tables[table]
        cmd = sqlalchemy.select([sql_table.columns[c] for c in columns],
                                for_update=forUpdate)
        if len(whereMap) > 0:
            cmd = cmd.where(sqlalchemy.sql.and_(*[sql_table.columns[c] == v 
                                                  for c,v in whereMap.iteritems()]))
        if orderBy is not None:
            cmd = cmd.order_by(sql_table.columns[orderBy])
        
        return cmd

    def createSQLInsert(self, table, columnMap):
        sql_table = self.metadata.tables[table]
        cmd = sql_table.insert().values(columnMap)
        return cmd

    def createSQLUpdate(self, table, columnMap, whereMap):
        sql_table = self.metadata.tables[table]
        cmd = sql_table.update([sql_table.columns[c] for c in columnMap])
        cmd = cmd.where(sqlalchemy.sql.and_(sql_table.columns[c] == v
                                            for c,v in whereMap.iteritems()))
        cmd = cmd.values(columnMap)
        return cmd

    def createSQLDelete(self, table, whereMap):
        sql_table = self.metadata.tables[table]
        cmd = sql_table.delete().where(sql_table.columns[c] == v
                                       for c,v in whereMap.iteritems())
        return cmd

    def executeSQL(self, db, cmd_tuple, isFetch):
        result = db.execute(cmd_tuple)

        if isFetch:
            data = result
        else:
            data = result.inserted_primary_key
            if len(data) > 0:
                data = data[0]
            else:
                data = None
        return data

    def executeSQLGroup(self, db, dbCommandList, isFetch):
        """ Executes a command consisting of multiple SELECT statements
            It returns a list of results from the SELECT statements
        """
        # break up into bundles
        BUNDLE_SIZE = 10000
        data = []
        num_commands = len(dbCommandList)
        for start in xrange(0,num_commands, BUNDLE_SIZE):
            cmds_str = ""
            params = []
            for i in xrange(start, min(num_commands, start+BUNDLE_SIZE)):
                cmd = dbCommandList[i]
                compiled_cmd = cmd.compile(dialect=db.dialect)
                cmds_str += compiled_cmd.string + ";\n"
                for k in compiled_cmd.positiontup:
                    v = compiled_cmd.params[k]
                    params.append(v)
            cur = db.connection.cursor()
            try:
                result = cur.execute(cmds_str, params)
                while True:
                    r = cur.fetchall() if isFetch else cur.lastrowid
                    data.append(r)
                    next = cur.nextset()
                    if not next:
                        break
            finally:
                cur.close()
        return data

    def executeSQLCommands(self, db, dbCommandList, isFetch):
        if db.dialect.name == 'mysql':
            return self.executeSQLGroup(db, dbCommandList, isFetch)
        else:
            results = []
            for cmd in dbCommandList:
                res = self.executeSQL(db, cmd, isFetch)
                results.append(res)
            return results

    def start_transaction(self, db):
        return db.begin()

    def commit_transaction(self, db, trans=None):
        trans.commit()
        db.commit()

    def rollback_transaction(self, db):
        db.rollback()
