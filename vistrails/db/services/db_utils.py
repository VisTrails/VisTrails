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
from datetime import datetime
import re
import vistrails.db.versions

class DBConnection(object):
    def __init__(self):
        self.auto_inc_re = re.compile("auto_increment", re.IGNORECASE)
        self.autoinc_re = re.compile("autoincrement", re.IGNORECASE)
        self.engine_re = re.compile("engine=InnoDB", re.IGNORECASE)
        self.int_type_re = re.compile(" int([ ,)])", re.IGNORECASE)
        self.autoinc_pk_re = re.compile("autoincrement primary key", 
                                        re.IGNORECASE)

    def get_connection(self):
        raise NotImplementedError("Subclass must implment get_connection.")

    def get_param_style(self):
        raise NotImplementedError("Subclass must implment get_param_style.")

    def format_stmt(self, statement):
        """format_prepared_statement(statement: str) -> str
        Formats a prepared statement for compatibility with the currently
        loaded database library's paramstyle.

        Currently only supports 'qmark' and 'format' paramstyles.
        May be expanded later to allow for more compatibility options
        on input and output.  See PEP 249 for more info.

        """

        style = self.get_param_style()
        if style == 'format':
            statement = statement.replace("?", "%s")
        elif style == 'qmark':
            statement = statement.replace("%s", "?")

        auto_inc = self.get_auto_inc()
        if auto_inc == "autoincrement":
            statement = self.auto_inc_re.sub("autoincrement", statement)
        elif auto_inc == "auto_increment":
            statement = self.auto_inc_re.sub("auto_increment", statement)

        engine = self.get_engine()
        if not engine:
            statement = self.engine_re.sub("", statement)

        int_type = self.get_int_type()
        if int_type == 'integer':
            statement = self.int_type_re.sub(" integer\\1", statement)

        statement = self.autoinc_pk_re.sub("primary key autoincrement", 
                                           statement)
        return statement

    def close(self):
        self.get_connection().close()

    def run_sql_file(self, fname):
        c = self.get_connection().cursor()
        with open(fname, 'rU') as f:
            cmd = ""
            # auto_inc_str = 'auto_increment'
            # not_null_str = 'not null'
            # engine_str = 'engine=InnoDB;'
            for line in f:
                # if line.find(auto_inc_str) > 0:
                #     num = line.find(auto_inc_str)
                #     line = line[:num] + line[num+len(auto_inc_str):]
                # if line.find(not_null_str) > 0:
                #     num = line.find(not_null_str)
                #     line = line[:num] + line[num+len(not_null_str):]
                line = line.strip()
                if cmd or not line.startswith('--'):
                    cmd += line
                    ending = line
                else:
                    ending = None
                if ending and ending[-1] == ';':
                    # FIXME engine stuff switch for MySQLdb, sqlite3
                    cmd = cmd.rstrip()
                    # if cmd.endswith(engine_str):
                    #     cmd = cmd[:-len(engine_str)] + ';'
                    print "CMD:", cmd
                    c.execute(self.format_stmt(cmd))
                    cmd = ""
        
        

    def setup_db_tables(self, version=None, old_version=None):
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
                    c.execute(self.format_stmt(cmd))
                    cmd = ""

        if version is None:
            version = currentVersion
        if old_version is None:
            old_version = version

        # delete tables
        c = self.get_connection().cursor()
        schema_dir = vistrails.db.versions.getVersionSchemaDir(old_version)
        f = open(os.path.join(schema_dir, 'vistrails_drop.sql'))
        execute_file(c, f)
#         db_script = f.read()
#         c.execute(db_script)
        c.close()
        f.close()

        # create tables        
        c = self.get_connection().cursor()
        schemaDir = vistrails.db.versions.getVersionSchemaDir(version)
        f = open(os.path.join(schemaDir, 'vistrails.sql'))
        execute_file(c, f)
#         db_script = f.read()
#         c.execute(db_script)
        f.close()
        c.close()

class MySQLDBConnection(DBConnection):
    def __init__(self, *args, **kwargs):
        DBConnection.__init__(self)
        import MySQLdb
        self._args = args
        self._kwargs = kwargs
        self._connection = None
        
    def get_connection(self):
        import MySQLdb
        if self._connection is None:
            self._connection = MySQLdb.connect(*self._args, **self._kwargs)
        return self._connection        

    def get_param_style(self):
        import MySQLdb
        return MySQLdb.paramstyle

    def get_auto_inc(self):
        return "auto_increment"

    def get_current_time(self):
        timestamp = datetime.now()
        try:
            c = self.get_connection().cursor()
            c.execute("SELECT NOW();")
            row = c.fetchone()
            if row:
                timestamp = row[0]
            c.close()
        finally:
            return timestamp

    def get_engine(self):
        return "engine=InnoDB"

    def get_int_type(self):
        return "int"

class SQLite3Connection(DBConnection):
    def __init__(self, *args, **kwargs):
        DBConnection.__init__(self)
        import sqlite3
        self._args = args
        self._kwargs = kwargs
        self._connection = None

    def get_connection(self):
        import sqlite3
        if self._connection is None:
            self._connection = sqlite3.connect(*self._args, **self._kwargs)
        return self._connection        

    def get_param_style(self):
        import sqlite3
        return sqlite3.paramstyle

    def get_auto_inc(self):
        return "autoincrement"

    def get_current_time(self):
        timestamp = datetime.now()
        try:
            c = self.get_connection().cursor()
            c.execute("SELECT DATETIME('NOW');")
            row = c.fetchone()
            if row:
                timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            c.close()
        finally:
            return timestamp
        
    def get_engine(self):
        return ""

    def get_int_type(self):
        return "integer"

