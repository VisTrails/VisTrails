import json
from vistrails.core.modules.vistrails_module import ModuleError

from ..common import TableObject, Table, InternalModuleError

# Currently works for dict-style table:
#    {key1: {name1: val1, name2: val2, ...}, key2: {...}, ...}
# TODO: need to add list-style table 
#    [{name1: val1, name2: val2, ...}, {name1: val1, ...}, ...]

class JSONTable(TableObject):
    def __init__(self, json_file):
        TableObject.__init__(self)
        self.filename = json_file
        self.data = []
        self.read_file()

    def read_file(self):
        with open(self.filename, 'rb') as fp:
            json_d = json.load(fp)
        
            for k, k_dict in json_d.iteritems():
                row_items = k_dict.items()
                row_items.sort()
                new_header, values = zip(*row_items)
                if self.names is None:
                    self.names = new_header
                elif self.names != new_header:
                    raise InternalModuleError(self, 
                                              "JSON Headers do not match")
                self.data.append([k,] + list(values))
        self.names = ['_key'] + list(self.names)
        self.columns = len(self.names)
        self.rows = len(self.data)

    def get_column(self, i, numeric=False): # pragma: no cover
        if numeric:
            return [float(r[i]) for r in self.data]
        return [r[i] for r in self.data]

class JSONFile(Table):
    _input_ports = [('file', '(org.vistrails.vistrails.basic:File)')]
    _output_ports = [('value', 
                      'org.vistrails.vistrails.tabledata:read|JSONFile)')]

    def compute(self):
        json_file = self.get_input('file').name
        try:
            table = JSONTable(json_file)
        except InternalModuleError, e:
            raise e.raise_module_error(self)
        self.set_output('column_count', table.columns)
        self.set_output('column_names', table.names)
        self.set_output('value', table)

_modules = [JSONFile]
