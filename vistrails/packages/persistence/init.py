###############################################################################
##
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

import copy
import os
import shutil
import tempfile
import uuid
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

import core.debug
from core.configuration import ConfigurationObject
from core.cache.hasher import Hasher
from core.modules.basic_modules import Path, File, Directory, Boolean, \
    String, Constant
from core.modules.module_registry import get_module_registry, MissingModule, \
    MissingPackageVersion, MissingModuleVersion
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.system import default_dot_vistrails, execute_cmdline2, \
    execute_piped_cmdlines, systemType, \
    current_user, current_time, get_executable_path
from core.upgradeworkflow import UpgradeWorkflowHandler, UpgradeWorkflowError
from compute_hash import compute_hash
from widgets import PersistentRefInlineWidget, \
    PersistentInputFileConfiguration, PersistentOutputFileConfiguration, \
    PersistentInputDirConfiguration, PersistentOutputDirConfiguration, \
    PersistentRefModel, PersistentConfiguration
from db_utils import DatabaseAccessSingleton

global_db = None
local_db = None
search_dbs = None
db_access = None
git_bin = "@executable_path/git"
tar_bin = "@executable_path/tar"
compress_by_default = False
debug = False
temp_persist_files = []

def debug_print(*args):
    global debug
    if debug:
        for arg in args:
            print arg,
        print ''

class PersistentRef(Constant):

    # ref types
    ALWAYS_NEW = 0
    CREATE = 1
    EXISTING = 2
    
    def __init__(self):
        Constant.__init__(self)
        self.default_value = self
        
        self.type = PersistentRef.CREATE
        self.id = None
        self.version = None
        self.local_path = None
        self.local_read = False
        self.local_writeback = False
        self.versioned = False
        self.name = ''
        self.tags = ''

    # @staticmethod
    # def get_widget_class():
    #     return PersistentRefInlineWidget

    @staticmethod
    def translate_to_python(x):
        try:
            res = PersistentRef()
            s_tuple = eval(x)
            (res.type, res.id, res.version, res.local_path, res.local_read,
             res.local_writeback, res.versioned, res.name, res.tags) = s_tuple
        except:
            return None
#         result.settings = dict(zip(sorted(default_settings.iterkeys()),
#                                    s_tuple))
#         print 'from_string:', result.settings
        return res

    @staticmethod
    def translate_to_string(x):
        rep = str((x.type, x.id, x.version, x.local_path,
                   x.local_read, x.local_writeback, x.versioned,
                   x.name, x.tags))
        # rep = str(tuple(y[1] for y in sorted(x.settings.iteritems())))
        # print 'to_string:', rep
        return rep
        
    @staticmethod
    def validate(x):
        return type(x) == PersistentRef

    _input_ports = [('value', 
                     '(edu.utah.sci.vistrails.persistence:PersistentRef)')]
    _output_ports = [('value', 
                     '(edu.utah.sci.vistrails.persistence:PersistentRef)')]

