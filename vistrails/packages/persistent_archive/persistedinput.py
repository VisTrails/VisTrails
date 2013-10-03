from datetime import datetime
from file_archive import hash_file, hash_directory
import os

from vistrails.core.modules.basic_modules import Directory, File, Path
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_INPUT, KEY_TIME, KEY_SIGNATURE, \
    get_default_store, PersistentHash
from .queries import Metadata
import vistrails.core.debug as debug


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

            if localpath and os.path.exists(localpath.name):
                path = localpath.name
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
                    if hasattr(self, 'signature'):
                        data[KEY_SIGNATURE] = self.signature
                    data[KEY_TIME] = datetime.strftime(datetime.utcnow(),
                                                       '%Y-%m-%d %H:%M:%S')
                    h = file_store.add(path, data)
                    best = file_store.get(h)
            elif localpath:
                debug.warning("Local file does not exist: %s" % localpath)
            if best is None:
                raise ModuleError(self, "Query returned no file")
            self._set_result(best)
        else:
            raise ModuleError(self,
                              "Missing input: set either 'metadata' "
                              "(optionally with path) or hash")

    def _set_result(self, entry):
        if os.path.isdir(entry.filename):
            r = Directory()
        else:
            r = File()
        r.name = entry.filename
        self.setResult('path', r)
        # TODO : output metadata


class PersistedInputFile(PersistedInputPath):
    _input_ports = [
            ('path', File, True),
            ('metadata', Metadata, True),
            ('hash', PersistentHash, True)]
    _output_ports = [
            ('path', File)]


class PersistedInputDir(PersistedInputPath):
    _input_ports = [
            ('path', Directory, True),
            ('metadata', Metadata, True),
            ('hash', PersistentHash, True)]
    _output_ports = [
            ('path', File)]
