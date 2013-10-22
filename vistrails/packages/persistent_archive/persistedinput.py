from datetime import datetime
from file_archive import hash_file, hash_directory
import os

import vistrails.core.debug as debug
from vistrails.core.modules.basic_modules import Directory, File, Path
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_INPUT, KEY_TIME, \
    get_default_store, wrap_path, PersistentHash
from .queries import Metadata


def hash_path(path):
    if os.path.isdir(path):
        return hash_directory(path)
    else:
        with open(path, 'rb') as fp:
            return hash_file(fp)


class PersistedInputPath(Module):
    """Records or retrieves an external file in the file store.

    Because this class has the same interface for querying an existing file and
    inserting a new one, it uses Metadata instead of QueryCondition for the
    query. This means it only allows equality conditions.
    """

    _input_ports = [
            ('path', Path, True),
            ('metadata', Metadata, True),
            ('hash', PersistentHash, True)]
    _output_ports = [
            ('path', Path)]

    def compute(self):
        localpath = self.forceGetInputFromPort('path')
        hasquery = self.hasInputFromPort('metadata')
        hashash = self.hasInputFromPort('hash')

        file_store = get_default_store()

        if hashash:
            if localpath or hasquery:
                raise ModuleError(self,
                                  "Don't set other ports if 'hash' is set")
            h = self.getInputFromPort('hash')._hash
            self._set_result(file_store.get(h))
        elif hasquery:
            # Do the query
            metadata = self.getInputListFromPort('metadata')
            metadata = dict(m.metadata for m in metadata)
            # Find the most recent match
            best = None
            for entry in file_store.query(metadata):
                if best is None or (KEY_TIME in entry.metadata and
                        entry[KEY_TIME] > best[KEY_TIME]):
                    best = entry
            if best is not None:
                self.check_path_type(best.filename)

            if localpath and os.path.exists(localpath.name):
                path = localpath.name
                self.check_path_type(path)
                if best is not None:
                    # Compare
                    if hash_path(path) != best['hash']:
                        # Record new version of external file
                        use_local = True
                    else:
                        # Recorded version is up to date
                        use_local = False
                else:
                    # No external file: use recorded version
                    use_local = True
                if use_local:
                    data = dict(metadata)
                    data[KEY_TYPE] = TYPE_INPUT
                    data[KEY_TIME] = datetime.strftime(datetime.utcnow(),
                                                       '%Y-%m-%d %H:%M:%S')
                    best = file_store.add(path, data)
                    self.annotate({'added_file': best['hash']})
            elif localpath:
                debug.warning("Local file does not exist: %s" % localpath)
            if best is None:
                raise ModuleError(self, "Query returned no file")
            self._set_result(best)
        else:
            raise ModuleError(self,
                              "Missing input: set either 'metadata' "
                              "(optionally with path) or hash")

    def check_path_type(self, path):
        pass

    def _set_result(self, entry):
        self.setResult('path', wrap_path(entry.filename))
        # TODO : output metadata


class PersistedInputFile(PersistedInputPath):
    _input_ports = [
            ('path', File, True),
            ('metadata', Metadata, True),
            ('hash', PersistentHash, True)]
    _output_ports = [
            ('path', File)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class PersistedInputDir(PersistedInputPath):
    _input_ports = [
            ('path', Directory, True),
            ('metadata', Metadata, True),
            ('hash', PersistentHash, True)]
    _output_ports = [
            ('path', File)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
