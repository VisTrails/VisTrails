import os

from vistrails.core.modules.basic_modules import Boolean, Directory, File, \
    Path
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
            ('path', Path)]

    def compute(self):
        # Do the query
        conditions = self.getInputListFromPort('query')
        conditions = dict(c.condition for c in conditions)

        file_store = get_default_store()

        nb = 0
        best = None
        for entry in file_store.query(conditions):
            nb += 1
            if best is None or (KEY_TIME in entry.metadata and
                    entry[KEY_TIME] > best[KEY_TIME]):
                best = entry

        if best is None:
            raise ModuleError(self, "No match")

        if nb > 1 and self.getInputFromPort('unique'):
            raise ModuleError(self,
                              "Query returned %d results and 'unique' is "
                              "True" % nb)

        self.check_path_type(entry.filename)

        self._set_result(entry)

    def check_path_type(self, path):
        pass

    def _set_result(self, entry):
        self.setResult('path', wrap_path(entry.filename))
        # TODO : output metadata


class QueriedInputFile(QueriedInputPath):
    _output_ports = [
            ('path', File)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class QueriedInputDir(QueriedInputPath):
    _output_ports = [
            ('path', Directory)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
