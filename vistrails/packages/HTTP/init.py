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
"""HTTP provides packages for HTTP-based file fetching. This provides
a location-independent way of referring to files. This package uses a
local cache of the files, inside the per-user VisTrails
directory. This way, files that haven't been changed do not need
downloading. The check is performed efficiently using the HTTP GET
headers.
"""
from vistrails.core.modules.vistrails_module import ModuleError
from vistrails.core.configuration import get_vistrails_persistent_configuration
from vistrails.gui.utils import show_warning
from vistrails.core.modules.vistrails_module import Module
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
from vistrails.core import debug
from vistrails.core.system import current_dot_vistrails
import vistrails.gui.repository

import datetime
import email.utils
import hashlib
import os.path
import sys
import unittest
import urllib
import urllib2

from vistrails.core.repository.poster.encode import multipart_encode
from vistrails.core.repository.poster.streaminghttp import register_openers

from vistrails.core.utils import DummyView

from http_directory import download_directory

# special file uploaders used to push files to repository

package_directory = None

###############################################################################

class HTTPFile(Module):
    """ Downloads file from URL """

    def compute(self):
        self.checkInputPort('url')
        url = self.getInputFromPort("url")
        (result, downloaded_file, local_filename) = self.download(url)
        self.setResult("local_filename", local_filename)
        if result == 2:
            raise ModuleError(self, downloaded_file)
        else:
            self.setResult("file", downloaded_file)

    def download(self, url):
        """download(url:string) -> (result: int, downloaded_file: File,
                                    local_filename:string)
        Tries to download a file from url. It returns a tuple with:
        result: 0 -> success
                1 -> couldn't download the file, but found a cached version
                2 -> failed (in this case downloaded_file will contain the 
                             error message)
        downloaded_file: The downloaded file or the error message in case it
                         failed
                         
        local_filename: the path to the local_filename
        
        """
        
        self._parse_url(url)

        opener = urllib2.build_opener()

        local_filename = self._local_filename(url)

        # Get ETag from disk
        try:
            with open(local_filename + '.etag') as etag_file:
                etag = etag_file.read()
        except IOError:
            etag = None

        try:
            request = urllib2.Request(url)
            if etag is not None:
                request.add_header(
                    'If-None-Match',
                    etag)
            try:
                mtime = email.utils.formatdate(os.path.getmtime(local_filename),
                                               usegmt=True)
                request.add_header(
                    'If-Modified-Since',
                    mtime)
            except OSError:
                pass
            f1 = opener.open(request)
        except urllib2.URLError, e:
            if isinstance(e, urllib2.HTTPError) and e.code == 304:
                # Not modified
                result = vistrails.core.modules.basic_modules.File()
                result.name = local_filename
                return (0, result, local_filename)
            if self._file_is_in_local_cache(local_filename):
                debug.warning('A network error occurred. HTTPFile will use a '
                              'cached version of the file')
                result = vistrails.core.modules.basic_modules.File()
                result.name = local_filename
                return (1, result, local_filename)
            else:
                return (2, (str(e)), local_filename)
        else:
            try:
                mod_header = f1.headers['last-modified']
            except KeyError:
                mod_header = None
            try:
                size_header = f1.headers['content-length']
                if not size_header:
                    raise ValueError
                size_header = int(size_header)
            except (KeyError, ValueError):
                size_header = None

            result = vistrails.core.modules.basic_modules.File()
            result.name = local_filename

            if (not self._file_is_in_local_cache(local_filename) or
                    not mod_header or
                    self._is_outdated(mod_header, local_filename)):
                try:
                    dl_size = 0
                    CHUNKSIZE = 4096
                    f2 = open(local_filename, 'wb')
                    while True:
                        if size_header is not None:
                            self.logging.update_progress(
                                    self,
                                    dl_size*1.0/size_header)
                        chunk = f1.read(CHUNKSIZE)
                        if not chunk:
                            break
                        dl_size += len(chunk)
                        f2.write(chunk)
                    f2.close()
                    f1.close()

                except Exception, e:
                    try:
                        os.unlink(local_filename)
                    except OSError:
                        pass
                    return (2, ("Error retrieving URL: %s" % e), local_filename)
            result.name = local_filename

            # Save ETag
            try:
                etag = f1.headers['ETag']
            except KeyError:
                pass
            else:
                with open(local_filename + '.etag', 'w') as etag_file:
                    etag = etag_file.write(etag)

            return (0, result, local_filename)
        
    ##########################################################################

    def _parse_url(self, url):
        s = url.split('/')
        try:
            self.host = s[2]
            self.filename = '/' + '/'.join(s[3:])
        except:
            raise ModuleError(self, "Malformed URL: %s" % url)

    def _is_outdated(self, remoteHeader, localFile):
        """Checks whether local file is outdated."""
        local_time = \
                datetime.datetime.utcfromtimestamp(os.path.getmtime(localFile))
        try:
            remote_time = datetime.datetime.strptime(remoteHeader,
                                                     "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            try:
                remote_time = datetime.datetime.strptime(remoteHeader,
                                                         "%a, %d %B %Y %H:%M:%S %Z")
            except ValueError:
                # unable to parse last-modified header, download file again
                debug.warning("Unable to parse Last-Modified header"
                              ", downloading file")
                return True
        return remote_time > local_time

    def _file_is_in_local_cache(self, local_filename):
        return os.path.isfile(local_filename)

    def _local_filename(self, url):
        return package_directory + '/' + urllib.quote_plus(url)


class HTTPDirectory(Module):
    """Downloads a whole directory recursively from a URL
    """

    def compute(self):
        self.checkInputPort('url')
        url = self.getInputFromPort('url')
        local_path = self.download(url)
        self.setResult('local_path', local_path)
        local_dir = vistrails.core.modules.basic_modules.Directory()
        local_dir.name = local_path
        self.setResult('directory', local_dir)

    def download(self, url):
        local_path = self.interpreter.filePool.create_directory(
                prefix='vt_http').name
        download_directory(url, local_path)
        return local_path


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

        checksum_url = "%s/datasets/exists/%s/" % (self.base_url, self.checksum)
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
                        show_warning("Upload Failure",
                                     "Data failed to upload to repository")
                        # make temporarily uncachable
                        self.is_cacheable = self.invalidate_cache
                    else:
                        debug.warning("Push to repository was successful")
                        # make sure module caches
                        self.is_cacheable = self.validate_cache
                except Exception, e:
                    show_warning("Upload Failure",
                                 "Data failed to upload to repository")
                    # make temporarily uncachable
                    self.is_cacheable = self.invalidate_cache
                debug.warning('RepoSync uploaded %s to the repository' % \
                              self.in_file.name)
            else:
                show_warning("Please login", ("You must be logged into the web"
                                              " repository in order to upload "
                                              "data. No data was synced"))
                # make temporarily uncachable
                self.is_cacheable = self.invalidate_cache

            # use local data
            self.setResult("file", self.in_file)
        else:
            # file on repository mirrors local file, so use local file
            if self.up_to_date and os.path.isfile(self.in_file.name):
                self.setResult("file", self.in_file)
            else:
                # local file not present or out of date, download or used cached
                self.url = "%s/datasets/download/%s" % (self.base_url,
                                                       self.checksum)
                local_filename = package_directory + '/' + \
                        urllib.quote_plus(self.url)
                if not self._file_is_in_local_cache(local_filename):
                    # file not in cache, download.
                    try:
                        urllib.urlretrieve(self.url, local_filename)
                    except IOError, e:
                        raise ModuleError(self, ("Invalid URL: %s" % e))
                out_file = vistrails.core.modules.basic_modules.File()
                out_file.name = local_filename
                debug.warning('RepoSync is using repository data')
                self.setResult("file", out_file)


    def compute(self):
        # if server, grab local file using checksum id
        if self.is_server:
            self.checkInputPort('checksum')
            self.checksum = self.getInputFromPort("checksum")
            # get file path
            path_url = "%s/datasets/path/%s/"%(self.base_url, self.checksum)
            try:
                dataset_path_request = urllib2.urlopen(url=path_url)
                dataset_path = dataset_path_request.read()
            except urllib2.HTTPError:
                pass

            if os.path.isfile(dataset_path):
                out_file = vistrails.core.modules.basic_modules.File()
                out_file.name = dataset_path
                self.setResult("file", out_file)
        else: # is client
            self.checkInputPort('file')
            self.in_file = self.getInputFromPort("file")
            if os.path.isfile(self.in_file.name):
                # do size check
                size = os.path.getsize(self.in_file.name)
                if size > 26214400:
                    show_warning("File is too large", ("file is larger than 25MB, "
                                 "unable to sync with web repository"))
                    self.setResult("file", self.in_file)
                else:
                    # compute checksum
                    f = open(self.in_file.name, 'r')
                    self.checksum = hashlib.sha1()
                    block = 1
                    while block:
                        block = f.read(128)
                        self.checksum.update(block)
                    f.close()
                    self.checksum = self.checksum.hexdigest()

                    # upload/download file
                    self.data_sync()

                    # set checksum param in module
                    if not self.hasInputFromPort('checksum'):
                        self.change_parameter('checksum', [self.checksum])

            else:
                # local file not present
                if self.hasInputFromPort('checksum'):
                    self.checksum = self.getInputFromPort("checksum")

                    # download file
                    self.data_sync()

def initialize(*args, **keywords):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    basic = vistrails.core.modules.basic_modules

    reg.add_module(HTTPFile)
    reg.add_input_port(HTTPFile, "url", (basic.String, 'URL'))
    reg.add_output_port(HTTPFile, "file", (basic.File, 'local File object'))
    reg.add_output_port(HTTPFile, "local_filename",
                        (basic.String, 'local filename'), optional=True)

    reg.add_module(HTTPDirectory)
    reg.add_input_port(HTTPDirectory, 'url', (basic.String, "URL"))
    reg.add_output_port(HTTPDirectory, 'directory',
                        (basic.Directory, "local Directory object"))
    reg.add_output_port(HTTPDirectory, 'local_path',
                        (basic.String, "local path"), optional=True)

    reg.add_module(RepoSync)
    reg.add_input_port(RepoSync, "file", (basic.File, 'File'))
    reg.add_input_port(RepoSync, "checksum",
                       (basic.String, 'Checksum'), optional=True)
    reg.add_output_port(RepoSync, "file", (basic.File,
                                           'Repository Synced File object'))
    reg.add_output_port(RepoSync, "checksum",
                        (basic.String, 'Checksum'), optional=True)

    global package_directory
    dotVistrails = current_dot_vistrails()
    package_directory = os.path.join(dotVistrails, "HTTP")

    if not os.path.isdir(package_directory):
        try:
            debug.log("Creating HTTP package directory: %s" % package_directory)
            os.mkdir(package_directory)
        except:
            debug.critical(("Create directory failed. Make sure '%s' does not"
                           " exist and parent directory is writable") %
                            package_directory)
            sys.exit(1)

##############################################################################


class TestHTTPFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from vistrails.core.packagemanager import get_package_manager
        from vistrails.core.modules.module_registry import MissingPackage
        pm = get_package_manager()
        try:
            pm.get_package('org.vistrails.vistrails.http')
        except MissingPackage:
            pm.late_enable_package('HTTP')

    def testParseURL(self):
        foo = HTTPFile()
        foo._parse_url('http://www.sci.utah.edu/~cscheid/stuff/vtkdata-5.0.2.zip')
        self.assertEquals(foo.host, 'www.sci.utah.edu')
        self.assertEquals(foo.filename, '/~cscheid/stuff/vtkdata-5.0.2.zip')

    def testIncorrectURL(self):
        from vistrails.tests.utils import execute
        self.assertTrue(execute([
                ('HTTPFile', identifier, [
                    ('url', [('String', 'http://idbetthisdoesnotexistohrly')]),
                ]),
            ]))

    def testIncorrectURL_2(self):
        from vistrails.tests.utils import execute
        self.assertTrue(execute([
                ('HTTPFile', identifier, [
                    ('url', [('String', 'http://neitherodesthisohrly')]),
                ]),
            ]))

class TestHTTPDirectory(unittest.TestCase):
    def test_download(self):
        url = 'http://www.vistrails.org/testing/httpdirectory/test/'

        import shutil
        import tempfile
        testdir = tempfile.mkdtemp(prefix='vt_test_http_')
        try:
            download_directory(url, testdir)
            files = {}
            def addfiles(dirpath):
                td = os.path.join(testdir, dirpath)
                for name in os.listdir(td):
                    filename = os.path.join(testdir, dirpath, name)
                    dn = os.path.join(dirpath, name)
                    if os.path.isdir(filename):
                        addfiles(os.path.join(dirpath, name))
                    else:
                        with open(filename, 'rb') as f:
                            files[dn.replace(os.sep, '/')] = f.read()
            addfiles('')
            self.assertEqual(len(files), 4)
            del files['f.html']
            self.assertEqual(files, {
                    'a': 'aa\n',
                    'bb': 'bb\n',
                    'cc/d': 'dd\n',
                })
        finally:
            shutil.rmtree(testdir)

if __name__ == '__main__':
    unittest.main()
