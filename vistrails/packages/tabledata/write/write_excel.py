from vistrails.core.bundles.pyimport import py_import
from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, ModuleError

from ..common import Table


def get_xlwt():
    try:
        return py_import('xlwt', {
                'pip': 'xlwt',
                'linux-debian': 'python-xlwt',
                'linux-ubuntu': 'python-xlwt',
                'linux-fedora': 'python-xlwt'})
    except ImportError: # pragma: no cover
        return None


class WriteExcelSpreadsheet(Module):
    """Writes a table to an Excel spreadsheet file.
    """
    _input_ports = [('table', Table)]
    _output_ports = [('file', '(org.vistrails.vistrails.basic:File)')]

    def compute(self):
        table = self.get_input('table')
        rows = table.rows

        xlwt = get_xlwt()
        if xlwt is None: # pragma: no cover
            raise ModuleError(self, "xlwt is not available")

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Sheet1')

        fileobj = self.interpreter.filePool.create_file(suffix='.xls')
        fname = fileobj.name

        for c in xrange(table.columns):
            column = table.get_column(c)
            for r, e in enumerate(column):
                sheet.write(r, c, e)
            if r+1 != rows: # pragma: no cover
                debug.warning("WriteExcelSpreadsheet wrote %d lines instead "
                              "of expected %d" % (r, rows))

        workbook.save(fname)
        self.set_output('file', fileobj)


_modules = [WriteExcelSpreadsheet]
