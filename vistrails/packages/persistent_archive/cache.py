from datetime import datetime
import os

from vistrails.core.modules.basic_modules import Directory, File, Path
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_CACHED, KEY_TIME, KEY_SIGNATURE, \
    get_default_store, wrap_path


class CachedPath(Module):
    """Uses the file store as a cache.

    Stores the path in the cache along with the module signature, so it can be
    retrieved in a later execution of the same pipeline.

    This is very similar to PersistentIntermediatePath except it doesn't record
    more metadata than what's required for caching.
    """

    _input_ports = [
            IPort('path', Path)]
    _output_ports = [
            OPort('path', Path)]

    _cached = None

    def updateUpstream(self):
        if not hasattr(self, 'signature'):
            raise ModuleError(self, "Module has no signature")
        file_store = get_default_store()
        entries = file_store.query({KEY_SIGNATURE: self.signature})
        best = None
        for entry in entries:
            if best is None or entry[KEY_TIME] > best[KEY_TIME]:
                best = entry
        if best is not None:
            self._cached = best.filename
        else:
            super(CachedPath, self).updateUpstream()

    def compute(self):
        if self._cached is not None:
            self._set_result(self._cached)
        else:
            file_store = get_default_store()
            newpath = self.get_input('path').name
            self.check_path_type(newpath)
            metadata = {
                    KEY_TYPE: TYPE_CACHED,
                    KEY_TIME: datetime.strftime(datetime.utcnow(),
                                                '%Y-%m-%d %H:%M:%S'),
                    KEY_SIGNATURE: self.signature}
            entry = file_store.add(newpath, metadata)
            self.annotate({'added_file': entry['hash']})
            self._set_result(entry.filename)

    def check_path_type(self, path):
        pass

    def _set_result(self, path):
        self.set_output('path', wrap_path(path))


class CachedFile(CachedPath):
    _input_ports = [
            IPort('path', File)]
    _output_ports = [
            OPort('path', File)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class CachedDir(CachedPath):
    _input_ports = [
            IPort('path', Directory)]
    _output_ports = [
            OPort('path', Directory)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
