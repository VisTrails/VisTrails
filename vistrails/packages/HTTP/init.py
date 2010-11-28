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
"""HTTP provides packages for HTTP-based file fetching. This provides
a location-independent way of referring to files. This package uses a
local cache of the files, inside the per-user VisTrails
directory. This way, files that haven't been changed do not need
downloading. The check is performed efficiently using the HTTP GET
headers.
"""


from PyQt4 import QtGui
from core.modules.vistrails_module import ModuleError
from core.configuration import get_vistrails_persistent_configuration
from gui.utils import show_warning
import core.modules.vistrails_module
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system
from core import debug
import gui.repository
import httplib
import urllib2
import os.path
import sys
import socket
import datetime
import urllib

import hashlib
# special file uploaders used to push files to repository
from core.repository.poster.encode import multipart_encode
from core.repository.poster.streaminghttp import register_openers

package_directory = None

class MyURLopener(urllib.FancyURLopener):
    """ Custom URLopener that enables urllib.urlretrieve to catch 404 errors"""
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        if errcode == 404:
            raise IOError, ('http error', errcode, errmsg, headers)
        # call parent method 
        urllib.FancyURLopener().http_error_default(url, fp, errcode,
                                                   errmsg, headers)

urllib._urlopener = MyURLopener()

###############################################################################

class HTTP(core.modules.vistrails_module.Module):
    pass

class HTTPFile(HTTP):
    """ Downloads file from URL """

    def is_cacheable(self):
        self.checkInputPort('url')
        url = self.getInputFromPort("url")
        self._parse_url(url)
        local_filename = self._local_filename(url)
        return self._file_is_in_local_cache(local_filename)
            
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
        
        request = urllib2.Request(url)
        try:
            f1 = opener.open(url)
        except urllib2.URLError, e:
            if self._file_is_in_local_cache(local_filename):
                debug.warning(('A network error occurred. HTTPFile will use'
                                ' cached version of file'))
                result = core.modules.basic_modules.File()
                result.name = local_filename
                return (1, result, local_filename)
            else:
                return (2, (str(e)), local_filename)
        except urllib2.HTTPError, e:
            return (2,(str(e)), local_filename)
        else:
            mod_header = f1.info().getheader('last-modified')
            content_type = f1.info().getmaintype()
             
            result = core.modules.basic_modules.File()
            result.name = local_filename

            if (not self._file_is_in_local_cache(local_filename) or
                not mod_header or
                self._is_outdated(mod_header, local_filename)):
                try:
                    # For binary files on windows the mode has to be 'wb'
                    if content_type in ['application', 
                                        'audio', 
                                        'image', 
                                        'video']:
                        mode = 'wb'
                    else:
                        mode = 'w'
                    f2 = open(local_filename, mode)
                    f2.write(f1.read())
                    f2.close()
                    f1.close()

                except IOError, e:
                    return (2, ("Invalid URL: %s" % e), local_filename)
                except:
                    return (2, ("Could not create local file '%s'" %
                                             local_filename), local_filename)
            result.name = local_filename
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

class RepoSync(HTTP):
    """ VisTrails Server version of RepoSync modules. Customized to play 
    nicely with crowdlabs. Needs refactoring.

    RepoSync enables data to be synced with a online repository. The designated file
    parameter will be uploaded to the repository on execution,
    creating a new pipeline version that links to online repository data.
    If the local file isn't available, then the online repository data is used.
    """

    def __init__(self):
        HTTP.__init__(self)
        self.base_url = \
                get_vistrails_persistent_configuration().webRepositoryURL

        # TODO: this '/' check should probably be done in core/configuration.py
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]

    def compute(self):
        self.checkInputPort('checksum')
        self.checksum = self.getInputFromPort("checksum")
        # get file path
        path_url = "%s/datasets/path/%s/"%(self.base_url, self.checksum)
        print path_url
        try:
            dataset_path_request = urllib2.urlopen(url=path_url)
            dataset_path = dataset_path_request.read()
        except urllib2.HTTPError:
            pass

        if os.path.isfile(dataset_path):
            out_file = core.modules.basic_modules.File()
            out_file.name = dataset_path
            #print out_file.name
            self.setResult("file", out_file)

def initialize(*args, **keywords):
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules

    reg.add_module(HTTP, abstract=True)
    reg.add_module(HTTPFile)
    reg.add_input_port(HTTPFile, "url", (basic.String, 'URL'))
    reg.add_output_port(HTTPFile, "file", (basic.File, 'local File object'))
    reg.add_output_port(HTTPFile, "local_filename",
                        (basic.String, 'local filename'), optional=True)

    reg.add_module(RepoSync)
    reg.add_input_port(RepoSync, "file", (basic.File, 'File'))
    reg.add_input_port(RepoSync, "checksum",
                       (basic.String, 'Checksum'), optional=True)
    reg.add_output_port(RepoSync, "file", (basic.File,
                                           'Repository Synced File object'))
    reg.add_output_port(RepoSync, "checksum",
                        (basic.String, 'Checksum'), optional=True)

    global package_directory
    package_directory = core.system.default_dot_vistrails() + "/HTTP"

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

import unittest


class TestHTTPFile(unittest.TestCase):

    class DummyView(object):
        def set_module_active(self, id):
            pass
        def set_module_computing(self, id):
            pass
        def set_module_success(self, id):
            pass
        def set_module_error(self, id, error):
            pass

    def testParseURL(self):
        foo = HTTPFile()
        foo._parse_url('http://www.sci.utah.edu/~cscheid/stuff/vtkdata-5.0.2.zip')
        self.assertEquals(foo.host, 'www.sci.utah.edu')
        self.assertEquals(foo.filename, '/~cscheid/stuff/vtkdata-5.0.2.zip')

    def testIncorrectURL(self):
        from core.db.locator import XMLFileLocator
        import core.vistrail
        from core.vistrail.module import Module
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam
        import core.interpreter
        p = core.vistrail.pipeline.Pipeline()
        m_param = ModuleParam(type='String',
                              val='http://illbetyouthisdoesnotexistohrly',
                              )
        m_function = ModuleFunction(name='url',
                                    parameters=[m_param],
                                    )
        p.add_module(Module(name='HTTPFile',
                           package=identifier,
                           id=0,
                           functions=[m_function],
                           ))
        interpreter = core.interpreter.default.get_default_interpreter()
        kwargs = {'locator': XMLFileLocator('foo'),
                  'current_version': 1L,
                  'view': self.DummyView(),
                  }
        interpreter.execute(p, **kwargs)

    def testIncorrectURL_2(self):
        import core.vistrail
        from core.db.locator import XMLFileLocator
        from core.vistrail.module import Module
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam
        import core.interpreter
        p = core.vistrail.pipeline.Pipeline()
        m_param = ModuleParam(type='String',
                              val='http://neitherodesthisohrly',
                              )
        m_function = ModuleFunction(name='url',
                                    parameters=[m_param],
                                    )
        p.add_module(Module(name='HTTPFile',
                           package=identifier,
                           id=0,
                           functions=[m_function],
                           ))
        interpreter = core.interpreter.default.get_default_interpreter()
        kwargs = {'locator': XMLFileLocator('foo'),
                  'current_version': 1L,
                  'view': self.DummyView(),
                  }
        interpreter.execute(p, **kwargs)

if __name__ == '__main__':
    unittest.main()
