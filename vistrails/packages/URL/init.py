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

"""URL provides modules to download files via the network.

It can refer to HTTP and FTP files, which enables workflows to be distributed
without its associated data.

This package uses a local cache, inside the per-user VisTrails directory. This
way, files that haven't been changed do not need to be downloaded again. The
check is performed efficiently using HTTP headers.
"""

from datetime import datetime
import email.utils
import hashlib
import os
import urllib
import urllib2

from vistrails.core.configuration import get_vistrails_persistent_configuration
from vistrails.core import debug
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.system import current_dot_vistrails, strptime
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
import vistrails.gui.repository
from vistrails.gui.utils import show_warning

from vistrails.core.repository.poster.encode import multipart_encode
from vistrails.core.repository.poster.streaminghttp import register_openers

from .http_directory import download_directory
from .https_if_available import build_opener


package_directory = None


###############################################################################

class Downloader(object):
    def __init__(self, url, module, insecure):
        self.url = url
        self.module = module
        self.opener = build_opener(insecure=insecure)

    def execute(self):
        """ Tries to download a file from url.

        Returns the path to the local file.
        """
        self.local_filename = os.path.join(package_directory,
                                           urllib.quote_plus(self.url))

        # Before download
        self.pre_download()

        # Send request
        try:
            response = self.send_request()
        except urllib2.URLError, e:
            if self.is_in_local_cache:
                debug.warning("A network error occurred. DownloadFile will "
                              "use a cached version of the file")
                return self.local_filename
            else:
                raise ModuleError(
                        self.module,
                        "Network error: %s" % debug.format_exception(e))
        if response is None:
            return self.local_filename

        # Read response headers
        self.size_header = None
        if not self.read_headers(response):
            return self.local_filename

        # Download
        self.download(response)

        # Post download
        self.post_download(response)

        return self.local_filename

    def pre_download(self):
        pass

    def send_request(self):
        return self.opener.open(self.url)

    def read_headers(self, response):
        return True

    def download(self, response):
        try:
            dl_size = 0
            CHUNKSIZE = 4096
            f2 = open(self.local_filename, 'wb')
            while True:
                if self.size_header is not None:
                    self.module.logging.update_progress(
                            self.module,
                            dl_size*1.0/self.size_header)
                chunk = response.read(CHUNKSIZE)
                if not chunk:
                    break
                dl_size += len(chunk)
                f2.write(chunk)
            f2.close()
            response.close()

        except Exception, e:
            try:
                os.unlink(self.local_filename)
            except OSError:
                pass
            raise ModuleError(
                    self.module,
                    "Error retrieving URL: %s" % debug.format_exception(e))

    def post_download(self, response):
        pass

    @property
    def is_in_local_cache(self):
        return os.path.isfile(self.local_filename)