class PersistentPath(Module):
    def __init__(self):
        Module.__init__(self)

    @staticmethod
    def git_command():
        global git_bin
        if systemType == "Windows":
            return [ "%s:" % local_db[0], "&&","cd", "%s" % local_db, "&&", git_bin]
        return ["cd", "%s" % local_db, "&&", git_bin]

    @staticmethod
    def git_get_path(name, version="HEAD", path_type=None, 
                     out_name=None, out_suffix=''):
        if path_type is None:
            path_type = PersistentPath.git_get_type(name, version)
        if path_type == 'tree':
            return PersistentPath.git_get_dir(name, version, out_name,
                                              out_suffix)
        elif path_type == 'blob':
            return PersistentPath.git_get_file(name, version, out_name,
                                               out_suffix)
        
        raise ModuleError(self, "Unknown path type '%s'" % path_type)

    @staticmethod
    def git_get_file(name, version="HEAD", out_fname=None, out_suffix=''):
        global temp_persist_files
        if out_fname is None:
            # create a temporary file
            (fd, out_fname) = tempfile.mkstemp(suffix=out_suffix,
                                               prefix='vt_persist')
            os.close(fd)
            temp_persist_files.append(out_fname)
            
        cmd_line =  PersistentPath.git_command() + ["show",
                                                    str(version + ':' + name),
                                                    '>', out_fname]
        debug_print('executing command', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        if result != 0:
            # check output for error messages
            raise ModuleError(self, "Error retrieving file '%s'\n" % name +
                              errs)
        return out_fname

    @staticmethod
    def git_get_dir(name, version="HEAD", out_dirname=None, 
                    out_suffix=''):
        global temp_persist_files, tar_bin
        if out_dirname is None:
            # create a temporary directory
            out_dirname = tempfile.mkdtemp(suffix=out_suffix,
                                           prefix='vt_persist')
            temp_persist_files.append(out_dirname)
        elif not os.path.exists(out_dirname):
            os.makedirs(out_dirname)
        if systemType == "Windows":
            cmd_list = [PersistentPath.git_command() + \
                        ["archive", str(version + ':' + name)],
                    ["%s:" % out_dirname[0], "&&", "cd", "%s"%out_dirname, "&&", tar_bin, '-xf-']]
        else:
            cmd_list = [PersistentPath.git_command() + \
                        ["archive", str(version + ':' + name)],
                    [tar_bin, '-C', out_dirname, '-xf-']]
        debug_print('executing commands', cmd_list)
        result, output, errs = execute_piped_cmdlines(cmd_list)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        if result != 0:
            # check output for error messages
            raise ModuleError(self, "Error retrieving file '%s'\n" % name +
                              errs)
        return out_dirname

    # def git_get_hash(self, name, version="HEAD"):
    #     cmd_list = [["echo", str(version + ':' + name)],
    #                 self.git_command() + ["cat-file", "--batch-check"]]
    @staticmethod
    def git_get_hash(name, version="HEAD", path_type=None):
        if path_type is None:
            path_type = PersistentPath.git_get_type(name, version)
        if path_type == 'blob':
            cmd_list = [PersistentPath.git_command() + ["ls-files", "--stage",
                                                        str(version),
                                                        str(name)]]
            debug_print('executing commands', cmd_list)
            result, output, errs = execute_piped_cmdlines(cmd_list)
            debug_print('stdout:', type(output), output)
            debug_print('stderr:', type(errs), errs)
            if result != 0:
                # check output for error messages
                raise ModuleError(self, "Error retrieving path '%s'\n" % name +
                                  errs)
            return output.split(None, 2)[1]
        elif path_type == 'tree':
            cmd_list = [PersistentPath.git_command() + ["ls-tree", "-d",
                                                        str(version),
                                                        str(name)]]
            debug_print('executing commands', cmd_list)
            result, output, errs = execute_piped_cmdlines(cmd_list)
            debug_print('stdout:', type(output), output)
            debug_print('stderr:', type(errs), errs)
            if result != 0:
                # check output for error messages
                raise ModuleError(self, "Error retrieving path '%s'\n" % name +
                                  errs)
            return output.split(None, 3)[2]
        return None

    @staticmethod
    def git_get_type(name, version="HEAD"):
        #cmd_list = [["echo", str(version + ':' + name)],
        #            self.git_command() + ["cat-file", "--batch-check"]]
        cmd_list = [PersistentPath.git_command() + ["cat-file", "-t",
                                                    str(version + ':'+name)]]
        debug_print('executing commands', cmd_list)
        result, output, errs = execute_piped_cmdlines(cmd_list)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        if result != 0:
            # check output for error messages
            raise ModuleError(self, "Error retrieving file '%s'" % name +
                              errs)
        return output.split(None,1)[0]
        #return output.split(None, 2)[1]

    @staticmethod
    def git_add_commit(filename):
        cmd_line = PersistentPath.git_command() + ['add', filename]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print(output)
        debug_print('***')

        cmd_line = PersistentPath.git_command() + ['commit', '-q', '-m', 
                                         'Updated %s' % filename]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        debug_print('***')

        if len(output) > 1:
            # failed b/c file is the same
            # return 
            debug_print('got unexpected output')
            return None

        cmd_line = PersistentPath.git_command() + ['log', '-1']
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print(output)
        debug_print('***')

        if output.startswith('commit'):
            return output.split(None, 2)[1]
        return None

    @staticmethod
    def git_get_latest_version(filename):
        cmd_line = PersistentPath.git_command() + ['log', '-1', filename]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print(output)
        if output.startswith('commit'):
            return output.split(None, 2)[1]
        return None

    @staticmethod
    def git_compute_hash(path, path_type=None):
        if path_type is None:
            if os.path.isdir(path):
                path_type = 'tree'
            elif os.path.isfile(path):
                path_type = 'blob'
        if path_type == 'tree':
            return PersistentPath.git_compute_tree_hash(path)
        elif path_type == 'blob':
            return PersistentPath.git_compute_file_hash(path)
        
        raise ModuleError(None, "Unknown path type '%s'" % path_type)
        

    @staticmethod
    def git_compute_file_hash(filename):
        # run git hash-object filename
        cmd_line = PersistentPath.git_command() + ['hash-object', filename]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        debug_print('***')

        if result != 0:
            raise ModuleError(None, "Error retrieving file '%s'\n" % filename +
                              errs)
        return output.strip()

    @staticmethod
    def git_compute_tree_hash(dirname):
        lines = []
        for file in os.listdir(dirname):
            fname = os.path.join(dirname, file)
            if os.path.isdir(fname):
                hash = PersistentPath.git_compute_tree_hash(fname)
                lines.append("040000 tree " + hash + '\t' + file)
            elif os.path.isfile(fname):
                hash = PersistentPath.git_compute_file_hash(fname)
                lines.append("100644 blob " + hash + '\t' + file)

        (fd, tree_fname) = tempfile.mkstemp(prefix='vt_persist')
        os.close(fd)
        
        tree_f = open(tree_fname, 'w')
        for line in lines:
            print >>tree_f, line
        tree_f.close()

        cmd_line = PersistentPath.git_command() + ['mktree', '--missing',
                                                   '<', tree_fname]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print(output)
        debug_print('***')
        os.remove(tree_fname)
        if result != 0:
            raise ModuleError(self, "Error retrieving file '%s'\n" % dirname +
                              errs)
        tree_hash = output.rsplit(None, 1)[-1].strip()
        debug_print('hash:', tree_hash)

        cmd_line = PersistentPath.git_command() + ['prune']
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print(output)
        debug_print('***')
        
        return tree_hash

    @staticmethod
    def git_remove_path(path):
        global git_bin, local_db
        # only recommended for intermediate files!
        inner_cmd = [git_bin, "rm", "-r", "--cached", "--ignore-unmatch",path]
        inner_cmd_str = ' '.join(inner_cmd)
        cmd_line = PersistentPath.git_command() + \
            ['filter-branch', '--index-filter', inner_cmd_str, 'HEAD']
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        debug_print('***')
        shutil.rmtree(os.path.join(local_db, ".git", "refs", "original"))
        cmd_line = PersistentPath.git_command() + ["reflog", "expire","--all"]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        debug_print('***')
        cmd_line = PersistentPath.git_command() + ["gc", "--aggressive",
                                                   "--prune"]
        debug_print('executing', cmd_line)
        result, output, errs = execute_cmdline2(cmd_line)
        debug_print('result:', result)
        debug_print('stdout:', type(output), output)
        debug_print('stderr:', type(errs), errs)
        debug_print('***')

    def get_path_type(self, path):
        if os.path.isdir(path):
            return 'tree'
        elif os.path.isfile(path):
            return 'blob'            

    def copypath(self, src, dst, path_type=None):
        if path_type is None:
            path_type = self.get_path_type(src)

        if path_type == 'blob':
            shutil.copyfile(src, dst)
        elif path_type == 'tree':
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            raise ModuleError(self, "Unknown path type '%s'" % path_type)

    def set_result(self, path):
        persistent_path = Path()
        persistent_path.name = path
        persistent_path.setResult('value', self)
        persistent_path.upToDate = True
        self.setResult("value", persistent_path)

    def updateUpstream(self, is_input=None, path_type=None):
        global local_db, db_access

        if is_input is None:
            if not self.hasInputFromPort('value'):
                is_input = True
            else:
                # FIXME: check if the signature is the signature of
                # the value if so we know that it's an input...
                is_input = False

        self.persistent_ref = None
        self.persistent_path = None
        if not is_input:
            # can check updateUpstream
            if not hasattr(self, 'signature'):
                raise ModuleError(self, 'Module has no signature')
            if not self.hasInputFromPort('ref'):
                # create new reference with no name or tags
                ref = PersistentRef()
                ref.signature = self.signature
                debug_print('searching for signature', self.signature)
                sig_ref = db_access.search_by_signature(self.signature)
                debug_print('sig_ref:', sig_ref)
                if sig_ref:
                    debug_print('setting persistent_ref')
                    ref.id, ref.version, ref.name = sig_ref
                    self.persistent_ref = ref
                    #             else:
                    #                 ref.id = uuid.uuid1()
            else:
                # update single port
                self.updateUpstreamPort('ref')
                ref = self.getInputFromPort('ref')
                if db_access.ref_exists(ref.id, ref.version):
                    if ref.version is None:
                        ref.version = self.git_get_latest_version(ref.id)
                    signature = db_access.get_signature(ref.id, ref.version)
                    if signature == self.signature:
                        # don't need to create a new version
                        self.persistent_ref = ref

                # copy as normal
                # don't copy if equal

            # FIXME also need to check that the file actually exists here!
            if self.persistent_ref is not None:
                _, suffix = os.path.splitext(self.persistent_ref.name)
                self.persistent_path = \
                    self.git_get_path(self.persistent_ref.id, 
                                      self.persistent_ref.version,
                                      out_suffix=suffix)
                debug_print("FOUND persistent path")
                debug_print(self.persistent_path)
                debug_print(self.persistent_ref.local_path)

        if self.persistent_ref is None or self.persistent_path is None:
            debug_print("NOT FOUND persistent path")
            Module.updateUpstream(self)

    def compute(self, is_input=None, path_type=None):
        global db_access
        if not self.hasInputFromPort('value') and \
                not self.hasInputFromPort('ref'):
            raise ModuleError(self, "Need to specify path or reference")

        if self.persistent_path is not None:
            debug_print('using persistent path')
            ref = self.persistent_ref
            path = self.persistent_path
        elif self.hasInputFromPort('ref'):
            ref = self.getInputFromPort('ref')
            if ref.id is None:
                ref.id = str(uuid.uuid1())
        else:
            # create a new reference
            ref = PersistentRef()
            ref.id = str(uuid.uuid1())

        if self.hasInputFromPort('localPath'):
            ref.local_path = self.getInputFromPort('localPath').name
            if self.hasInputFromPort('readLocal'):
                ref.local_read = self.getInputFromPort('readLocal')
            if self.hasInputFromPort('writeLocal'):
                ref.local_writeback = self.getInputFromPort('writeLocal')

        if is_input is None:
            is_input = False
            if not self.hasInputFromPort('value'):
                is_input = True
            else:
                if ref.local_path and ref.local_read:
                    debug_print('found local path with local read')
                    is_input = True
                # FIXME: check if the signature is the signature of
                # the value if so we know that it's an input...

        # if just reference, pull path from repository (get latest
        # version unless specified as specific version)
        if self.persistent_path is None and not self.hasInputFromPort('value') \
                and is_input and not (ref.local_path and ref.local_read):
            _, suffix = os.path.splitext(ref.name)
            if not db_access.ref_exists(ref.id, ref.version):
                raise ModuleError(self, "Persistent entity '%s' does not "
                                  "exist in the local repository." % ref.id)
            if ref.version is None:
                ref.version = self.git_get_latest_version(ref.id)

            # get specific ref.uuid, ref.version combo
            path = self.git_get_path(ref.id, ref.version, 
                                     out_suffix=suffix)
            
        elif self.persistent_path is None:
            # copy path to persistent directory with uuid as name
            if is_input and ref.local_path and ref.local_read:
                debug_print('using local_path')
                path = ref.local_path
            else:
                path = self.getInputFromPort('value').name
            # this is a static method so we need to add module ourselves
            try:
                new_hash = self.git_compute_hash(path, path_type)
            except ModuleError, e:
                e.module = self
                raise e
            rep_path = os.path.join(local_db, ref.id)
            do_update = True
            if os.path.exists(rep_path):
                old_hash = self.git_get_hash(ref.id, path_type=path_type)
                debug_print('old_hash:', old_hash)
                debug_print('new_hash:', new_hash)
                if old_hash == new_hash:
                    do_update = False
                    
            if do_update:
                debug_print('doing update')
                self.copypath(path, os.path.join(local_db, ref.id))

                # commit (and add to) repository
                # get commit id as version id
                # persist object-hash, commit-version to repository
                version = self.git_add_commit(ref.id)
                ref.version = version

                # write object-hash, commit-version to provenance
                if is_input:
                    signature = new_hash
                else:
                    signature = self.signature
                db_access.write_database({'id': ref.id, 
                                          'name': ref.name, 
                                          'tags': ref.tags, 
                                          'user': current_user(),
                                          'date_created': current_time(),
                                          'date_modified': current_time(),
                                          'content_hash': new_hash,
                                          'version': version, 
                                          'signature': signature,
                                          'type': path_type})
            
        # if keep-local and path is different than the selected path, copy
        # the path to the keep-local path
        if ref.local_path and ref.local_writeback:
            if path != ref.local_path:
                self.copypath(path, ref.local_path)
        if not str(ref.version):
            core.debug.critical("Persistent version annotation not set correctly "
                           "for persistent_id=%s" % ref.id)
        # for all paths
        self.annotate({'persistent_id': ref.id,
                       'persistent_version': ref.version})
        self.set_result(path)

    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:Path)'),
                    ('ref', 
                     '(edu.utah.sci.vistrails.persistence:PersistentRef)'),
                    ('localPath', '(edu.utah.sci.vistrails.basic:Path)'),
                    ('readLocal', '(edu.utah.sci.vistrails.basic:Boolean)', \
                         True),
                    ('writeLocal','(edu.utah.sci.vistrails.basic:Boolean)', \
                         True)]
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:Path)')]

