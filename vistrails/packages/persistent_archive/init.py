from datetime import datetime
from file_archive import FileStore
import os

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.basic_modules import Constant, Path, String,\
    Directory, File
from vistrails.core.modules.vistrails_module import ModuleError, Module
from vistrails.core.system import current_dot_vistrails

file_archive = py_import('file_archive', {
        'pip': 'file_archive'})


file_store = None
file_store_path = None


def initialize():
    global file_store, file_store_path

    if configuration.check('file_store'):
        file_store_path = configuration.file_store
    else:
        file_store_path = os.path.join(current_dot_vistrails(), 'file_archive')
    if not os.path.exists(file_store_path) or not os.listdir(file_store_path):
        FileStore.create_store(file_store_path)
    file_store = FileStore(file_store_path)


class PersistentHash(Constant):
    """Reference to a specific file.

    Unequivocally references a specific file (by its full hash).
    """
    def __init__(self, h=None):
        Constant.__init__(self)
        if h is not None:
            self._set_hash(h)
        else:
            self._hash = None

    def _set_hash(self, h):
        if not (isinstance(h, basestring)):
            raise TypeError("File hash should be a string")
        elif len(h) != 40:
            raise ValueError("File hash should be 40 characters long")
        if not isinstance(h, str):
            h = str(h)
        self._hash = h

    @staticmethod
    def translate_to_python(h):
        try:
            return PersistentHash(h)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def translate_to_string(ref):
        if ref._hash is not None:
            return ref._hash
        else:
            raise ValueError("Reference is invalid")

    @staticmethod
    def validate(ref):
        return isinstance(ref, PersistentHash)

    def __str__(self):
        return self._hash

    def __repr__(self):
        if self._hash is not None:
            return "<PersistentHash %s>" % self._hash
        else:
            return "<PersistentHash (invalid)>"

    def compute(self):
        if self.hasInputFromPort('value') == self.hasInputFromPort('hash'):
            raise ModuleError(self, "Set either 'value' or 'hash'")
        if self.hasInputFromPort('value'):
            self._hash = self.getInputFromPort('value')._hash
        else:
            try:
                self._set_hash(self.getInputFromPort('hash'))
            except ValueError, e:
                raise ModuleError(self, e.message)
PersistentHash._input_ports = [
        ('value', PersistentHash),
        ('hash', String)]
PersistentHash._output_ports = [
        ('value', PersistentHash)]


KEY_TIME = 'vistrails_timestamp'
KEY_SIGNATURE = 'vistrails_signature'


class CachedPath(Module):
    """Uses the file store as a cache.

    Stores the path in the cache along with the module signature, so it can be
    retrieve in a later execution of the same pipeline.
    """

    _input_ports = [
            ('path', Path)]
    _output_ports = [
            ('path', Path)]

    def __init__(self):
        Module.__init__(self)
        self._cached = None

    def updateUpstream(self):
        if not hasattr(self, 'signature'):
            raise ModuleError(self, "Module has no signature")
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
            newpath = self.getInputFromPort('path').name
            self.check_path_type(newpath)
            metadata = {
                    # FIXME : add date support to file_archive
                    #KEY_TIME: {'type': 'str', 'date': 'utcnow'},
                    KEY_TIME: datetime.strftime(datetime.utcnow(),
                                                '2013-10-01 21:42:49'),
                    KEY_SIGNATURE: self.signature}
            if os.path.isdir(newpath):
                h = file_store.add_directory(newpath, metadata)
            else:
                h = file_store.add_file(newpath, metadata)
            self._set_result(file_store.get_filename(h))

    def check_path_type(self, path):
        pass

    def _set_result(self, path):
        if os.path.isdir(path):
            r = Directory()
        else:
            r = File()
        r.name = path
        self.setResult('path', r)


class CachedFile(CachedPath):
    _input_ports = [
            ('path', File)]
    _output_ports = [
            ('path', File)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class CachedDir(CachedPath):
    _input_ports = [
            ('path', Directory)]
    _output_ports = [
            ('path', Directory)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")


# TODO :
# Use as an input: use PersistentHash or query
# Use as an output: file + dict of metadata
# Intermediate: input+output
    # most recent version of specific value of hardcoded key?


_modules = [PersistentHash,
            (CachedPath, {'abstract': True}),
            CachedFile,
            CachedDir]
