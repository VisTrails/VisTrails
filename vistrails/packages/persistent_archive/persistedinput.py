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

from datetime import datetime
from file_archive import hash_file, hash_directory
import os

import vistrails.core.debug as debug
from vistrails.core.modules.basic_modules import Directory, File, Path, \
    PathObject
from vistrails.core.modules.config import IPort, OPort, ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_INPUT, KEY_TIME, \
    get_default_store, PersistentHash
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
            IPort('path', Path, optional=True),
            IPort('metadata', Metadata, optional=True),
            IPort('hash', PersistentHash, optional=True)]
    _output_ports = [
            OPort('path', Path)]

    def compute(self):
        localpath = self.force_get_input('path')
        hasquery = self.has_input('metadata')
        hashash = self.has_input('hash')

        file_store = get_default_store()

        if hashash:
            if localpath or hasquery:
                raise ModuleError(self,
                                  "Don't set other ports if 'hash' is set")
            h = self.get_input('hash')._hash
            self._set_result(file_store.get(h))
        elif hasquery:
            # Do the query
            metadata = self.get_input_list('metadata')
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
        self.set_output('path', PathObject(entry.filename))
        # TODO : output metadata


class PersistedInputFile(PersistedInputPath):
    """Records or retrieves an external file in the file store.

    Because this class has the same interface for querying an existing file and
    inserting a new one, it uses Metadata instead of QueryCondition for the
    query. This means it only allows equality conditions.
    """

    _input_ports = [
            IPort('path', File, optional=True),
            IPort('metadata', Metadata, optional=True),
            IPort('hash', PersistentHash, optional=True)]
    _output_ports = [
            OPort('path', File)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class PersistedInputDir(PersistedInputPath):
    """Records or retrieves an external directory in the file store.

    Because this class has the same interface for querying an existing
    directory and inserting a new one, it uses Metadata instead of
    QueryCondition for the query. This means it only allows equality
    conditions.
    """

    _input_ports = [
            IPort('path', Directory,  optional=True),
            IPort('metadata', Metadata,  optional=True),
            IPort('hash', PersistentHash,  optional=True)]
    _output_ports = [
            OPort('path', File)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