class PersistentFile(PersistentPath):
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:File)'),
                    ('localPath', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:File)')]

    def updateUpstream(self, is_input=None):
        PersistentPath.updateUpstream(self, is_input, 'blob')

    def compute(self, is_input=None):
        PersistentPath.compute(self, is_input, 'blob')

    def set_result(self, path):
        persistent_path = File()
        persistent_path.name = path
        persistent_path.setResult('value', self)
        persistent_path.upToDate = True
        self.setResult("value", persistent_path)

class PersistentDir(PersistentPath):
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('localPath', '(edu.utah.sci.vistrails.basic:Directory)')]
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:Directory)')]

    def updateUpstream(self, is_input=None):
        PersistentPath.updateUpstream(self, is_input, 'tree')

    def compute(self, is_input=None):
        PersistentPath.compute(self, is_input, 'tree')

    def set_result(self, path):
        persistent_path = Directory()
        persistent_path.name = path
        persistent_path.setResult('value', self)
        persistent_path.upToDate = True
        self.setResult("value", persistent_path)

# class PersistentFile(PersistentPath):
#     _input_ports = [('value', '(edu.utah.sci.vistrails.basic:File)')]
#     _output_ports = [('value', '(edu.utah.sci.vistrails.basic:File)')]

#     def updateUpstream(self, is_input=None):
#         PersistentPath.updateUpstream(self, is_input, 'blob')

