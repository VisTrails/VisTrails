############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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

import os
import shutil
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

from core.configuration import ConfigurationObject
from core.modules.basic_modules import File
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.system import default_dot_vistrails

identifier = 'edu.utah.sci.vistrails.persistence'
version = '0.0.1'
name = 'Persistence'

global_db = None
local_db = None
configuration = ConfigurationObject(global_db=(None, str), 
                                    local_db=(None, str))

class PersistentFile(NotCacheable, Module):
    def __init__(self):
        Module.__init__(self)
        self.persistent_fname = None

    def updateUpstream(self):
        global local_db
        # FIXME not sure if we need this
        self.persistent_fname = None
        if not hasattr(self, 'signature'):
            raise ModuleError('Module has no signature')
        # FIXME really we need this to be everything upstream of 
        # PersistentFile but not including itself and its own parameters
        # may be able to use a different hasher...
        print 'signature:', self.signature
        if not os.path.exists(local_db):
            raise ModuleError('local_db "%s" does not exist' % local_db)
        dir = self.signature[:2]
        fname = self.signature[2:]
        full_path = os.path.join(local_db, dir, fname)
        if os.path.exists(full_path):
            self.persistent_fname = full_path
            return
        Module.updateUpstream(self)
            
    def compute(self):
        global local_db
        if self.persistent_fname is not None:
            persistent_file = File()
            persistent_file.name = self.persistent_fname
            if not os.path.isfile(persistent_file.name):
                raise ModuleError('Persistent file "%s" does not exist' % \
                                      persistent_file.name)
        else:
            persistent_file = self.getInputFromPort("value")
            if not os.path.isfile(persistent_file.name):
                raise ModuleError('File "%s" does not exist' % \
                                      persistent_file.name)
            dir = self.signature[:2]
            fname = self.signature[2:]
            full_path = os.path.join(local_db, dir, fname)
            dir_name = os.path.join(local_db, dir)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            shutil.copy(persistent_file.name, full_path)
        # have the file
        self.setResult("value", persistent_file)
        
    _input_ports = [('value', File)]
    _output_ports = [('value', File)]

def persistent_file_hasher(pipeline, module, constant_hasher_map={}):
    hasher = sha_hash()
    u = hasher.update
    u(module.name)
    u(module.package)
    u(module.namespace or '')
    # FIXME: Not true because File can be a function!
    # do not include functions here because they shouldn't change the
    # hashing of the persistent_file
    return hasher.digest()

# _modules = [(PersistentFile, {'signatureCallable': persistent_file_hasher})]
_modules = [PersistentFile]

def initialize():
    global global_db, local_db

    if configuration.check('global_db'):
        global_db = configuration.global_db
    if configuration.check('local_db'):
        local_db = configuration.local_db
        if not os.path.exists(local_db):
            raise Exception('local_db "%s" does not exist' % local_db)
    else:
        local_db = os.path.join(default_dot_vistrails(), 'persistent_files')
        if not os.path.exists(local_db):
            try:
                os.mkdir(local_db)
            except:
                raise Exception('local_db "%s" does not exist' % local_db)

