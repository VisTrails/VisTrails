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

from file_archive import FileStore
import os

from vistrails.core.system import current_dot_vistrails

from .common import set_default_store, PersistentHash
from .cache import CachedPath, CachedFile, CachedDir
from .queries import QueryCondition, EqualString, EqualInt, IntInRange, \
    Metadata
from .persistedinput import PersistedInputPath, \
    PersistedInputFile, PersistedInputDir
from .queriedinput import QueriedInputPath, QueriedInputFile, QueriedInputDir
from .persistedoutput import PersistedPath, PersistedFile, PersistedDir


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
