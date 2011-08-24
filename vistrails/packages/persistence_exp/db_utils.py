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

import os
import sqlite3

class DatabaseAccessSingleton(object):
    def __new__(cls, *args, **kw):
        print "got here"
        if DatabaseAccess._instance is None:
            print "instance is None"
            obj = DatabaseAccess(*args, **kw)
            DatabaseAccess._instance = obj
        return DatabaseAccess._instance

class DatabaseAccess(object):
    _instance = None
    def __init__(self, db_file):
        print 'initing DatabaseAccess'
        self.db_file = db_file
        run_schema = False
        if not os.path.exists(db_file):
            run_schema = True
        self.conn = sqlite3.connect(db_file)
        if run_schema:
            print 'running schema'
            print '__file__:', __file__
            print 'schema file:', os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'schema.sql')
            cur = self.conn.cursor()
            self.run_sql_file(cur, os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'schema.sql'))
        self.model = None

    def set_model(self, model):
        self.model = model

    def run_sql_file(self, cur, sql_file):
        cmd = ''
        for line in open(sql_file):
            cmd += line
            if line.strip().endswith(';'):
                cur.execute(cmd.strip())
                cmd = ''

    def finalize(self):
        self.conn.close()

    def write_database(self, value_dict):
#         db_file = '/vistrails/managed/files.db'
#         self.conn = sqlite3.connect(db_file)

        cur = self.conn.cursor()
        cols, vals = zip(*value_dict.iteritems())
        col_str = ', '.join(cols)
        print "executing sql:", "INSERT INTO file(%s) VALUES (%s);" % \
                        (col_str, ','.join(['?'] * len(vals)))
        print "  ", vals
        cur.execute("INSERT INTO file(%s) VALUES (%s);" % \
                        (col_str, ','.join(['?'] * len(vals))),
                    vals)
        self.conn.commit()

        if self.model:
            self.model.add_data(value_dict)

    #         cur.execute("SELECT id, name, tags, user, date_created, "
    #                     "date_modified, content_hash, version, signature "
    #                     "FROM file;")

    def read_database(self, cols=None, where_dict=None):
        # self.conn = sqlite3.connect(db_file)
        cur = self.conn.cursor()
        if cols is None:
            cols = ["id", "name", "tags", "user", "date_created",
                    "date_modified", "content_hash", "version", "signature"]
        col_str = ', '.join(cols)
        if where_dict is None or len(where_dict) <= 0:
            cur.execute("SELECT " + ", ".join(cols) + " FROM file;")
        else:
            where_cols, where_vals = zip(*where_dict.iteritems())
            where_str = '=? AND '.join(where_cols) + '=?'
            cur.execute("SELECT " + ", ".join(cols) + " FROM file "
                        "WHERE %s;" % where_str, where_vals)
        return cur.fetchall()

    def search_by_signature(self, signature):
        cur = self.conn.cursor()
        cur.execute("SELECT id, version FROM file WHERE signature=? "
                    "ORDER BY date_created DESC LIMIT 1;", (signature,))
        res = cur.fetchone()
        if res:
            return res
        return None

    def get_signature(self, id, version=None):
        cur = self.conn.cursor()
        cur.execute("SELECT signature FROM file where id=? and verison=?;", 
                    (id, version))
        res = cur.fetchone()
        if res:
            return res[0]
        return None

    def ref_exists(self, id, version=None):
        cur = self.conn.cursor()
        cur.execute("SELECT id, version FROM file WHERE id=? AND version=?;",
                    (id, version))
        res = cur.fetchone()
        return res is not None
