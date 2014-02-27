###############################################################################
##
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

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL
import urllib

from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module

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

        self.set_output('connection', create_engine(url))


class SQLSource(Module):
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.sql.widgets:SQLSourceConfigurationWidget')
    _input_ports = [('connection', '(DBConnection)'),
                    ('cacheResults', '(basic:Boolean)'),
                    ('source', '(basic:String)')]
    _output_ports = [('result', '(org.vistrails.vistrails.tabledata:Table)')]

    def is_cacheable(self):
        return False

    def compute(self):
        cached = False
        if self.has_input('cacheResults'):
            cached = self.get_input('cacheResults')
            self.is_cacheable = lambda: cached
        engine = self.get_input('connection')
        inputs = [self.get_input(k) for k in self.inputPorts.iterkeys()
                  if k not in ('source', 'connection', 'cacheResults')]
        s = urllib.unquote(str(self.get_input('source')))

        connection = engine.connect()
        results = connection.execute(s, inputs)
        table = TableObject.from_dicts((row for row in results), results.keys())
        self.set_output('result', table)
        connection.close()


_modules = [DBConnection, SQLSource]
