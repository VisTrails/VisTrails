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
# Utilities for user-defined Modules
import os
import tempfile
from vistrails.core.modules import basic_modules
from vistrails.core.system import link_or_copy
from vistrails.core.utils import VistrailsInternalError
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core import debug

import unittest

################################################################################

class FilePool(object):

    """FilePool provides a convenient interface for Module developers to
    use temporary files.

    """
    
    def __init__(self):
        d = {'prefix':'vt_tmp'}
        if get_vistrails_configuration().check('temporaryDir'):
            dir = get_vistrails_configuration().temporaryDir
            if os.path.exists(dir):
                d['dir'] = dir
            else:
                debug.critical("Temporary directory does not exist: %s" % dir)

        self.directory = tempfile.mkdtemp(**d)
        self.files = {}
        
    def cleanup(self):
        """cleanup() -> None

        Cleans up the file pool, by removing all temporary files and
        the directory they existed in. Module developers should never
        call this directly.

        """
        if not os.path.isdir(self.directory):
            # cleanup has already happened
            return
        try:
            for root, dirs, files in os.walk(self.directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.directory)
        except OSError, e:
            debug.unexpected_exception(e)
            raise VistrailsInternalError("Can't remove %s: %s" %
                                         (self.directory,
                                          debug.format_exception(e)))

    def create_file(self, suffix = '', prefix = 'vt_tmp'):
        """create_file(suffix='', prefix='vt_tmp') -> PathObject.

        Returns a File module representing a writable file for use in
        modules. To avoid race conditions, this file will already
        exist in the file system.

        """
        (fd, name) = tempfile.mkstemp(suffix=suffix,
                                      prefix=prefix,
                                      dir=self.directory)
        os.close(fd)
        result = basic_modules.PathObject(name)
        self.files[name] = result
        return result

    def create_directory(self, suffix = '', prefix = 'vt_tmp'):
        """create_directory(suffix='', prefix='vt_tmp') -> PathObject.

        Returns a writable directory for use in modules. To avoid race
        conditions, this directory will already exist in the file system.

        """
        name = tempfile.mkdtemp(suffix=suffix,
                                      prefix=prefix,
                                      dir=self.directory)
        result = basic_modules.PathObject(name)
        self.files[name] = result
        return result

    def guess_suffix(self, file_name):
        """guess_suffix(file_name) -> String.
        Tries to guess the suffix of the given filename.
        
        """
        return os.path.splitext(file_name)[1]

    def make_local_copy(self, src):
        """make_local_copy(src) -> PathObject

        Returns a file in the filePool that's either a link or a copy
        of the given file path. This ensures the file's longevity when
        necessary. Since it might use a hardlink for speed, modules
        should only use this method if the file is not going to be
        changed in the future.

        """
        (fd, name) = tempfile.mkstemp(suffix=self.guess_suffix(src),
                                      dir=self.directory)
        os.close(fd)
        # FIXME: Watch out for race conditions
        os.unlink(name)
        link_or_copy(src, name)
        result = basic_modules.PathObject(name)
        self.files[name] = result
        return result
        
################################################################################


class TestFilePool(unittest.TestCase):

    def test_guess_suffix(self):
        """Tests FilePool.guess_suffix"""
        x = FilePool()
        self.assertEquals(x.guess_suffix('asd.foo'), '.foo')
        self.assertEquals(x.guess_suffix('bar'), '')
        self.assertEquals(x.guess_suffix('./lalala'), '')
        self.assertEquals(x.guess_suffix('./lalala.bar'), '.bar')
        self.assertEquals(x.guess_suffix('user.foo/lalala'), '')
        x.cleanup()
        del x

    def test_double_cleanup(self):
        x = FilePool()
        x.cleanup()
        try:
            x.cleanup()
        except VistrailsInternalError:
            self.fail("cleanup failed")

if __name__ == '__main__':
    unittest.main()
