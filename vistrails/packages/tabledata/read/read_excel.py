import numpy

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.vistrails_module import ModuleError

from ..common import Table


def get_xlrd():
    try:
        return py_import('xlrd', {
                'pip': 'xlrd',
                'linux-debian': 'python-xlrd',
                'linux-ubuntu': 'python-xlrd',
                'linux-fedora': 'python-xlrd'})
    except ImportError:
        return None


class ExcelSpreadsheet(Table):
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('sheet_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('sheet_index', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:String)'),
            ('self', '(org.vistrails.vistrails.tabledata:'
             'read|ExcelSpreadsheet)')]

    def compute(self):
        xlrd = get_xlrd()
        if xlrd is None:
            raise ModuleError(self, "xlrd is not available")

        workbook = self.getInputFromPort('file')
        workbook = xlrd.open_workbook(workbook.name)

        if self.hasInputFromPort('sheet_index'):
            sheet_index = self.getInputFromPort('sheet_index')
        if self.hasInputFromPort('sheet_name'):
            name = self.getInputFromPort('sheet_name')
            try:
                index = workbook.sheet_names().index(name)
            except:
                raise ModuleError(self, "Sheet name not found")
            if self.hasInputFromPort('sheet_index'):
                if sheet_index != index:
                    raise ModuleError(self,
                                      "Both sheet_name and sheet_index were "
                                      "specified, and they don't agree")
        elif self.hasInputFromPort('sheet_index'):
            index = sheet_index
        else:
            raise ModuleError(self,
                              "You must set one of sheet_name or sheet_index")
        self.sheet = workbook.sheet_by_index(index)

        self.header_present = self.getInputFromPort('header_present')
        if self.header_present:
            self.names = [c.value for c in self.sheet.row(0)]
            self.setResult('column_names', self.names)
        else:
            self.names = None

        self.rows = self.sheet.nrows
        if self.header_present:
            self.rows -= 1

        self.columns = self.sheet.ncols
        self.setResult('column_count', self.columns)

        self.column_cache = {}

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        result = [c.value for c in self.sheet.col(index)]
        if self.header_present:
            result = result[1:]
        if numeric:
            result = numpy.array(result, dtype=numpy.float32)

        self.column_cache[(index, numeric)] = result
        return result


_modules = [ExcelSpreadsheet]
