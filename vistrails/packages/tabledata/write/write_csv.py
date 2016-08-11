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
        cols = [table.get_column(i) for i in xrange(table.columns)]

        with open(fname, 'w') as fp:
            if write_header and table.names is not None:
                fp.write(delimiter.join(table.names) + '\n')

            line = 0
            for l in izip(*cols):
                fp.write(delimiter.join(str(e) for e in l) + '\n')
                line += 1

        return line

    def compute(self):
        table = self.get_input('table')
        delimiter = self.get_input('delimiter')
        fileobj = self.interpreter.filePool.create_file(suffix='.csv')
        fname = fileobj.name

        with open(fname, 'w') as fp:
            write_header = self.force_get_input('write_header')
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

        self.set_output('file', fileobj)


_modules = [WriteCSV]
