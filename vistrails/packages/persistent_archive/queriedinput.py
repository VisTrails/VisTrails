from __future__ import division

import os

from vistrails.core.modules.basic_modules import Boolean, Directory, File, \
    Integer, List, Path, PathObject
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TIME, get_default_store
from .queries import QueryCondition


class QueriedInputPath(Module):
    """Searches for files using a query.

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
        conditions = self.get_input_list('query')
        conditions = dict(c.condition for c in conditions)

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
    _output_ports = [
            OPort('most_recent', File),
            OPort('results', List),
            OPort('count', Integer, optional=True)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class QueriedInputDir(QueriedInputPath):
    _output_ports = [
            OPort('most_recent', Directory),
            OPort('results', List),
            OPort('count', Integer, optional=True)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