#     def compute(self, is_input=None):
#         PersistentPath.compute(self, is_input, 'blob')

#     def set_result(self, path):
#         persistent_path = File()
#         persistent_path.name = path
#         persistent_path.setResult('value', self)
#         persistent_path.upToDate = True
#         self.setResult("value", persistent_path)

class PersistentInputDir(PersistentDir):
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:Directory)', True)]

    def updateUpstream(self):
        PersistentDir.updateUpstream(self, True)

    def compute(self):
        PersistentDir.compute(self, True)
        
class PersistentIntermediateDir(PersistentDir):
    def updateUpstream(self):
        PersistentDir.updateUpstream(self, False)

    def compute(self):
        PersistentDir.compute(self, False)
    
class PersistentOutputDir(PersistentDir):
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:Directory)', 
                      True)]

    def updateUpstream(self):
        PersistentDir.updateUpstream(self, False)

    def compute(self):
        PersistentDir.compute(self, False)

class PersistentInputFile(PersistentFile):
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:File)', True)]

    def updateUpstream(self):
        PersistentFile.updateUpstream(self, True)

    def compute(self):
        PersistentFile.compute(self, True)
    
class PersistentIntermediateFile(PersistentFile):
    def updateUpstream(self):
        PersistentFile.updateUpstream(self, False)

    def compute(self):
        PersistentFile.compute(self, False)
    
