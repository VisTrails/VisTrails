import os

from vistrails.core.modules.basic_modules import Boolean, Directory, File, \
    Integer, List, Path
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TIME, get_default_store, wrap_path
from .queries import QueryCondition


class QueriedInputPath(Module):
    """Searches for files using a query.

    This uses QueryConditions instead of Metadata, allowing for more complex
    queries than what PersistedInputPath provides (equality in metadata).
    """

    _input_ports = [
            ('query', QueryCondition),
            ('unique', Boolean, {'optional': True, 'defaults': '["False"]'})]
    _output_ports = [
            ('most_recent', Path),
            ('results', List),
            ('count', Integer)]

    def compute(self):
        # Do the query
        conditions = self.getInputListFromPort('query')
        conditions = dict(c.condition for c in conditions)

        file_store = get_default_store()

        nb = 0
        best = None
        entries = list(file_store.query(conditions))
        for entry in entries:
            nb += 1
            self.check_path_type(entry.filename)
            if best is None or (KEY_TIME in entry.metadata and
                    entry[KEY_TIME] > best[KEY_TIME]):
                best = entry

        if best is None:
            raise ModuleError(self, "No match")

        if nb > 1 and self.getInputFromPort('unique'):
            raise ModuleError(self,
                              "Query returned %d results and 'unique' is "
                              "True" % nb)

        self._set_result(entries, entry)

    def check_path_type(self, path):
        pass

    def _set_result(self, results, latest):
        self.setResult('most_recent', wrap_path(latest.filename))
        self.setResult('results', [wrap_path(e.filename)
                                   for e in results])
        self.setResult('count', len(results))
        # TODO : output metadata


class QueriedInputFile(QueriedInputPath):
    _output_ports = [
            ('most_recent', File),
            ('results', List),
            ('count', Integer)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class QueriedInputDir(QueriedInputPath):
    _output_ports = [
            ('most_recent', Directory),
            ('results', List),
            ('count', Integer)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
