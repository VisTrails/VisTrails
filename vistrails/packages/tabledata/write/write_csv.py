from __future__ import division

from itertools import izip

from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, ModuleError

from ..common import Table


class WriteCSV(Module):
    """Writes a table to a CSV file.

    You can use the 'delimiter' and 'write_header' ports to choose the format
    you want. By default, the file will include a single-line header if the
    table has column names, and will use semicolon separators (';').
    """
    _input_ports = [
            ('table', Table),
            ('delimiter', '(org.vistrails.vistrails.basic:String',
             {'optional': True, 'defaults': "[';']"}),
            ('write_header', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True})]
    _output_ports = [('file', '(org.vistrails.vistrails.basic:File)')]

    @staticmethod
    def write(fname, table, delimiter=';', write_header=True):
        with open(fname, 'w') as fp:
            if write_header and table.names is not None:
                fp.write(delimiter.join(table.names) + '\n')

            cols = [table.get_column(i) for i in xrange(table.columns)]
            line = 0
            for l in izip(*cols):
                fp.write(delimiter.join(str(e) for e in l) + '\n')
                line += 1

        return line

    def compute(self):
        table = self.getInputFromPort('table')
        delimiter = self.getInputFromPort('delimiter')
        fileobj = self.interpreter.filePool.create_file(suffix='.csv')
        fname = fileobj.name

        with open(fname, 'w') as fp:
            write_header = self.forceGetInputFromPort('write_header')
            if write_header is not False:
                if table.names is None:
                    if write_header is True:  # pragma: no cover
                        raise ModuleError(
                                self,
                                "write_header is set but the table doesn't "
                                "have column names")

            if not table.columns:
                raise ModuleError(
                        self,
                        "Table has no columns")

            nb_lines = self.write(fname, table, delimiter,
                                  write_header is not False)

            rows = table.rows
            if nb_lines != rows:  # pragma: no cover
                debug.warning("WriteCSV wrote %d lines instead of expected "
                              "%d" % (nb_lines, rows))

        self.setResult('file', fileobj)


_modules = [WriteCSV]
