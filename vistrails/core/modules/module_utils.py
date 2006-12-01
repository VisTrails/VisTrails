# Utilities for user-defined Modules

import os
import tempfile
from core.modules import basic_modules
from core.system import link_or_copy
from core.utils import VistrailsInternalError

################################################################################

class FilePool(object):
    
    def __init__(self):
        self.directory = tempfile.mkdtemp(prefix='vt_tmp')
        self.files = {}
        
    def cleanup(self):
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
            raise VistrailsInternalError("Can't remove %s: %s" %
                                         (self.directory,
                                          str(e)))

    def createFile(self, suffix = '', prefix = 'vt_tmp'):
        (fd, name) = tempfile.mkstemp(suffix=suffix,
                                      prefix=prefix,
                                      dir=self.directory)
        os.close(fd)
        result = basic_modules.File()
        result.name = name
        result.upToDate = True
        self.files[name] = result
        return result

    def __del__(self):
        self.cleanup()

    def guess_suffix(self, file_name):
        """Tries to guess the suffix of the given filename."""
        suffix = ''
        # try to guess suffix
        f = file_name.rfind('.')
        if f == -1:
            return ''
        else:
            # It might be a suffix, or it might be a path.  Try to
            # work around path by checking for presence of '/' after
            # suffix delimiter.
            if file_name.rfind('/', f) == -1:
                return file_name[f:]
            else:
                return ''

    def make_local_copy(self, src):
        """Returns a file in the filePool that's either a link or a
        copy of the given file path. This ensures the file's longevity
        when necessary."""
        (fd, name) = tempfile.mkstemp(suffix=self.guess_suffix(src),
                                      dir=self.directory)
        os.close(fd)
        # FIXME: Watch out for race conditions
        os.unlink(name)
        link_or_copy(src, name)
        result = basic_modules.File()
        result.name = name
        result.upToDate = True
        self.files[name] = result
        return result
        
################################################################################

import unittest

class TestFilePool(unittest.TestCase):

    def test_guess_suffix(self):
        """Tests FilePool.guess_suffix"""
        x = FilePool()
        self.assertEquals(x.guess_suffix('asd.foo'), '.foo')
        self.assertEquals(x.guess_suffix('.foo'), '.foo')
        self.assertEquals(x.guess_suffix('bar'), '')
        self.assertEquals(x.guess_suffix('./lalala'), '')
        self.assertEquals(x.guess_suffix('./lalala.bar'), '.bar')

    def test_double_cleanup(self):
        x = FilePool()
        x.cleanup()
        try:
            x.cleanup()
        except VistrailsInternalError:
            self.fail("cleanup failed")

if __name__ == '__main__':
    unittest.main()