class PersistentOutputFile(PersistentFile):
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:File)', True)]

    def updateUpstream(self):
        PersistentFile.updateUpstream(self, False)

    def compute(self):
        PersistentFile.compute(self, False)
    
#def persistent_ref_hasher(p):
#    return Hasher.parameter_signature(p)

def persistent_module_hasher(pipeline, module, chm):
    current_hash = Hasher.module_signature(module, chm)
    ref = None
    read_local = False
    for function in module.functions:
        if function.name == "ref":
            ref = PersistentRef.translate_to_python(function.params[0].strValue)
        if function.name == 'readLocal':
            read_local = \
                Boolean.translate_to_python(function.params[0].strValue)
    if ref and not read_local and db_access.ref_exists(ref.id, ref.version):
        if ref.version is None:
            ref.version = PersistentPath.git_get_latest_version(ref.id)
        return Hasher.compound_signature([current_hash, str(ref.id),
                                          str(ref.version)])
    return current_hash

_modules = [PersistentRef, PersistentPath, PersistentFile, PersistentDir,
           (PersistentInputFile, {'configureWidgetType': \
                                      PersistentInputFileConfiguration,
                                  'signatureCallable': \
                                      persistent_module_hasher}),
           (PersistentOutputFile, {'configureWidgetType': \
                                       PersistentOutputFileConfiguration,
                                   'signatureCallable': \
                                       persistent_module_hasher}),
           (PersistentIntermediateFile, {'configureWidgetType': \
                                             PersistentOutputFileConfiguration,
                                         'signatureCallable': \
                                             persistent_module_hasher}),
           (PersistentInputDir, {'configureWidgetType': \
                                     PersistentInputDirConfiguration,
                                 'signatureCallable': \
                                     persistent_module_hasher}),
           (PersistentOutputDir, {'configureWidgetType': \
                                      PersistentOutputDirConfiguration,
                                  'signatureCallable': \
                                      persistent_module_hasher}),
           (PersistentIntermediateDir, {'configureWidgetType': \
                                            PersistentOutputDirConfiguration,
                                        'signatureCallable': \
                                            persistent_module_hasher})]

