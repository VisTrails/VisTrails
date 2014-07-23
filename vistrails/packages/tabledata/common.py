try:
    import numpy
except ImportError: # pragma: no cover
    numpy = None

from vistrails.core.modules.basic_modules import List, ListType
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.output_modules import OutputModule, FileMode
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    Converter


class InternalModuleError(Exception):
    """Track ModuleError in subclasses."""

    def raise_module_error(self, module_obj):
        raise ModuleError(module_obj, self.message)


class TableObject(object):
    columns = None # the number of columns in the table
    rows = None # the number of rows in the table
    names = None # the names of the columns
    name = None # a name for the table (useful for joins, etc.)

    def __init__(self, columns, nb_rows, names):
        self.columns = len(columns)
        self.rows = nb_rows
        self.names = names

        self._columns = columns

    def get_column(self, i, numeric=False): # pragma: no cover
        """Gets a column from the table as a list or numpy array.

        If numeric=False (the default), the data is returned 'as-is'. It might
        either be bytes (=str), unicode or number (int, long, float).

        If numeric=True, the data is returned as a numpy array if numpy is
        available, or as a list of floats.
        """
        if numeric and numpy is not None:
            return numpy.array(self._columns[i], dtype=numpy.float32)
        else:
            return self._columns[i]

    def get_column_by_name(self, name, numeric=False):
        """Gets a column from its name.

        This convenience methods looks up the right column index if names are
        available and calls get_column().

        You shouldn't need to override this method, get_column() should be
        sufficient.
        """
        try:
            col = self.names.index(name)
        except ValueError:
            raise KeyError(name)
        else:
            return self.get_column(col, numeric)

    @classmethod
    def from_dicts(cls, dicts, keys=None):
        iterator = iter(dicts)
        try:
            first = next(iterator)
        except StopIteration:
            if keys is None:
                raise ValueError("No entry in sequence")
            return cls([[]] * len(keys), 0, list(keys))
        if keys is None:
            keys = first.keys()
        columns = [[first[key]] for key in keys]
        count = 1
        for dct in iterator:
            for i, key in enumerate(keys):
                try:
                    v = dct[key]
                except KeyError:
                    raise ValueError("Entry %d has no key %r" % (count, key))
                else:
                    columns[i].append(v)
            count += 1
        return cls(columns, count, keys)


class Table(Module):
    _input_ports = [('name', '(org.vistrails.vistrails.basic:String)')]
    _output_ports = [('value', 'Table')]

    def set_output(self, port_name, value):
        if self.list_depth == 0 and value is not None and port_name == 'value':
            if value.name is None:
                value.name = self.force_get_input('name', None)
        Module.set_output(self, port_name, value)


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


class ExtractColumn(Module):
    """Gets a single column from a table, as a list.

    Specifying one of 'column_name' or 'column_index' is sufficient; if you
    provide both, the module will check that the column has the expected name.
    """
    _input_ports = [
            ('table', Table),
            ('column_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('column_index', '(org.vistrails.vistrails.basic:Integer)',
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
        except ValueError, e:
            raise ModuleError(self, e.message)

        self.set_output('value', table.get_column(
                column_idx,
                self.get_input('numeric', allow_default=True)))


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

class TableToFileMode(FileMode):
    formats = ['html']
    def write_html(self, table):
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

    def compute_output(self, output_module, configuration=None):
        value = output_module.get_input("value")
        filename = self.get_filename(configuration, suffix='.html')
        with open(filename, 'wb') as fp:
            fp.write(self.write_html(value))

class TableOutput(OutputModule):
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    _input_ports = [('value', 'Table')]
    _output_modes = [TableToFileMode]

_modules = [(Table, {'abstract': True}), ExtractColumn, BuildTable,
            (SingleColumnTable, {'hide_descriptor': True}),
            TableOutput]
