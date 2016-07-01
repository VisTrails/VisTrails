###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from ast import literal_eval
import copy
import os
import shutil
import tempfile
import uuid

import vistrails.core.debug
from vistrails.core.configuration import ConfigurationObject
from vistrails.core.cache.hasher import Hasher
from vistrails.core.modules.basic_modules import Path, PathObject, Directory, Boolean, \
    String, Constant
from vistrails.core.modules.module_registry import get_module_registry, MissingModule, \
    MissingPackageVersion, MissingModuleVersion
from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
from vistrails.core.system import current_dot_vistrails, execute_cmdline2, \
    execute_piped_cmdlines, systemType, \
    current_user, current_time, get_executable_path
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler, UpgradeWorkflowError
from compute_hash import compute_hash
from widgets import PersistentRefInlineWidget, \
    PersistentInputFileConfiguration, PersistentOutputFileConfiguration, \
    PersistentInputDirConfiguration, PersistentOutputDirConfiguration, \
    PersistentRefModel, PersistentConfiguration
from db_utils import DatabaseAccessSingleton
import repo

try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new


global_db = None
local_db = None
search_dbs = None
db_access = None
git_bin = "@executable_path/git"
tar_bin = "@executable_path/tar"
compress_by_default = False
debug = False

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
            s_tuple = literal_eval(x)
            (res.type, res.id, res.version, res.local_path, res.local_read,
             res.local_writeback, res.versioned, res.name, res.tags) = s_tuple
        except Exception:
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
        return isinstance(x, PersistentRef)

    _input_ports = [('value', '(PersistentRef)')]
    _output_ports = [('value', '(PersistentRef)')]

