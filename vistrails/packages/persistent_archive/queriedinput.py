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

import os

from vistrails.core.modules.basic_modules import Boolean, Directory, File, \
    Integer, List, Path, PathObject
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TIME, get_default_store
from .queries import QueryCondition


class QueriedInputPath(Module):
    """Base class for file-querying modules.

    This uses QueryConditions instead of Metadata, allowing for more complex
    queries than what PersistedInputPath provides (equality in metadata).
    """

    _input_ports = [
            IPort('query', QueryCondition),
            IPort('unique', Boolean, optional=True, default='False')]
    # TODO: Order by more conditions than only `vistrails_timestamp`
    _output_ports = [
            OPort('most_recent', Path),
            OPort('results', List),
            OPort('count', Integer, optional=True)]
    # TODO: Set query from `configure_widget`

    def compute(self):
        # Do the query
        queries = self.get_input_list('query')
        conditions = {}
        for c in conditions:
            conditions.update(c.conditions)

        file_store = get_default_store()

        nb = 0
        best = None
        entries = list(file_store.query(conditions))
        for entry in entries:
            nb += 1
            self.check_path_type(entry.filename)
            if best is None or (KEY_TIME in entry.metadata and
                    KEY_TIME in best.metadata and
                    entry[KEY_TIME] > best[KEY_TIME]):
                best = entry

        if best is None:
            raise ModuleError(self, "No match")

        if nb > 1 and self.get_input('unique'):
            raise ModuleError(self,
                              "Query returned %d results and 'unique' is "
                              "True" % nb)

        self._set_result(entries, best)

    def check_path_type(self, path):
        pass

    def _set_result(self, results, latest):
        self.set_output('most_recent', PathObject(latest.filename))
        self.set_output('results', [PathObject(e.filename)
                                   for e in results])
        self.set_output('count', len(results))
        # TODO : output metadata


class QueriedInputFile(QueriedInputPath):
    """Searches for files using a query.

    This uses QueryConditions instead of Metadata, allowing for more complex
    queries than what PersistedInputFile provides (equality in metadata).
    """

    _output_ports = [
            OPort('most_recent', File),
            OPort('results', List),
            OPort('count', Integer, optional=True)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class QueriedInputDir(QueriedInputPath):
    """Searches for directories using a query.

    This uses QueryConditions instead of Metadata, allowing for more complex
    queries than what PersistedInputDir provides (equality in metadata).
    """

    _output_ports = [
            OPort('most_recent', Directory),
            OPort('results', List),
            OPort('count', Integer, optional=True)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
