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
import re

class DBConnection(object):
    def __init__(self):
        self.auto_inc_re = re.compile("auto_increment", re.IGNORECASE)
        self.autoinc_re = re.compile("autoincrement", re.IGNORECASE)

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

        return statement

    def close(self):
        self.get_connection().close()

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
