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
import os

from vistrails.core.modules.basic_modules import Directory, File, Path, \
    PathObject
from vistrails.core.modules.config import IPort, OPort, ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_OUTPUT, \
    KEY_SIGNATURE, KEY_TIME, KEY_WORKFLOW, KEY_MODULE_ID, get_default_store
from .queries import Metadata


class PersistedPath(Module):
    """Records a file in the file store.
    """

    _input_ports = [
            IPort('path', Path),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', Path)]

    _cached = None

    def update_upstream(self):
        """A modified version of the update_upstream method.

        Only updates upstream if the file is not found in the store.
        """
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
            super(PersistedPath, self).update_upstream()

    def compute(self):
        if self._cached is not None:
            self._set_result(self._cached)
        else:
            file_store = get_default_store()
            newpath = self.get_input('path').name
            self.check_path_type(newpath)
            metadata = self.get_input_list('metadata')
            metadata = dict(m.metadata for m in metadata)
            metadata[KEY_TYPE] = TYPE_OUTPUT
            metadata[KEY_TIME] = datetime.strftime(datetime.utcnow(),
                                                   '%Y-%m-%d %H:%M:%S')
            metadata[KEY_SIGNATURE] = self.signature
            locator = self.moduleInfo.get('locator')
            if locator is not None:
                metadata[KEY_WORKFLOW] = "%s:%s" % (
                        locator.name,
                        self.moduleInfo['version'])
            metadata[KEY_MODULE_ID] = self.moduleInfo['moduleId']
            entry = file_store.add(newpath, metadata)
            self.annotate({'added_file': entry['hash']})
            self._set_result(entry.filename)

    def check_path_type(self, path):
        pass

    def _set_result(self, path):
        self.set_output('path', PathObject(path))


class PersistedFile(PersistedPath):
    """Records a file in the file store.
    """

    _input_ports = [
            IPort('path', File),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', File)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class PersistedDir(PersistedPath):
    """Records a directory in the file store.
    """

    _input_ports = [
            IPort('path', Directory),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', Directory)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
