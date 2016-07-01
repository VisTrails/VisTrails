###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

from vistrails.core.modules.basic_modules import ListType
from vistrails.core.modules.vistrails_module import ModuleError

from ..common import Table, TableObject, InternalModuleError


class BaseConverter(Table):
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('value', Table)]

    def convert_to_table(self, obj):
        try:
            table = self.make_table(obj)
        except InternalModuleError, e:
            e.raise_module_error(self)
        self.set_output('column_count', table.columns)
        if table.names is not None:
            self.set_output('column_names', table.names)
        self.set_output('value', table)

    @staticmethod
    def add_list(columns, key, value):
        if not isinstance(value, ListType):
            raise InternalModuleError("Entry for key %r is not a list" % key)
        if key is not None:
            value = [key] + value
        for i, v in enumerate(value):
            columns[i].append(v)

    @staticmethod
    def add_dict(columns, keys, key_set, key, value):
        if not isinstance(value, dict):
            raise InternalModuleError(
                    "Entry for key %r is not an object" % key)
        value_keys = set(value.keys())
        m = key_set - value_keys
        if m:
            raise InternalModuleError(
                    "Entry for key %r is missing field %r" % (
                    key,
                    next(iter(m))))
        m = value_keys - key_set
        if m:
            raise InternalModuleError(
                    "Entry for key %r has unexpected field %r" % (
                    key,
                    next(iter(m))))
        if key is None:
            for i, k in enumerate(keys):
                columns[i].append(value[k])
        else:
            columns[0].append(key)
            for i, k in enumerate(keys):
                columns[i + 1].append(value[k])


class BaseDictToTable(BaseConverter):
    _input_ports = [('key_name', '(org.vistrails.vistrails.basic:String)',
                     {'optional': True, 'defaults': repr(["key"])})]

    def make_table(self, obj):
        if not isinstance(obj, dict):
            raise ModuleError(self, "JSON file is not an object")
        key_name = self.get_input('key_name', True)
        iterator = obj.iteritems()
        try:
            first_key, first_value = next(iterator)
        except StopIteration:
            raise ModuleError(self, "No entry in JSON object")
        count = 1
        if isinstance(first_value, ListType):
            keys = None
            columns = [[] for i in xrange(1 + len(first_value))]
            self.add_list(columns, first_key, first_value)
            for key, value in iterator:
                self.add_list(columns, key, value)
                count += 1
        elif isinstance(first_value, dict):
            keys = first_value.keys()
            key_set = set(keys)
            columns = [[] for i in xrange(1 + len(keys))]
            self.add_dict(columns, keys, key_set, first_key, first_value)
            for key, value in iterator:
                self.add_dict(columns, keys, key_set, key, value)
                count += 1
        else:
            raise ModuleError(self, "Values should be lists or objects")

        if keys is not None:
            names = [key_name] + keys
        else:
            names = None
        return TableObject(columns, count, names)


class BaseListToTable(BaseConverter):
    def make_table(self, obj):
        if not isinstance(obj, ListType):
            raise ModuleError(self, "JSON file is not a list")
        iterator = iter(obj)
        try:
            first = next(iterator)
        except StopIteration:
            raise ModuleError(self, "No element in JSON list")
        count = 1
        if isinstance(first, ListType):
            keys = None
            columns = [[] for i in xrange(len(first))]
            self.add_list(columns, None, first)
            for value in iterator:
                self.add_list(columns, None, value)
                count += 1
        elif isinstance(first, dict):
            keys = first.keys()
            key_set = set(keys)
            columns = [[] for i in xrange(len(keys))]
            self.add_dict(columns, keys, key_set, None, first)
            for value in iterator:
                self.add_dict(columns, keys, key_set, None, value)
                count += 1
        else:
            raise ModuleError(self, "Values should be lists or objects")

        return TableObject(columns, count, keys)


class DictToTable(BaseDictToTable):
    """Converts a Python dictionary into a table.

    This is basically the same as read.JSONObject except that it takes a live
    Python dictionary instead of a JSON file.
    """
    _input_ports = [('dict', '(basic:Dictionary)')]

    def compute(self):
        self.convert_to_table(self.get_input('dict'))


class ListToTable(BaseListToTable):
    """Converts a Python list into a table.

    This is basically the same as read.JSONList exept that it takes a live
    Python list instead of a JSON file.
    """
    _input_ports = [('list', '(basic:List)')]

    def compute(self):
        self.convert_to_table(self.get_input('list'))


_modules = [(BaseConverter, {'abstract': True}),
            (BaseDictToTable, {'abstract': True}),
            (BaseListToTable, {'abstract': True}),
            DictToTable, ListToTable]
