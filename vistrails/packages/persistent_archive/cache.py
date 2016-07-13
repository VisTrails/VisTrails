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
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_CACHED, KEY_TIME, KEY_SIGNATURE, \
    get_default_store


class CachedPath(Module):
    """Uses the file store as a cache.

    Stores the path in the cache along with the module signature, so it can be
    retrieved in a later execution of the same pipeline.

    This is very similar to PersistedPath except it doesn't record more
    metadata than what's required for caching.
    """

    _input_ports = [
            IPort('path', Path)]
    _output_ports = [
            OPort('path', Path)]

    _cached = None

    def update_upstream(self):
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
            super(CachedPath, self).update_upstream()

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
        self.set_output('path', PathObject(path))


class CachedFile(CachedPath):
    """Uses the file store as a cache.

    Stores the file in the cache along with the module signature, so it can be
    retrieved in a later execution of the same pipeline.

    This is very similar to PersistedFile except it doesn't record more
    metadata than what's required for caching.
    """

    _input_ports = [
            IPort('path', File)]
    _output_ports = [
            OPort('path', File)]

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class CachedDir(CachedPath):
    """Uses the file store as a cache.

    Stores the directory in the cache along with the module signature, so it
    can be retrieved in a later execution of the same pipeline.

    This is very similar to PersistedDir except it doesn't record more metadata
    than what's required for caching.
    """

    _input_ports = [
            IPort('path', Directory)]
    _output_ports = [
            OPort('path', Directory)]

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
