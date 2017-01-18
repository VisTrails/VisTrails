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

import pandas
import numpy

from vistrails.core.modules.basic_modules import List, ListType
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.output_modules import OutputModule, FileMode, \
    IPythonMode
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    Converter


class InternalModuleError(Exception):
    """Track ModuleError in subclasses."""

    def raise_module_error(self, module_obj):
        raise ModuleError(module_obj, self.message)


class Series(Module):
    """A pandas.Series object, basically a single column with a row index.
    """
    _input_ports = [('data', '(basic:Array)'),
                    ('index', '(basic:Array)', {'optional': True})]
    _output_ports = [('value', '(Series)')]

    @staticmethod
    def validate(v):
        return isinstance(v, pandas.Series)

    def compute(self):
        self.set_output('value',
                        pandas.Series(self.get_input('data'),
                                      self.force_get_input('index', None)))


def _slice_compute(input_port):
    def compute(self):
        series = self.get_input(input_port)
        from_ = self.force_get_input('from')
        to = self.force_get_input('to')
        stride = self.force_get_input('stride')
        self.set_output('value', series.iloc[from_:to:stride])
    return compute


class SliceSeries(Module):
    """Slice a series.
    """
    _input_ports = [('series', Series),
                    ('from', '(basic:Integer)', {'optional': True}),
                    ('to', '(basic:Integer)', {'optional': True}),
                    ('stride', '(basic:Integer)', {'optional': True})]
    _output_ports = [('value', '(Series)')]

    compute = _slice_compute('series')


class Table(Module):
    """A pandas.DataFrame object, basically a table with hierarchical indexes.
    """


class SliceTable(Module):
    """Slice a table.
    """
    _input_ports = [('table', Table),
                    ('from', '(basic:Integer)', {'optional': True}),
                    ('to', '(basic:Integer)', {'optional': True}),
                    ('stride', '(basic:Integer)', {'optional': True})]
    _output_ports = [('value', '(Series)')]

    compute = _slice_compute('table')


def choose_column(nb_columns, column_names=None, name=None, index=None):
    """Selects a column in a table either by name or index.

    If both are specified, the function will make sure that they represent the
    same column.
    """
    if name is not None:
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        if column_names is None:
            raise ValueError("Unable to get column by name: table doesn't "
                             "have column names")
        try:
            name_index = column_names.index(name)
        except ValueError:
            try:
                name_index = column_names.index(name.strip())
            except ValueError:
                raise ValueError("Column name was not found: %r" % name)
        if index is not None:
            if name_index != index:
                raise ValueError("Both a column name and index were "
                                 "specified, and they don't agree")
        return name_index
    elif index is not None:
        if index < 0 or index >= nb_columns:
            raise ValueError("No column %d, table only has %d columns" % (
                             index, nb_columns))
        return index
    else:
        raise ValueError("No column name nor index specified")


def choose_columns(nb_columns, column_names=None, names=None, indexes=None):
    """Selects a list of columns from a table.

    If both the names and indexes lists are specified, the function will make
    sure that they represent the same list of columns.
    Columns may appear more than once.
    """
    if names is not None:
        if column_names is None:
            raise ValueError("Unable to get column by names: table "
                             "doesn't have column names")
        result = []
        for name in names:
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            try:
                idx = column_names.index(name)
            except ValueError:
                try:
                    idx = column_names.index(name.strip())
                except ValueError:
                    raise ValueError("Column name was not found: %r" % name)
            result.append(idx)
        if indexes is not None:
            if result != indexes:
                raise ValueError("Both column names and indexes were "
                                 "specified, and they don't agree")
        return result
    elif indexes is not None:
        for index in indexes:
            if index < 0 or index >= nb_columns:
                raise ValueError("No column %d, table only has %d columns" % (
                                 index, nb_columns))
        return indexes
    else:
        raise ValueError("No column names nor indexes specified")


