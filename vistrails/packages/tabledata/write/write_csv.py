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

    def compute(self):
        table = self.get_input('table')
        delimiter = self.get_input('delimiter')
        fileobj = self.interpreter.filePool.create_file(suffix='.csv')
        fname = fileobj.name

        with open(fname, 'w') as fp:
            write_header = self.force_get_input('write_header')
            if write_header is not False:
                if table.names is None:
                    if write_header is True: # pragma: no cover
                        raise ModuleError(
                                self,
                                "write_header is set but the table doesn't "
                                "have column names")
                else:
                    fp.write(delimiter.join(table.names) + '\n')

            cols = [iter(table.get_column(i)) for i in xrange(table.columns)]

            if not cols:
                raise ModuleError(
                        self,
                        "Table has no columns")

            line = 0
            for l in izip(*cols):
                fp.write(delimiter.join(str(e) for e in l) + '\n')
                line += 1

            rows = table.rows
            if line != rows: # pragma: no cover
                debug.warning("WriteCSV wrote %d lines instead of expected "
                              "%d" % (line, rows))

        self.set_output('file', fileobj)


_modules = [WriteCSV]
