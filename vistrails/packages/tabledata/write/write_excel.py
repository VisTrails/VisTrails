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
                             'linux-fedora': 'python-xlwt'},
                         True)
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