class GetColumn(Module):
    """Gets a single column from a table, as a list.

    Specifying one of 'column_name' or 'column_index' is sufficient; if you
    provide both, the module will check that the column has the expected name.
    """
    _input_ports = [
            ('table', Table),
            ('column_index', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('column_num', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('numeric', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['False']"})]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        table = self.get_input('table')
        try:
            column_idx = choose_column(
                    table.columns,
                    column_names=table.names,
                    name=self.force_get_input('column_name', None),
                    index=self.force_get_input('column_index', None))

            self.set_output('value', table.get_column(
                    column_idx,
                    self.get_input('numeric', allow_default=True)))
        except ValueError, e:
            raise ModuleError(self, e.message)


class BuildTable(Module):
    """Builds a table by putting together columns from multiple sources.

    Input can be a mix of lists, which will be used as single columns, and
    whole tables, whose column names will be mangled.
    """
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.tabledata.widgets:BuildTableWidget')
    _output_ports = [('value', Table)]

    def __init__(self):
        Module.__init__(self)
        self.input_ports_order = []

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.input_ports_order = [p.name for p in module.input_port_specs]

    def compute(self):
        items = None
        if self.input_ports_order: # pragma: no branch
            items = [(p, self.get_input(p))
                     for p in self.input_ports_order]
        if not items:
            raise ModuleError(self, "No inputs were provided")

        nb_rows = None
        cols = []
        names = []
        for portname, item in items:
            if isinstance(item, TableObject):
                if nb_rows is not None:
                    if item.rows != nb_rows:
                        raise ModuleError(
                                self,
                                "Different row counts: %d != %d" % (
                                item.rows, nb_rows))
                else:
                    nb_rows = item.rows
                cols.extend(item.get_column(c)
                            for c in xrange(item.columns))
                if item.names is not None:
                    names.extend(item.names)
                else:
                    names.extend("%s col %d" % (portname, i)
                                 for i in xrange(len(cols) - len(names)))
            else:
                if nb_rows is not None:
                    if len(item) != nb_rows:
                        raise ModuleError(
                                self,
                                "Different row counts: %d != %d" % (
                                len(item), nb_rows))
                else:
                    nb_rows = len(item)
                cols.append(item)
                names.append(portname)

        self.set_output('value', TableObject(cols, nb_rows, names))


class SingleColumnTable(Converter):
    """Automatic Converter module from List to Table.
    """
    _input_ports = [('in_value', List)]
    _output_ports = [('out_value', Table)]

    def compute(self):
        column = self.get_input('in_value')
        if not isinstance(column, ListType):
            column = list(column)
        self.set_output('out_value', TableObject(
                [column],               # columns
                len(column),            # nb_rows
                ['converted_list']))    # names


class HtmlRendererMixin(object):
    @staticmethod
    def make_html(table):
        document = ['<!DOCTYPE html>\n'
                    '<html>\n  <head>\n'
                    '    <meta http-equiv="Content-type" content="text/html; '
                            'charset=utf-8" />\n'
                    '    <title>Exported table</title>\n'
                    '    <style type="text/css">\n'
                    'table { border-collapse: collapse; }\n'
                    'td, th { border: 1px solid black; }\n'
                    '    </style>\n'
                    '  </head>\n  <body>\n    <table>\n']
        if table.names is not None:
            names = table.names
        else:
            names = ['col %d' % n for n in xrange(table.columns)]
        document.append('<tr>\n')
        document.extend('  <th>%s</th>\n' % name for name in names)
        document.append('</tr>\n')
        columns = [table.get_column(col) for col in xrange(table.columns)]
        for row in xrange(table.rows):
            document.append('<tr>\n')
            for col in xrange(table.columns):
                elem = columns[col][row]
                if isinstance(elem, bytes):
                    elem = elem.decode('utf-8', 'replace')
                elif not isinstance(elem, unicode):
                    elem = unicode(elem)
                document.append('  <td>%s</td>\n' % elem)
            document.append('</tr>\n')
        document.append('    </table>\n  </body>\n</html>\n')

        return ''.join(document)


class TableToFileMode(FileMode, HtmlRendererMixin):
    formats = ['html', 'csv']

    def write_html(self, table, configuration):
        filename = self.get_filename(configuration, suffix='.html')
        with open(filename, 'wb') as fp:
            fp.write(self.make_html(table))

    def write_csv(self, table, configuration):
        from .write.write_csv import WriteCSV

        filename = self.get_filename(configuration, suffix='.csv')
        WriteCSV.write(filename, table)

    def compute_output(self, output_module, configuration):
        value = output_module.get_input("value")
        format = configuration.get('format', 'html').lower()
        try:
            func = getattr(self, 'write_%s' % format)
        except AttributeError:
            raise AttributeError("TableToFileMode: unknown format %s" % format)
        else:
            func(value, configuration)


class TableToIPythonMode(IPythonMode, HtmlRendererMixin):
    def compute_output(self, output_module, configuration):
        from IPython.core.display import display, HTML

        table = output_module.get_input('value')
        html = self.make_html(table)
        display(HTML(data=html))


class TableOutput(OutputModule):
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    _input_ports = [('value', 'Table')]
    _output_modes = [TableToFileMode, TableToIPythonMode]


_modules = [(Table, {'abstract': True}), ExtractColumn, BuildTable,
            (SingleColumnTable, {'hide_descriptor': True}),
            TableOutput]
