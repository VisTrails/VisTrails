###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
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

"""URL provides modules to download files via the network.

It can refer to HTTP and FTP files, which enables workflows to be distributed
without its associated data.

This package uses a local cache, inside the per-user VisTrails directory. This
way, files that haven't been changed do not need to be downloaded again. The
check is performed efficiently using HTTP headers.
"""

from __future__ import division

import os
import urllib
import urllib2

try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

from vistrails.core.application import is_running_gui
from vistrails.core.configuration import get_vistrails_persistent_configuration
from vistrails.core import debug
import vistrails.core.modules.basic_modules
from vistrails.core.modules.basic_modules import PathObject
import vistrails.core.modules.module_registry
from vistrails.core.modules.vistrails_module import Module, ModuleError

from vistrails.core.repository.poster.encode import multipart_encode
from vistrails.core.repository.poster.streaminghttp import register_openers

from vistrails.packages.URL.init import cache_filename, package_directory


class RepoSync(Module):
    """ VisTrails Server version of RepoSync modules. Customized to play
    nicely with crowdlabs. Needs refactoring.

    RepoSync enables data to be synced with a online repository. The designated file
    parameter will be uploaded to the repository on execution,
    creating a new pipeline version that links to online repository data.
    If the local file isn't available, then the online repository data is used.
    """

    def __init__(self):
        Module.__init__(self)

        config = get_vistrails_persistent_configuration()
        if config.check('webRepositoryURL'):
            self.base_url = config.webRepositoryURL
        else:
            raise ModuleError(self,
                              ("No webRepositoryURL value defined"
                               " in the Expert Configuration"))

        # check if we are running in server mode
        # this effects how the compute method functions
        if config.check('isInServerMode'):
            self.is_server = bool(config.isInServerMode)
        else:
            self.is_server = False

        # TODO: this '/' check should probably be done in core/configuration.py
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]

    # used for invaliding cache when user isn't logged in to crowdLabs
    # but wants to upload data
    def invalidate_cache(self):
        return False

    def validate_cache(self):
        return True

    def _file_is_in_local_cache(self, local_filename):
        return os.path.isfile(local_filename)

    def checksum_lookup(self):
        """ checks if the repository has the wanted data """

        checksum_url = "%s/datasets/exists/%s/" % (self.base_url,
                                                   self.checksum)
        self.on_server = False
        try:
            check_dataset_on_repo = urllib2.urlopen(url=checksum_url)
            self.up_to_date = True if \
                    check_dataset_on_repo.read() == 'uptodate' else False
            self.on_server = True
        except urllib2.HTTPError:
            self.up_to_date = True

    def data_sync(self):
        """ downloads/uploads/uses the local file depending on availability """
        self.checksum_lookup()

        # local file not on repository, so upload
        if not self.on_server and os.path.isfile(self.in_file.name):
            cookiejar = None
            if is_running_gui():
                import vistrails.gui.repository
                cookiejar = vistrails.gui.repository.QRepositoryDialog.cookiejar
            if cookiejar:
                register_openers(cookiejar=cookiejar)

                params = {'dataset_file': open(self.in_file.name, 'rb'),
                          'name': self.in_file.name.split('/')[-1],
                          'origin': 'vistrails',
                          'checksum': self.checksum}

                upload_url = "%s/datasets/upload/" % self.base_url

                datagen, headers = multipart_encode(params)
                request = urllib2.Request(upload_url, datagen, headers)
                try:
                    result = urllib2.urlopen(request)
                    if result.code != 200:
                        debug.warning("Failed to upload data to the "
                                      "repository")
                        # make temporarily uncachable
                        self.is_cacheable = self.invalidate_cache
                    else:
                        debug.log("Push to repository was successful")
                        # make sure module caches
                        self.is_cacheable = self.validate_cache
                except Exception, e:
                    debug.warning("Failed to upload data to the repository")
                    # make temporarily uncachable
                    self.is_cacheable = self.invalidate_cache
                debug.warning('RepoSync uploaded %s to the repository' % \
                              self.in_file.name)
            else:
                debug.warning("You must be logged into the web repository in "
                              "order to upload data. No data was synced")
                # make temporarily uncachable
                self.is_cacheable = self.invalidate_cache

            # use local data
            self.set_output("file", self.in_file)
        else:
            # file on repository mirrors local file, so use local file
            if self.up_to_date and os.path.isfile(self.in_file.name):
                self.set_output("file", self.in_file)
            else:
                # local file not present or out of date, download or use cache
                self.url = "%s/datasets/download/%s" % (self.base_url,
                                                       self.checksum)
                local_filename = os.path.join(package_directory,
                                              cache_filename(self.url))
                if not self._file_is_in_local_cache(local_filename):
                    # file not in cache, download.
                    try:
                        urllib.urlretrieve(self.url, local_filename)
                    except IOError, e:
                        raise ModuleError(self, ("Invalid URL: %s" % e))
                out_file = PathObject(local_filename)
                debug.warning('RepoSync is using repository data')
                self.set_output("file", out_file)


    def compute(self):
        # if server, grab local file using checksum id
        if self.is_server:
            self.check_input('checksum')
            self.checksum = self.get_input("checksum")
            # get file path
            path_url = "%s/datasets/path/%s/"%(self.base_url, self.checksum)
            dataset_path_request = urllib2.urlopen(url=path_url)
            dataset_path = dataset_path_request.read()

            if os.path.isfile(dataset_path):
                out_file = PathObject(dataset_path)
                self.set_output("file", out_file)
        else: # is client
            self.check_input('file')
            self.in_file = self.get_input("file")
            if os.path.isfile(self.in_file.name):
                # do size check
                size = os.path.getsize(self.in_file.name)
                if size > 26214400:
                    debug.warning("File is too large (>25MB): unable to sync "
                                  "with web repository")
                    self.set_output("file", self.in_file)
                else:
                    # compute checksum
                    f = open(self.in_file.name, 'r')
                    self.checksum = sha_hash()
                    block = 1
                    while block:
                        block = f.read(128)
                        self.checksum.update(block)
                    f.close()
                    self.checksum = self.checksum.hexdigest()

                    # upload/download file
                    self.data_sync()

                    # set checksum param in module
                    if not self.has_input('checksum'):
                        self.change_parameter('checksum', [self.checksum])

            else:
                # local file not present
                if self.has_input('checksum'):
                    self.checksum = self.get_input("checksum")

                    # download file
                    self.data_sync()


def initialize(*args, **keywords):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    basic = vistrails.core.modules.basic_modules

    reg.add_module(RepoSync)
    reg.add_input_port(RepoSync, "file", (basic.File, 'File'))
    reg.add_input_port(RepoSync, "checksum",
                       (basic.String, 'Checksum'), optional=True)
    reg.add_output_port(RepoSync, "file", (basic.File,
                                           'Repository Synced File object'))
    reg.add_output_port(RepoSync, "checksum",
                        (basic.String, 'Checksum'), optional=True)