class HTTPDownloader(Downloader):
    def pre_download(self):
        # Get ETag from disk
        try:
            with open(self.local_filename + '.etag') as etag_file:
                self.etag = etag_file.read()
        except IOError:
            self.etag = None

    def send_request(self):
        try:
            request = urllib2.Request(self.url)
            if self.etag is not None:
                request.add_header(
                    'If-None-Match',
                    self.etag)
            try:
                mtime = email.utils.formatdate(
                        os.path.getmtime(self.local_filename),
                        usegmt=True)
                request.add_header(
                    'If-Modified-Since',
                    mtime)
            except OSError:
                pass
            return self.opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 304:
                # Not modified
                return None
            raise

    def read_headers(self, response):
        try:
            self.mod_header = response.headers['last-modified']
        except KeyError:
            self.mod_header = None
        try:
            size_header = response.headers['content-length']
            if not size_header:
                raise ValueError
            self.size_header = int(size_header)
        except (KeyError, ValueError):
            self.size_header = None
        return True

    def _is_outdated(self):
        local_time = datetime.utcfromtimestamp(
                os.path.getmtime(self.local_filename))
        try:
            remote_time = strptime(self.mod_header,
                                   "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            try:
                remote_time = strptime(self.mod_header,
                                       "%a, %d %B %Y %H:%M:%S %Z")
            except ValueError:
                # unable to parse last-modified header, download file again
                debug.warning("Unable to parse Last-Modified header, "
                              "downloading file")
                return True
        return remote_time > local_time

    def download(self, response):
        if (not self.is_in_local_cache or
                not self.mod_header or self._is_outdated()):
            Downloader.download(self, response)

    def post_download(self, response):
        try:
            etag = response.headers['ETag']
        except KeyError:
            pass
        else:
            with open(self.local_filename + '.etag', 'w') as etag_file:
                etag = etag_file.write(etag)


downloaders = {
    'http': HTTPDownloader,
    'https': HTTPDownloader,
    'ftp': Downloader}


class DownloadFile(Module):
    """ Downloads file from URL.

    This modules uses urllib2 to download a remote file. It uses a cache on the
    filesystem so as to not re-download unchanged files.
    """

    def compute(self):
        self.check_input('url')
        url = self.get_input('url')
        insecure = self.get_input('insecure')
        local_filename = self.download(url, insecure)
        self.set_output('local_filename', local_filename)
        result = vistrails.core.modules.basic_modules.File()
        result.name = local_filename
        self.set_output('file', result)

    def download(self, url, insecure):
        """ Tries to download a file from url.

        Returns the path to the local file.
        """
        scheme = urllib2.splittype(url)[0]
        DL = downloaders.get(scheme, Downloader)
        return DL(url, self, insecure).execute()


class HTTPDirectory(Module):
    """Downloads a whole directory recursively from a URL
    """

    def compute(self):
        self.check_input('url')
        url = self.get_input('url')
        insecure = self.get_input('insecure')
        local_path = self.download(url, insecure)
        self.set_output('local_path', local_path)
        local_dir = vistrails.core.modules.basic_modules.Directory()
        local_dir.name = local_path
        self.set_output('directory', local_dir)

    def download(self, url, insecure):
        local_path = self.interpreter.filePool.create_directory(
                prefix='vt_http').name
        download_directory(url, local_path, insecure)
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
            self.set_output("file", self.in_file)
        else:
            # file on repository mirrors local file, so use local file
            if self.up_to_date and os.path.isfile(self.in_file.name):
                self.set_output("file", self.in_file)
            else:
                # local file not present or out of date, download or use cache
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
                self.set_output("file", out_file)


    def compute(self):
        # if server, grab local file using checksum id
        if self.is_server:
            self.check_input('checksum')
            self.checksum = self.get_input("checksum")
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
                self.set_output("file", out_file)
        else: # is client
            self.check_input('file')
            self.in_file = self.get_input("file")
            if os.path.isfile(self.in_file.name):
                # do size check
                size = os.path.getsize(self.in_file.name)
                if size > 26214400:
                    show_warning("File is too large",
                                 "file is larger than 25MB, "
                                 "unable to sync with web repository")
                    self.set_output("file", self.in_file)
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
                    if not self.has_input('checksum'):
                        self.change_parameter('checksum', [self.checksum])

            else:
                # local file not present
                if self.has_input('checksum'):
                    self.checksum = self.get_input("checksum")

                    # download file
                    self.data_sync()


class URLEncode(Module):
    def compute(self):
        value = self.get_input('string')
        self.set_output('encoded', urllib.quote_plus(value))


class URLDecode(Module):
    def compute(self):
        encoded = self.get_input('encoded')
        self.set_output('string', urllib.unquote_plus(encoded))


def initialize(*args, **keywords):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    basic = vistrails.core.modules.basic_modules

    reg.add_module(DownloadFile)
    reg.add_input_port(DownloadFile, "url", (basic.String, 'URL'))
    reg.add_input_port(DownloadFile, 'insecure',
                       (basic.Boolean, "Allow invalid SSL certificates"),
                       optional=True, defaults="['False']")
    reg.add_output_port(DownloadFile, "file",
                        (basic.File, 'local File object'))
    reg.add_output_port(DownloadFile, "local_filename",
                        (basic.String, 'local filename'), optional=True)

    reg.add_module(HTTPDirectory)
    reg.add_input_port(HTTPDirectory, 'url', (basic.String, "URL"))
    reg.add_input_port(HTTPDirectory, 'insecure',
                       (basic.Boolean, "Allow invalid SSL certificates"),
                       optional=True, defaults="['False']")
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

    reg.add_module(URLEncode)
    reg.add_input_port(URLEncode, "string", basic.String)
    reg.add_output_port(URLEncode, "encoded", basic.String)

    reg.add_module(URLDecode)
    reg.add_input_port(URLDecode, "encoded", basic.String)
    reg.add_output_port(URLDecode, "string", basic.String)

    global package_directory
    dotVistrails = current_dot_vistrails()
    package_directory = os.path.join(dotVistrails, "HTTP")

    if not os.path.isdir(package_directory):
        try:
            debug.log("Creating HTTP package directory: %s" % package_directory)
            os.mkdir(package_directory)
        except:
            raise RuntimeError("Failed to create cache directory: %s" %
                               package_directory)


def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {
            # HTTPFile was renamed DownloadFile
            'HTTPFile': [
                (None, '1.0.0', 'DownloadFile', {})
            ],
        }

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)


###############################################################################

import unittest


class TestDownloadFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from vistrails.core.packagemanager import get_package_manager
        from vistrails.core.modules.module_registry import MissingPackage
        pm = get_package_manager()
        try:
            pm.get_package('org.vistrails.vistrails.http')
        except MissingPackage:
            pm.late_enable_package('URL')

    def testIncorrectURL(self):
        from vistrails.tests.utils import execute
        self.assertTrue(execute([
                ('DownloadFile', identifier, [
                    ('url', [('String', 'http://idbetthisdoesnotexistohrly')]),
                ]),
            ]))

    def testIncorrectURL_2(self):
        from vistrails.tests.utils import execute
        self.assertTrue(execute([
                ('DownloadFile', identifier, [
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