def git_init(dir):
    global git_bin
    if systemType == "Windows":
        cmd = ["%s:" % dir[0], "&&", "cd", "%s" % dir, "&&", git_bin, "init"]
    else:
        cmd = ["cd", "%s" % dir, "&&", git_bin, "init"]
    debug_print('cmd:', cmd)
    result, output, errs = execute_cmdline2(cmd)
    debug_print('init result', result)
    debug_print('init output', output)

def initialize():
    global global_db, local_db, search_dbs, compress_by_default, db_access, \
        git_bin, tar_bin, debug
    
    if configuration.check('git_bin'):
        git_bin = configuration.git_bin
    if git_bin.startswith("@executable_path/"):
        non_expand_path = git_bin
        git_bin = get_executable_path(git_bin[len("@executable_path/"):])
        if git_bin is not None:
            configuration.git_bin = non_expand_path
    if git_bin is None:
        git_bin = 'git'
        configuration.git_bin = git_bin

    if configuration.check('tar_bin'):
        tar_bin = configuration.tar_bin
    if tar_bin.startswith("@executable_path/"):
        non_expand_path = tar_bin
        tar_bin = get_executable_path(tar_bin[len("@executable_path/"):])
        if tar_bin is not None:
            configuration.tar_bin = non_expand_path
    if tar_bin is None:
        tar_bin = 'tar'
        configuration.tar_bin = tar_bin
        
    if configuration.check('compress_by_default'):
        compress_by_default = configuration.compress_by_default
    if configuration.check('debug'):
        debug = configuration.debug
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

    git_init(local_db)
    debug_print('creating DatabaseAccess')
    db_path = os.path.join(local_db, '.files.db')
    db_access = DatabaseAccessSingleton(db_path)
    debug_print('done', db_access)
    
    search_dbs = [local_db,]
    if configuration.check('search_dbs'):
        try:
            check_paths = eval(configuration.search_dbs)
        except:
            print "*** persistence error: cannot parse search_dbs ***"
        for path in check_paths:
            if os.path.exists(path):
                search_dbs.append(path)
            else:
                print '*** persistence warning: cannot find path "%s"' % path