class PersistentPath(Module):
    def __init__(self):
        Module.__init__(self)

    # FIXME find a way to do this through dulwich and move to repo.py
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

    @staticmethod
    def git_command():
        if systemType in ['Windows', 'Microsoft']:
            return ['cd', '/D', local_db, '&&', git_bin]
        else:
            return ['cd', local_db, '&&', git_bin]

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
        persistent_path.set_output('value', self)
        persistent_path.upToDate = True
        self.set_output("value", persistent_path)

    def update_upstream(self, is_input=None, path_type=None):
        global db_access

        if is_input is None:
            if not self.has_input('value'):
                is_input = True
            else:
                # FIXME: check if the signature is the signature of
                # the value if so we know that it's an input...
                is_input = False

        self.persistent_ref = None
        self.persistent_path = None
        if is_input:
            return super(PersistentPath, self).update_upstream()

        # can check update_upstream
        if not hasattr(self, 'signature'):
            raise ModuleError(self, 'Module has no signature')

        ref_exists = False
        if not self.has_input('ref'):
            # create new reference with no name or tags
            ref = PersistentRef()
            ref.signature = self.signature
        else:
            # update single port
            self.update_upstream_port('ref')
            ref = self.get_input('ref')
            if db_access.ref_exists(ref.id, ref.version):
                ref_exists = True
                if ref.version is None:
                    ref.version = \
                        repo.get_current_repo().get_latest_version(ref.id)
                signature = db_access.get_signature(ref.id, ref.version)
                if signature == self.signature:
                    # don't need to create a new version
                    self.persistent_ref = ref

        # Note that ref_exists is True if the reference is a fixed
        # reference; if it was assigned a new uuid, we can still
        # reuse a reference with the same signature
        if not ref_exists:
            signature = self.signature
            debug_print('searching for signature', signature)
            sig_ref = db_access.search_by_signature(signature)
            debug_print('sig_ref:', sig_ref)
            if sig_ref:
                debug_print('setting persistent_ref')
                ref.id, ref.version, ref.name = sig_ref
                self.persistent_ref = ref
                #             else:
                #                 ref.id = uuid.uuid1()

            # copy as normal
            # don't copy if equal

        # FIXME also need to check that the file actually exists here!
        if self.persistent_ref is not None:
            _, suffix = os.path.splitext(self.persistent_ref.name)
            self.persistent_path = repo.get_current_repo().get_path(
                self.persistent_ref.id,
                self.persistent_ref.version,
                out_suffix=suffix)
            debug_print("FOUND persistent path")
            debug_print(self.persistent_path)
            debug_print(self.persistent_ref.local_path)

        if self.persistent_ref is None or self.persistent_path is None:
            debug_print("NOT FOUND persistent path")
            super(PersistentPath, self).update_upstream()

    def compute(self, is_input=None, path_type=None):
        global db_access
        if not self.has_input('value') and \
                not self.has_input('ref'):
            raise ModuleError(self, "Need to specify path or reference")

        if self.persistent_path is not None:
            debug_print('using persistent path')
            ref = self.persistent_ref
            path = self.persistent_path
        elif self.has_input('ref'):
            ref = self.get_input('ref')
            if ref.id is None:
                ref.id = str(uuid.uuid1())
        else:
            # create a new reference
            ref = PersistentRef()
            ref.id = str(uuid.uuid1())

        if self.has_input('localPath'):
            ref.local_path = self.get_input('localPath').name
            if self.has_input('readLocal'):
                ref.local_read = self.get_input('readLocal')
            if self.has_input('writeLocal'):
                ref.local_writeback = self.get_input('writeLocal')

        if is_input is None:
            is_input = False
            if not self.has_input('value'):
                is_input = True
            else:
                if ref.local_path and ref.local_read:
                    debug_print('found local path with local read')
                    is_input = True
                # FIXME: check if the signature is the signature of
                # the value if so we know that it's an input...

        # if just reference, pull path from repository (get latest
        # version unless specified as specific version)
        if self.persistent_path is None and not self.has_input('value') \
                and is_input and not (ref.local_path and ref.local_read):
            _, suffix = os.path.splitext(ref.name)
            if not db_access.ref_exists(ref.id, ref.version):
                raise ModuleError(self, "Persistent entity '%s' does not "
                                  "exist in the local repository." % ref.id)
            if ref.version is None:
                ref.version = repo.get_current_repo().get_latest_version(ref.id)

            # get specific ref.uuid, ref.version combo
            path = repo.get_current_repo().get_path(ref.id, ref.version, 
                                                    out_suffix=suffix)
            
        elif self.persistent_path is None:
            # copy path to persistent directory with uuid as name
            if is_input and ref.local_path and ref.local_read:
                debug_print('using local_path')
                path = ref.local_path
            else:
                path = self.get_input('value').name
            # this is a static method so we need to add module ourselves
            try:
                new_hash = repo.get_current_repo().compute_hash(path)
            except ModuleError, e:
                e.module = self
                raise e
            rep_path = os.path.join(local_db, ref.id)
            do_update = True
            if os.path.exists(rep_path):
                if os.path.isdir(rep_path):
                    actual_type = 'tree'
                elif os.path.isfile(rep_path):
                    actual_type = 'blob'
                else:
                    raise ModuleError(self, "Path is something not a file or "
                                      "a directory")
                if path_type is None:
                    path_type = actual_type
                else:
                    if path_type != actual_type:
                        def show_type(t):
                            if t == 'tree': return "directory"
                            elif t == 'blob': return "file"
                            else: return '"%s"' % t
                        raise ModuleError(self, "Path is not a %s but a %s" % (
                                          show_type(path_type),
                                          show_type(actual_type)))

                old_hash = repo.get_current_repo().get_hash(ref.id, 
                                                            path_type=path_type)
                debug_print('old_hash:', old_hash)
                debug_print('new_hash:', new_hash)
                if old_hash == new_hash:
                    do_update = False
                    
            if do_update:
                debug_print('doing update')

                if path_type == 'tree':
                    if (not os.path.exists(path) or
                            not os.listdir(path)):
                        raise ModuleError(self, "This directory is empty")

                self.copypath(path, os.path.join(local_db, ref.id))

                # commit (and add to) repository
                # get commit id as version id
                # persist object-hash, commit-version to repository
                version = repo.get_current_repo().add_commit(ref.id)
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
            vistrails.core.debug.critical("Persistent version annotation not set correctly "
                           "for persistent_id=%s" % ref.id)
        # for all paths
        self.annotate({'persistent_id': ref.id,
                       'persistent_version': ref.version})
        self.set_result(path)

    _input_ports = [('value', '(basic:Path)'),
                    ('ref', '(PersistentRef)'),
                    ('localPath', '(basic:Path)'),
                    ('readLocal', '(basic:Boolean)', True),
                    ('writeLocal','(basic:Boolean)', True)]
    _output_ports = [('value', '(basic:Path)')]

class PersistentFile(PersistentPath):
    _input_ports = [('value', '(basic:File)'),
                    ('localPath', '(basic:File)')]
    _output_ports = [('value', '(basic:File)')]

    def update_upstream(self, is_input=None):
        PersistentPath.update_upstream(self, is_input, 'blob')

    def compute(self, is_input=None):
        PersistentPath.compute(self, is_input, 'blob')

    def set_result(self, path):
        persistent_path = PathObject(path)
        self.set_output("value", persistent_path)

class PersistentDir(PersistentPath):
    _input_ports = [('value', '(basic:Directory)'),
                    ('localPath', '(basic:Directory)')]
    _output_ports = [('value', '(basic:Directory)')]

    def update_upstream(self, is_input=None):
        PersistentPath.update_upstream(self, is_input, 'tree')

    def compute(self, is_input=None):
        PersistentPath.compute(self, is_input, 'tree')

    def set_result(self, path):
        persistent_path = PathObject(path)
        self.set_output("value", persistent_path)

