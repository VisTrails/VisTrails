# Utilities for user-defined Modules

import os
import tempfile

################################################################################

class FilePool(object):
    
    def __init__(self):
        self.directory = tempfile.mkdtemp(prefix='vt_tmp')
        self.files = {}
        
    def cleanup(self):
        try:
            for root, dirs, files in os.walk(self.directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.directory)
        except OSError:
            print "Oh oh, couldn't remove ",self.directory
            raise VistrailsInternalError("Can't remove %s" % self.directory)

    def createFile(self, suffix = '', prefix = 'vt_tmp'):
        from core.modules import basic_modules
        (fd, name) = tempfile.mkstemp(suffix=suffix,
                                      prefix=prefix,
                                      dir=self.directory)
        os.close(fd)
        result = basic_modules.File()
        result.name = name
        result.upToDate = True
        self.files[name] = result
        return result

################################################################################
