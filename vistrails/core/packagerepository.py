###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
from vistrails.core import debug
import os
import vistrails.core.configuration
from vistrails.core import system
import shutil
import urllib2
import tempfile
import os.path

##############################################################################
# The local codepaths have '.' replaced by '_' because '.' in the names
# of directories that will be used as python libraries confuses the Python
# runtime.

##############################################################################

class PackageRepository(object):

    def __init__(self):
        upd = system.get_vistrails_directory('userPackageDir')
        if upd is not None:
            self._upd = upd
        else:
            conf = vistrails.core.configuration.get_vistrails_configuration()
            self._upd = os.path.join(conf.get('dotVistrails'), '.userpackages')

    def create_main_directory(self, codepath):
        debug.log("Makedir '%s'" % (os.path.join(self._upd, codepath)))
        os.mkdir(os.path.join(self._upd, codepath))

    ##########################################################################

    def create_directory(self, codepath, filename):
        r = os.path.join(self._upd, codepath, filename)
        debug.log("Makedir '%s'" % r)
        os.mkdir(r)

    def copy_file(self, codepath, filename, local_name):
        r = os.path.join(self._upd,
                         codepath, filename)
        debug.log("Copyfile '%s' to '%s'" % (local_name, r))
        shutil.copyfile(local_name, r)

    ##########################################################################
    # implement these

    # def find_package(self, identifier):
    #     pass

    # def install_package(self, identifier):
    #     pass

    ##########################################################################

    class InvalidPackage(Exception):
        pass

##############################################################################

class LocalPackageRepository(PackageRepository):

    def __init__(self, repository_path):
        PackageRepository.__init__(self)
        self._path = repository_path

    def find_package(self, identifier):
        lst = set(os.listdir(self._path))
        codepath = identifier.replace('.', '_')
        if codepath in lst:
            return codepath

    def install_package(self, codepath):
        debug.log("package found!")
        # read manifest
        try:
            f = open(os.path.join(self._path, codepath, 'MANIFEST'))
        except IOError, e:
            raise InvalidPackage("Package is missing manifest.")
        # create directory
        self.create_main_directory(codepath)
        for l in f:
            l = l[:-1]
            if len(l) == 0:
                continue
            file_type = l[0]
            l = l[2:]
            if file_type == 'D':
                self.create_directory(codepath, l)
            elif file_type == 'F':
                self.copy_file(codepath, l, os.path.join(self._path, codepath, l))

##############################################################################

class HTTPPackageRepository(PackageRepository):

    def __init__(self, repository_url):
        PackageRepository.__init__(self)
        self._path = repository_url

    def find_package(self, identifier):
        identifier = identifier.replace('.', '_')
        package_url = self._path + '/' + identifier
        try:
            f = urllib2.urlopen(package_url)
            return identifier
        except urllib2.HTTPError:
            return None

    def install_package(self, codepath):
        debug.log("package found!")
        # read manifest
        try:
            f = urllib2.urlopen(self._path + '/' + codepath + '/MANIFEST')
        except urllib2.HTTPError, e:
            raise InvalidPackage("Package is missing manifest.")
        self.create_main_directory(codepath)
        for l in f:
            l = l[:-1]
            if len(l) == 0:
                continue
            file_type = l[0]
            l = l[2:]
            if file_type == 'D':
                self.create_directory(codepath, l)
            elif file_type == 'F':
                fd, name = tempfile.mkstemp()
                os.close(fd)
                try:
                    fout = open(name, 'w')
                    fin = urllib2.urlopen(self._path + '/' + codepath + '/' + l)
                    fout.write(fin.read()) # There should be a better way to do this
                    fin.close()
                    fout.close()
                    self.copy_file(codepath, l, name)
                finally:
                    os.unlink(name)

##############################################################################

_repository = None
def get_repository():
    global _repository
    if _repository:
        return _repository
    import vistrails.core.configuration
    conf = vistrails.core.configuration.get_vistrails_configuration()
    if conf.check('repositoryHTTPURL'):
        _repository = HTTPPackageRepository(conf.repositoryHTTPURL)
        debug.log("Using HTTP Package Repository @ %s" % conf.repositoryHTTPURL)
    elif conf.check('repositoryLocalPath'):
        _repository = LocalPackageRepository(conf.repositoryLocalPath)
        debug.log("Using Local Repository @ %s" % conf.repositoryLocalPath)
    else:
        _repository = None
    return _repository
