try:
    import numpy
except ImportError:
    numpy = None

from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError

class InternalModuleError(Exception):
    """Track ModuleError in subclasses."""

    def raise_module_error(self, module_obj):
        raise ModuleError(module_obj, self.message)

class TableObject(object):
    columns = None # the number of columns in the table
    rows = None # the number of rows in the table
    names = None # the names of the columns
    name = None # a name for the table (useful for joins, etc.)

    def get_column(self, i, numeric=False): # pragma: no cover
        raise NotImplementedError


class Table(Module):
    _input_ports = [('name', '(org.vistrails.vistrails.basic:String)')]
    _output_ports = [('value', 'Table')]

    def set_output(self, port_name, value):
        if port_name == 'value':
            if value.name is None:
                value.name = self.force_get_input('name', None)
        Module.set_output(self, port_name, value)

class ExtractColumn(Module):
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
        if self.has_input('column_index'):
            column_index = self.get_input('column_index')
        if self.has_input('column_name'):
            name = self.get_input('column_name')
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            if table.names is None:
                raise ModuleError("Unable to get column by names: table "
                                  "doesn't have column names")
            try:
                index = table.names.index(name)
            except ValueError:
                try:
                    name = name.strip()
                    index = table.column_names.index(name)
                except:
                    raise ModuleError(self, "Column name was not found")
            if self.has_input('column_index'):
                if column_index != index:
                    raise ModuleError(self,
                                      "Both column_name and column_index were "
                                      "specified, and they don't agree")
        elif self.has_input('column_index'):
            index = column_index
        else:
            raise ModuleError(self,
                              "You must set one of column_name or "
                              "column_index")

        result = table.get_column(
                index,
                numeric=self.get_input('numeric', allow_default=True))

        self.set_output('value', result)


class BuiltTable(TableObject):
    def __init__(self, columns, nb_rows, names):
        self.columns = len(columns)
        self.rows = nb_rows
        self.names = names

        self._columns = columns

    def get_column(self, i, numeric=False):
        if numeric and numpy is not None:
            return numpy.array(self._columns[i], dtype=numpy.float32)
        else:
            return self._columns[i]


class BuildTable(Module):
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.tabledata.widgets:BuildTableWidget')
    _output_ports = [('value', Table)]

    def __init__(self):
        Module.__init__(self)
        self.input_ports_order = []

    def compute(self):
        items = None
        if self.input_ports_order:
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

        self.set_output('value', BuiltTable(cols, nb_rows, names))


_modules = [(Table, {'abstract': True}), ExtractColumn, BuildTable]
