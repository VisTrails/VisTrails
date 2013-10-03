import os

from vistrails.core.modules.basic_modules import Path, Boolean, Directory, File
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TIME, get_default_store
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

        self._set_result(entry)

    def _set_result(self, entry):
        if os.path.isdir(entry.filename):
            r = Directory()
        else:
            r = File()
        r.name = entry.filename
        self.setResult('path', r)
        # TODO : output metadata


class QueriedInputFile(QueriedInputPath):
    _output_ports = [
            ('path', File)]


class QueriedInputDir(QueriedInputPath):
    _output_ports = [
            ('path', Directory)]