class PersistentInputDir(PersistentDir):
    _input_ports = [('value', '(basic:Directory)', True)]

    def update_upstream(self):
        PersistentDir.update_upstream(self, True)

    def compute(self):
        PersistentDir.compute(self, True)
        
class PersistentIntermediateDir(PersistentDir):
    def update_upstream(self):
        PersistentDir.update_upstream(self, False)

    def compute(self):
        PersistentDir.compute(self, False)
    
class PersistentOutputDir(PersistentDir):
    _output_ports = [('value', '(basic:Directory)', True)]

    def update_upstream(self):
        PersistentDir.update_upstream(self, False)

    def compute(self):
        PersistentDir.compute(self, False)

class PersistentInputFile(PersistentFile):
    _input_ports = [('value', '(basic:File)', True)]

    def update_upstream(self):
        PersistentFile.update_upstream(self, True)

    def compute(self):
        PersistentFile.compute(self, True)
    
class PersistentIntermediateFile(PersistentFile):
    def update_upstream(self):
        PersistentFile.update_upstream(self, False)

    def compute(self):
        PersistentFile.compute(self, False)
    
class PersistentOutputFile(PersistentFile):
    _output_ports = [('value', '(basic:File)', True)]

    def update_upstream(self):
        PersistentFile.update_upstream(self, False)

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
            ref.version = repo.get_current_repo().get_latest_version(ref.id)
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

def initialize():
    global global_db, local_db, search_dbs, compress_by_default, db_access, \
        git_bin, debug
    
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
        
    if configuration.check('compress_by_default'):
        compress_by_default = configuration.compress_by_default
    if configuration.check('debug'):
        debug = configuration.debug
    if configuration.check('global_db'):
        global_db = configuration.global_db
    if configuration.check('local_db'):
        local_db = configuration.local_db
        if not os.path.exists(local_db):
            raise RuntimeError('local_db "%s" does not exist' % local_db)
    else:
        local_db = os.path.join(current_dot_vistrails(), 'persistent_files')
        if not os.path.exists(local_db):
            try:
                os.mkdir(local_db)
            except OSError:
                raise RuntimeError('local_db "%s" does not exist' % local_db)

    local_repo = repo.get_repo(local_db)
    repo.set_current_repo(local_repo)

    debug_print('creating DatabaseAccess')
    db_path = os.path.join(local_db, '.files.db')
    db_access = DatabaseAccessSingleton(db_path)
    debug_print('done', db_access)
    
    search_dbs = [local_db,]
    if configuration.check('search_dbs'):
        try:
            check_paths = literal_eval(configuration.search_dbs)
        except Exception:
            print "*** persistence error: cannot parse search_dbs ***"
        else:
            for path in check_paths:
                if os.path.exists(path):
                    search_dbs.append(path)
                else:
                    print '*** persistence warning: cannot find path "%s"' % path

_configuration_widget = None

def finalize():
    # delete all temporary files/directories used by zip
    global db_access, _configuration_widget

    for fname in repo.get_current_repo().temp_persist_files:
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
    module_remap = {
            # Migrates from pre-0.1.0 to 0.2.0+
            'PersistentFile': [
                (None, '0.1.0', 'PersistentIntermediateFile', {
                    'dst_port_remap': {
                        'compress': None}})],
            'PersistentDirectory': [
                (None, '0.1.0', 'PersistentIntermediateDir', {
                    'dst_port_remap': {
                        'compress': None}})],
            # Migrates from persistence_exp (0.1.0-0.2.0) to 0.2.0+
            'ManagedRef': [
                ('0.1.0', None, 'persistence:PersistentRef', {})],
            'ManagedPath': [
                ('0.1.0', None, 'persistence:PersistentPath', {})],
            'ManagedFile': [
                ('0.1.0', None, 'persistence:PersistentFile', {})],
            'ManagedDir': [
                ('0.1.0', None, 'persistence:PersistentDir', {})],
            'ManagedInputFile': [
                ('0.1.0', None, 'persistence:PersistentInputFile', {})],
            'ManagedOutputFile': [
                ('0.1.0', None, 'persistence:PersistentOutputFile', {})],
            'ManagedIntermediateFile': [
                ('0.1.0', None, 'persistence:PersistentIntermediateFile', {})],
            'ManagedInputDir': [
                ('0.1.0', None, 'persistence:PersistentInputDir', {})],
            'ManagedOutputDir': [
                ('0.1.0', None, 'persistence:PersistentOutputDir', {})],
            'ManagedIntermediateDir': [
                ('0.1.0', None, 'persistence:PersistentIntermediateDir', {})]
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