_configuration_widget = None

def finalize():
    # delete all temporary files/directories used by zip
    global temp_persist_files, db_access, _configuration_widget

    for fname in temp_persist_files:
        if os.path.isfile(fname):
            os.remove(fname)
        elif os.path.isdir(fname):
            shutil.rmtree(fname)
    db_access.finalize()
    if _configuration_widget is not None:
        _configuration_widget.deleteLater()

def menu_items():
    def show_configure():
        global _configuration_widget
        if _configuration_widget is None:
            _configuration_widget = PersistentConfiguration()
        _configuration_widget.show()
    menu_tuple = (("Manage Store...", show_configure),)
    return menu_tuple

def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {'PersistentFile':
                        [(None, '0.1.0', 'PersistentIntermediateFile',
                          {'dst_port_remap':
                               {'compress': None}})],
                    'PersistentDirectory':
                        [(None, '0.1.0', 'PersistentIntermediateDir',
                          {'dst_port_remap':
                               {'compress': None}})]
                    }
    for module in ['PersistentPath', 'PersistentFile', 'PersistentDir',
                   'PersistentInputFile', 'PersistentOutputFile',
                   'PersistentIntermediateFile',
                   'PersistentInputDir', 'PersistentOutputDir',
                   'PersistentIntermediateDir']:
        upgrade = ('0.2.0', '0.2.2', None,
                   {'dst_port_remap': {'ref': 'ref'}})
        if module in module_remap:
            module_remap[module].append(upgrade)
        else:
            module_remap[module] = [upgrade]
    
    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               module_remap)
    
# def handle_missing_module(controller, module_id, pipeline):
#     reg = get_module_registry()
#     module_remap = {'PersistentFile': PersistentIntermediateFile,
#                     'PersistentDirectory': PersistentIntermediateDir,
#                     } # 'PersistentPath': PersistentIntermediatePath}
#     function_remap = {'value': 'value',
#                       'compress': None}
#     src_port_remap = {'value': 'value',
#                       'compress': None},
#     dst_port_remap = {'value': 'value'}

#     old_module = pipeline.modules[module_id]
#     debug_print('running handle_missing_module', old_module.name)
#     if old_module.name in module_remap:
#         debug_print('running through remamp')
#         new_descriptor = reg.get_descriptor(module_remap[old_module.name])
#         action_list = \
#             UpgradeWorkflowHandler.replace_module(controller, pipeline,
#                                                   module_id, new_descriptor,
#                                                   function_remap,
#                                                   src_port_remap,
#                                                   dst_port_remap)
#         debug_print('action_list', action_list)
#         return action_list

#     return False

# def handle_all_errors(controller, err_list, pipeline):
#     new_actions = []
#     debug_print('starting handle_all_errors')
#     for err in err_list:
#         debug_print('processing', err)
#         if isinstance(err, MissingModule):
#             debug_print('got missing')
#             actions = handle_missing_module(controller, err._module_id, 
#                                             pipeline)
#             if actions:
#                 new_actions.extend(actions)
#         elif isinstance(err, MissingPackageVersion):
#             debug_print('got package version change')
#             actions = handle_module_upgrade_request(controller, err._module_id,
#                                                     pipeline)
#             if actions:
#                 new_actions.extend(actions)

#     if len(new_actions) == 0:
#         return None
#     return new_actions
