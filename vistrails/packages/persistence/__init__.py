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
import tempfile
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

from core.configuration import ConfigurationObject
from core.modules.basic_modules import Path, File, Directory, Boolean
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.system import default_dot_vistrails, execute_cmdline, systemType

identifier = 'edu.utah.sci.vistrails.persistence'
version = '0.0.2'
name = 'Persistence'

global_db = None
local_db = None
compress_by_default = False
temp_persist_files = []
configuration = ConfigurationObject(global_db=(None, str), 
                                    local_db=(None, str),
                                    compress_by_default=False)

class PersistentPath(NotCacheable, Module):
    def __init__(self):
        Module.__init__(self)
        self.persistent_path = None

    def updateUpstream(self):
        global local_db
        # FIXME not sure if we need this
        self.persistent_path = None
        if not hasattr(self, 'signature'):
            raise ModuleError(self, 'Module has no signature')
        # FIXME really we need this to be everything upstream of 
        # PersistentFile but not including itself and its own parameters
        # may be able to use a different hasher...
        print 'signature:', self.signature
        if not os.path.exists(local_db):
            raise ModuleError(self, 'local_db "%s" does not exist' % local_db)
        dir = self.signature[:2]
        fname = self.signature[2:]
        full_path = os.path.join(local_db, dir, fname)
        if os.path.exists(full_path):
            self.persistent_path = full_path
            return
        elif os.path.exists(full_path + '.zip'):
            self.persistent_path = full_path + '.zip'
            return
        Module.updateUpstream(self)

    def unzip(self, zip_file, is_dir=None):
        global temp_persist_files

        output = []
        unzip_dir = tempfile.mkdtemp(prefix='vt_persist')
        temp_persist_files.append(unzip_dir)
        cmdline = ['unzip', '-q','-o','-d', unzip_dir, 
                   zip_file]
        result = execute_cmdline(cmdline, output)
        if result != 0 and len(output) != 0:
            raise ModuleError(self, "Unzip of '%s' failed" % zip_file)
        if is_dir is None or not is_dir:
            file_list = os.listdir(unzip_dir)
            if len(file_list) != 1:
                if is_dir is False:
                    raise ModuleError(self, 
                                      "Unzip expected one file, found %d" % \
                                          len(file_list))
                else:
                    is_dir = True
                    return unzip_dir
            elif is_dir is True:
                raise ModuleError(self,
                                  "Unzip expected directory, found one file")
            return os.path.join(unzip_dir, file_list[0])
        return unzip_dir

    def zip(self, input_path, zip_file, is_dir=None):
        zipcmd = 'zip'
        output = []
        result = -1
        cur_dir = os.getcwd()
        if systemType in ['Windows', 'Microsoft']:
            zipcmd = os.path.join(cur_dir,'zip.exe')
            if not os.path.exists(zipcmd):
                zipcmd = 'zip.exe' #assume zip is in path
        if is_dir is None:
            is_dir = os.path.isdir(input_path)
        if is_dir:
            if not os.path.isdir(input_path):
                raise ModuleError(self, 'Zip expected a directory, found file')
            cmdline = [zipcmd, '-r', '-q', zip_file, '.']
            os.chdir(input_path)
            result = execute_cmdline(cmdline, output)
            os.chdir(cur_dir)
        else:
            if not os.path.isfile(input_path):
                raise ModuleError(self, 'Zip expected a file, found directory')
            cmdline = [zipcmd, '-j', '-q', zip_file, input_path]
            result = execute_cmdline(cmdline, output)
            
        #if we want that directories are also stored in the zip file
        # we need to run from the vt directory
        #print result, output
        if result != 0 or len(output) != 0:
            for line in output:
                if line.find('deflated') == -1:
                    raise ModuleError(self, " ".join(output))
        return True

    def find(self, is_dir=None):
        global local_db
        if self.persistent_path is not None:
            if not os.path.exists(self.persistent_path):
                raise ModuleError(self, 
                                  'Persistent path "%s" does not exist' % \
                                      self.persistent_path)
            if self.persistent_path.endswith('.zip'):
                # it's compressed
                p_path = self.unzip(self.persistent_path, is_dir)
            else:
                # it's not compressed
                p_path = self.persistent_path
            return p_path
        return None

    def create(self, input_path, is_dir=None, do_compress=False):
        global local_db
        if not os.path.exists(input_path):
            raise ModuleError(self, 'Path "%s" does not exist' % input_path)
        dir = self.signature[:2]
        fname = self.signature[2:]
        full_path = os.path.join(local_db, dir, fname)
        dir_name = os.path.join(local_db, dir)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if is_dir is None:
            is_dir = os.path.isdir(input_path)
        if is_dir:
            if not os.path.isdir(input_path):
                raise ModuleError(self,
                                  'Create expected a directory, found file')
            if do_compress:
                full_path += '.zip'
                self.zip(input_path, full_path, is_dir)
            else:
                shutil.copytree(input_path, full_path)
        else:
            if not os.path.isfile(input_path):
                raise ModuleError(self,
                                  'Create expected a file, found directory')
            if do_compress:
                full_path += '.zip'
                self.zip(input_path, full_path, is_dir)
            else:
                shutil.copyfile(input_path, full_path)
        return full_path

    def find_or_create(self, is_dir=None):
        global compress_by_default
        p_path = self.find(is_dir)
        if p_path is not None:
            return p_path
        else:
            input_value = self.getInputFromPort("value")
            if self.hasInputFromPort("compress"):
                compress = self.getInputFromPort("compress")
            else:
                compress = compress_by_default
            p_path = self.create(input_value.name, is_dir, compress)
        
            if not os.path.exists(p_path):
                raise ModuleError(self, "Could not create peristent copy")
        return input_value.name

    def compute(self):
        p_path = self.find_or_create()
        persistent_path = Path()
        persistent_path.name = p_path
        persistent_path.setResult("value", persistent_path)
        self.setResult("value", persistent_path)
        
    _input_ports = [('value', Path), ('compress', Boolean, True)]
    _output_ports = [('value', Path)]

class PersistentFile(PersistentPath):
    def __init__(self):
        PersistentPath.__init__(self)
        
    def compute(self):
        p_path = self.find_or_create(False)
        persistent_file = File()
        persistent_file.name = p_path
        persistent_file.setResult("value", persistent_file)
        self.setResult("value", persistent_file)
        
    _input_ports = [('value', File)]
    _output_ports = [('value', File)]

class PersistentDirectory(PersistentPath):
    def __init__(self):
        PersistentPath.__init__(self)
        
    def compute(self):
        p_path = self.find_or_create(True)
        persistent_dir = Directory()
        persistent_dir.name = p_path
        persistent_dir.setResult("value", persistent_dir)
        self.setResult("value", persistent_dir)    

    _input_ports = [('value', Directory)]
    _output_ports = [('value', Directory)]

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
_modules = [PersistentPath, PersistentFile, PersistentDirectory]

def initialize():
    global global_db, local_db, compress_by_default

    if configuration.check('compress_by_default'):
        compress_by_default = configuration.compress_by_default
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

def finalize():
    # delete all temporary files/directories used by zip
    global temp_persist_files

    for fname in temp_persist_files:
        shutil.rmtree(fname)

    
