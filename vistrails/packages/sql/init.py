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

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
import urllib

from vistrails.core.db.action import create_action
from vistrails.core.bundles.installbundle import install
from vistrails.core import debug
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
from vistrails.core.utils import versions_increasing

from vistrails.packages.tabledata.common import TableObject


class DBConnection(Module):
    """Connects to a database.

    If the URI you enter uses a driver which is not currently installed,
    VisTrails will try to set it up.
    """
    _input_ports = [('protocol', '(basic:String)'),
                    ('user', '(basic:String)',
                     {'optional': True}),
                    ('password', '(basic:String)',
                     {'optional': True}),
                    ('host', '(basic:String)',
                     {'optional': True}),
                    ('port', '(basic:Integer)',
                     {'optional': True}),
                    ('db_name', '(basic:String)')]
    _output_ports = [('connection', '(DBConnection)')]

    def compute(self):
        url = URL(drivername=self.get_input('protocol'),
                  username=self.force_get_input('user', None),
                  password=self.force_get_input('password', None),
                  host=self.force_get_input('host', None),
                  port=self.force_get_input('port', None),
                  database=self.get_input('db_name'))

        try:
            engine = create_engine(url)
        except ImportError, e:
            driver = url.drivername
            installed = False
            if driver == 'sqlite':
                raise ModuleError(self,
                                  "Python was built without sqlite3 support")
            elif (driver == 'mysql' or
                    driver == 'drizzle'): # drizzle is a variant of MySQL
                installed = install({
                        'pip': 'mysql-python',
                        'linux-debian': 'python-mysqldb',
                        'linux-ubuntu': 'python-mysqldb',
                        'linux-fedora': 'MySQL-python'})
            elif (driver == 'postgresql' or
                    driver == 'postgre'):   # deprecated alias
                installed = install({
                        'pip': 'psycopg2',
                        'linux-debian':'python-psycopg2',
                        'linux-ubuntu':'python-psycopg2',
                        'linux-fedora':'python-psycopg2'})
            elif driver == 'firebird':
                installed = install({
                        'pip': 'fdb',
                        'linux-fedora':'python-fdb'})
            elif driver == 'mssql' or driver == 'sybase':
                installed = install({
                        'pip': 'pyodbc',
                        'linux-debian':'python-pyodbc',
                        'linux-ubuntu':'python-pyodbc',
                        'linux-fedora':'pyodbc'})
            elif driver == 'oracle':
                installed = install({
                        'pip': 'cx_Oracle'})
            else:
                raise ModuleError(self,
                                  "SQLAlchemy couldn't connect: %s" %
                                  debug.format_exception(e))
            if not installed:
                raise ModuleError(self,
                                  "Failed to install required driver")
            try:
                engine = create_engine(url)
            except Exception, e:
                raise ModuleError(self,
                                  "Couldn't connect to the database: %s" %
                                  debug.format_exception(e))
        except SQLAlchemyError:
            # This is NoSuchModuleError in newer versions of SQLAlchemy but we
            # want compatibility here
            raise ModuleError(
                    self,
                    "SQLAlchemy has no support for protocol %r -- are you "
                    "sure you spelled that correctly?" % url.drivername)

        self.set_output('connection', engine.connect())


class SQLSource(Module):
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.sql.widgets:SQLSourceConfigurationWidget')
    _input_ports = [('connection', '(DBConnection)'),
                    ('cacheResults', '(basic:Boolean)'),
                    ('source', '(basic:String)')]
    _output_ports = [('result', '(org.vistrails.vistrails.tabledata:Table)'),
                     ('resultSet', '(basic:List)')]

    def is_cacheable(self):
        return False

    def compute(self):
        cached = False
        if self.has_input('cacheResults'):
            cached = self.get_input('cacheResults')
            self.is_cacheable = lambda: cached
        connection = self.get_input('connection')
        inputs = dict((k, self.get_input(k)) for k in self.inputPorts.iterkeys()
                  if k not in ('source', 'connection', 'cacheResults'))
        s = urllib.unquote(str(self.get_input('source')))

        try:
            transaction = connection.begin()
            results = connection.execute(s, inputs)
            try:
                rows = results.fetchall()
            except Exception:
                self.set_output('result', None)
                self.set_output('resultSet', None)
            else:
                # results.returns_rows is True
                # We don't use 'if return_rows' because this attribute didn't
                # use to exist
                table = TableObject.from_dicts(rows, results.keys())
                self.set_output('result', table)
                self.set_output('resultSet', rows)
            transaction.commit()
        except SQLAlchemyError, e:
            raise ModuleError(self, debug.format_exception(e))


_modules = [DBConnection, SQLSource]


