############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from core import debug
import os
import core.configuration
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
        conf = core.configuration.get_vistrails_configuration()
        if conf.check('userPackageDirectory'):
            self._upd = conf.userPackageDirectory
        else:
            self._upd = conf.get('dotVistrails') + '/.userpackages/'

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
            f = file(os.path.join(self._path, codepath, 'MANIFEST'))
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
                fout = file(name, 'w')
                fin = urllib2.urlopen(self._path + '/' + codepath + '/' + l)
                fout.write(fin.read()) # There should be a better way to do this
                fin.close()
                fout.close()
                self.copy_file(codepath, l, name)
                os.unlink(name)

##############################################################################

_repository = None
def get_repository():
    global _repository
    if _repository:
        return _repository
    import core.configuration
    conf = core.configuration.get_vistrails_configuration()
    if conf.check('repositoryHTTPURL'):
        _repository = HTTPPackageRepository(conf.repositoryHTTPURL)
        debug.log("Using HTTP Package Repository @ %s" % conf.repositoryHTTPURL)
    elif conf.check('repositoryLocalPath'):
        _repository = LocalPackageRepository(conf.repositoryLocalPath)
        debug.log("Using Local Repository @ %s" % conf.repositoryLocalPath)
    else:
        _repository = None
    return _repository
