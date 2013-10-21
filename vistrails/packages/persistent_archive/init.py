from file_archive import FileStore
import os

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.system import current_dot_vistrails

from .common import set_default_store, PersistentHash
from .cache import CachedPath, CachedFile, CachedDir
from .queries import QueryCondition, EqualString, EqualInt, IntInRange, \
    Metadata
from .persistedinput import PersistedInputPath, \
    PersistedInputFile, PersistedInputDir
from .queriedinput import QueriedInputPath, QueriedInputFile, QueriedInputDir
from .persistedoutput import PersistedPath, PersistedFile, PersistedDir

file_archive = py_import('file_archive', {
        'pip': 'file_archive'})


def initialize():
    if configuration.check('file_store'):
        file_store_path = configuration.file_store
    else:
        file_store_path = os.path.join(current_dot_vistrails(), 'file_archive')
    if not os.path.exists(file_store_path) or not os.listdir(file_store_path):
        FileStore.create_store(file_store_path)
    set_default_store(FileStore(file_store_path))


_modules = {
        '': [
            # Reference to a specific file
            PersistentHash,

            # Caching modules
            (CachedPath, {'abstract': True}),
            CachedFile,
            CachedDir,

            # Input modules
            (PersistedInputPath, {'abstract': True}),
            PersistedInputFile,
            PersistedInputDir,

            # Query modules
            (QueriedInputPath, {'abstract': True}),
            QueriedInputFile,
            QueriedInputDir,

            # Output modules
            (PersistedPath, {'abstract': True}),
            PersistedFile,
            PersistedDir,
        ],
        'metadata': [
            # Condition & metadata modules
            (QueryCondition, {'abstract': True}),
            (Metadata, {'abstract': True}),
            EqualString,
            EqualInt,
            IntInRange,
        ],
    }


def menu_items():
    from ui import show_viewer
    return [("Show archive content", show_viewer)]