def handle_module_upgrade_request(controller, module_id, pipeline):
    # Before 0.0.3, SQLSource's resultSet output was type ListOfElements (which
    #   doesn't exist anymore)
    # In 0.0.3, SQLSource's resultSet output was type List
    # In 0.1.0, SQLSource's output was renamed to result and is now a Table;
    #   this is totally incompatible and no upgrade code is possible
    #   the resultSet is kept for now for compatibility

    # Up to 0.0.4, DBConnection would ask for a password if one was necessary;
    #   this behavior has not been kept. There is now a password input port, to
    #   which you can connect a PasswordDialog from package dialogs if needed

    old_module = pipeline.modules[module_id]
    # DBConnection module from before 0.1.0: automatically add the password
    # prompt module
    if (old_module.name == 'DBConnection' and
            versions_increasing(old_module.version, '0.1.0')):
        reg = get_module_registry()
        # Creates the new module
        new_module = controller.create_module_from_descriptor(
                reg.get_descriptor(DBConnection))
        # Create the password module
        mod_desc = reg.get_descriptor_by_name(
                'org.vistrails.vistrails.dialogs', 'PasswordDialog')
        mod = controller.create_module_from_descriptor(mod_desc)
        # Adds a 'label' function to the password module
        ops = [('add', mod)]
        ops.extend(controller.update_function_ops(mod,
                                                  'label', ['Server password']))
        # Connects the password module to the new module
        conn = controller.create_connection(mod, 'result',
                                            new_module, 'password')
        ops.append(('add', conn))
        # Replaces the old module with the new one
        upgrade_actions = UpgradeWorkflowHandler.replace_generic(
                controller, pipeline,
                old_module, new_module,
                src_port_remap={'self': 'connection'})
        password_fix_action = create_action(ops)
        return upgrade_actions + [password_fix_action]

    return UpgradeWorkflowHandler.attempt_automatic_upgrade(
            controller, pipeline,
            module_id)


###############################################################################

import unittest


class TestSQL(unittest.TestCase):
    def test_query_sqlite3(self):
        """Queries a SQLite3 database.
        """
        import os
        import sqlite3
        import tempfile
        import urllib2
        from vistrails.tests.utils import execute, intercept_results
        identifier = 'org.vistrails.vistrails.sql'

        test_db_fd, test_db = tempfile.mkstemp(suffix='.sqlite3')
        os.close(test_db_fd)
        try:
            conn = sqlite3.connect(test_db)
            cur = conn.cursor()
            cur.execute('''
                    CREATE TABLE test(name VARCHAR(24) PRIMARY KEY,
                                      lastname VARCHAR(32) NOT NULL,
                                      age INTEGER NOT NULL)
                    ''')
            cur.executemany('''
                    INSERT INTO test(name, lastname, age)
                    VALUES(:name, :lastname, :age)
                    ''',
                    [{'name': 'John', 'lastname': 'Smith', 'age': 25},
                     {'name': 'Lara', 'lastname': 'Croft', 'age': 21}])
            conn.commit()
            conn.close()

            source = ('''
                    INSERT INTO test(name, lastname, age)
                    VALUES(:name, :lastname, :age)
                    ''')

            with intercept_results(DBConnection, 'connection', SQLSource, 'result') as (connection, table):
                self.assertFalse(execute([
                        ('DBConnection', identifier, [
                            ('protocol', [('String', 'sqlite')]),
                            ('db_name', [('String', test_db)]),
                        ]),
                        ('SQLSource', identifier, [
                            ('source', [('String', urllib2.quote(source))]),
                            ('name', [('String', 'Michael')]),
                            ('lastname', [('String', 'Buck')]),
                            ('age', [('Integer', '78')]),
                        ]),
                    ],
                    [
                        (0, 'connection', 1, 'connection'),
                    ],
                    add_port_specs=[
                        (1, 'input', 'name',
                         'org.vistrails.vistrails.basic:String'),
                        (1, 'input', 'lastname',
                         'org.vistrails.vistrails.basic:String'),
                        (1, 'input', 'age',
                         'org.vistrails.vistrails.basic:Integer'),
                    ]))

            self.assertEqual(len(connection), 1)
            connection[0].close()
            self.assertEqual(len(table), 1)
            self.assertIsNone(table[0])

            source = "SELECT name, lastname, age FROM test WHERE age > :age"

            with intercept_results(DBConnection, 'connection', SQLSource, 'result') as (connection, table):
                self.assertFalse(execute([
                        ('DBConnection', identifier, [
                            ('protocol', [('String', 'sqlite')]),
                            ('db_name', [('String', test_db)]),
                        ]),
                        ('SQLSource', identifier, [
                            ('source', [('String', urllib2.quote(source))]),
                            ('age', [('Integer', '22')]),
                        ]),
                    ],
                    [
                        (0, 'connection', 1, 'connection'),
                    ],
                    add_port_specs=[
                        (1, 'input', 'age',
                         'org.vistrails.vistrails.basic:Integer'),
                    ]))

            self.assertEqual(len(connection), 1)
            connection[0].close()
            self.assertEqual(len(table), 1)
            table, = table
            self.assertEqual(table.names, ['name', 'lastname', 'age'])
            self.assertEqual((table.rows, table.columns), (2, 3))
            self.assertEqual(set(table.get_column(1)),
                             set(['Smith', 'Buck']))
        finally:
            try:
                os.remove(test_db)
            except OSError:
                pass # Oops, we are leaking the file here...
